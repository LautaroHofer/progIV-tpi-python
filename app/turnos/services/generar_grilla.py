# Servicio para generar y consultar la grilla de ocurrencias de horarios
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pymongo import UpdateOne
from app.infra.db.mongo import obtener_db_mongo

COLECCION_CLASES = "clases_recurrentes"
COLECCION_EXCEPCIONES = "excepciones_horarios"
COLECCION_OCURRENCIAS = "ocurrencias_horarios"
TAMANO_LOTE = 500


def _calcular_timestamps_utc(fecha_dia, hora_inicio, hora_fin, zona_horaria):
    """Convierte fecha y horario local en la zona de la sucursal a ISO-8601 UTC."""
    try:
        tz = ZoneInfo(zona_horaria)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Zona horaria inválida: {zona_horaria}") from exc

    h_ini, m_ini = (int(x) for x in hora_inicio.split(":"))
    h_fin, m_fin = (int(x) for x in hora_fin.split(":"))
    inicio_utc = datetime.combine(fecha_dia, time(h_ini, m_ini), tzinfo=tz).astimezone(timezone.utc)
    fin_utc = datetime.combine(fecha_dia, time(h_fin, m_fin), tzinfo=tz).astimezone(timezone.utc)
    return (
        inicio_utc.isoformat().replace("+00:00", "Z"),
        fin_utc.isoformat().replace("+00:00", "Z"),
    )


def _indexar_excepciones(col_excepciones, desde_iso, hasta_iso):
    """Indexa feriados y excepciones por clase dentro del rango para consultas en O(1)."""
    feriados, por_clase = {}, {}
    for exc in col_excepciones.find({}):
        fecha = exc.get("fecha", "")
        if not (desde_iso <= fecha < hasta_iso):
            continue
        if exc.get("tipo") == "feriado":
            feriados[(exc.get("sucursal_id"), fecha)] = exc
        elif exc.get("clase_recurrente_id"):
            por_clase[(str(exc["clase_recurrente_id"]), fecha)] = exc
    return feriados, por_clase


def generar_grilla_horarios(fecha_inicio=None, meses=3, sucursal_id=None, db=None):
    """Genera ocurrencias aplicando feriados, suspensiones y suplencias de forma idempotente."""
    if not isinstance(meses, int) or isinstance(meses, bool) or not (1 <= meses <= 12):
        raise ValueError("meses debe ser un entero entre 1 y 12")

    desde = date.fromisoformat(fecha_inicio) if fecha_inicio else date.today()
    hasta = desde + timedelta(days=meses * 30)
    desde_iso, hasta_iso = desde.isoformat(), hasta.isoformat()

    base = db if db is not None else obtener_db_mongo()
    col_ocurrencias = base[COLECCION_OCURRENCIAS]
    if hasattr(col_ocurrencias, "create_index"):
        col_ocurrencias.create_index([("clase_recurrente_id", 1), ("fecha", 1)], unique=True)

    filtro_clases = {"sucursal_id": sucursal_id} if sucursal_id else {}
    clases_por_dia = {d: [] for d in range(7)}
    for clase in base[COLECCION_CLASES].find(filtro_clases):
        clases_por_dia.setdefault(clase["dia_semana"], []).append(clase)

    feriados, exc_por_clase = _indexar_excepciones(base[COLECCION_EXCEPCIONES], desde_iso, hasta_iso)

    operaciones = []
    stats = {"procesadas": 0, "creadas": 0, "actualizadas": 0, "canceladas_por_excepcion": 0, "con_suplencia": 0}
    dia = desde

    while dia < hasta:
        fecha_iso = dia.isoformat()
        for clase in clases_por_dia.get(dia.weekday(), []):
            clase_id = str(clase.get("_id", clase.get("id", "")))
            profesor_id = clase["profesor_id"]
            estado, motivo, es_suplencia = "programada", None, False

            feriado = feriados.get((clase["sucursal_id"], fecha_iso))
            excepcion = exc_por_clase.get((clase_id, fecha_iso))

            if feriado:
                estado, motivo = "cancelada", feriado.get("motivo")
                stats["canceladas_por_excepcion"] += 1
            elif excepcion and excepcion.get("tipo") == "clase_suspendida":
                estado, motivo = "cancelada", excepcion.get("motivo")
                stats["canceladas_por_excepcion"] += 1
            elif excepcion and excepcion.get("tipo") == "cambio_profesor":
                profesor_id = excepcion["profesor_suplente_id"]
                motivo, es_suplencia = excepcion.get("motivo"), True
                stats["con_suplencia"] += 1

            inicio_utc, fin_utc = _calcular_timestamps_utc(
                dia, clase["hora_inicio"], clase["hora_fin"], clase["zona_horaria"]
            )
            operaciones.append(
                UpdateOne(
                    {"clase_recurrente_id": clase_id, "fecha": fecha_iso},
                    {
                        "$set": {
                            "sucursal_id": clase["sucursal_id"],
                            "sala_id": clase["sala_id"],
                            "profesor_id": profesor_id,
                            "es_suplencia": es_suplencia,
                            "actividad": clase["actividad"],
                            "hora_inicio": clase["hora_inicio"],
                            "hora_fin": clase["hora_fin"],
                            "zona_horaria": clase["zona_horaria"],
                            "inicio_utc": inicio_utc,
                            "fin_utc": fin_utc,
                            "cupo_total": clase["cupo"],
                            "estado": estado,
                            "motivo_excepcion": motivo,
                        },
                        "$setOnInsert": {
                            "clase_recurrente_id": clase_id,
                            "fecha": fecha_iso,
                            "cupo_ocupado": 0,
                        },
                    },
                    upsert=True,
                )
            )
            stats["procesadas"] += 1

            if len(operaciones) >= TAMANO_LOTE:
                res = col_ocurrencias.bulk_write(operaciones, ordered=False)
                stats["creadas"] += res.upserted_count
                stats["actualizadas"] += res.matched_count
                operaciones = []
        dia += timedelta(days=1)

    if operaciones:
        res = col_ocurrencias.bulk_write(operaciones, ordered=False)
        stats["creadas"] += res.upserted_count
        stats["actualizadas"] += res.matched_count

    return {"fecha_inicio": desde_iso, "fecha_fin": hasta_iso, "meses": meses, **stats}


def listar_ocurrencias(filtros=None, limite=100, db=None):
    """Lista ocurrencias de la grilla aplicando filtros opcionales."""
    base = db if db is not None else obtener_db_mongo()
    filtros = filtros or {}
    query = {k: filtros[k] for k in ("sucursal_id", "sala_id", "profesor_id", "estado") if filtros.get(k)}

    rango_fecha = {}
    if filtros.get("desde"):
        rango_fecha["$gte"] = filtros["desde"]
    if filtros.get("hasta"):
        rango_fecha["$lte"] = filtros["hasta"]
    if rango_fecha:
        query["fecha"] = rango_fecha

    docs = list(base[COLECCION_OCURRENCIAS].find(query))
    docs.sort(key=lambda d: (d.get("fecha", ""), d.get("hora_inicio", "")))

    tope = min(max(int(limite), 1), 500)
    resultado = []
    for doc in docs[:tope]:
        item = dict(doc)
        if "_id" in item:
            item["id"] = str(item.pop("_id"))
        resultado.append(item)
    return resultado
