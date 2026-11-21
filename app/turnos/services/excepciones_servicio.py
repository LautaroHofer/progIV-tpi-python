# Servicio para gestionar excepciones de la grilla (feriados, suspensiones y cambios de profesor)
from datetime import date
from bson import ObjectId
from bson.errors import InvalidId
from app.infra.db.mongo import obtener_db_mongo

COLECCION_CLASES = "clases_recurrentes"
COLECCION_EXCEPCIONES = "excepciones_horarios"


def _hay_solapamiento(inicio_a, fin_a, inicio_b, fin_b):
    return inicio_a < fin_b and inicio_b < fin_a


def _buscar_clase(coleccion, clase_id):
    try:
        doc = coleccion.find_one({"_id": ObjectId(clase_id)})
        if doc:
            return doc
    except (InvalidId, TypeError):
        pass
    return coleccion.find_one({"_id": clase_id})


def registrar_excepcion(datos, db=None):
    """Guarda un feriado, suspension de clase o cambio de profesor validando conflictos."""
    base = db if db is not None else obtener_db_mongo()
    col_clases = base[COLECCION_CLASES]
    col_excepciones = base[COLECCION_EXCEPCIONES]

    tipo = datos["tipo"]
    fecha = datos["fecha"]

    if tipo == "feriado":
        ya_existe = col_excepciones.find_one({
            "tipo": "feriado",
            "sucursal_id": datos["sucursal_id"],
            "fecha": fecha,
        })
        if ya_existe:
            raise ValueError("Ya existe un feriado registrado para esa sucursal y fecha")
    else:
        clase = _buscar_clase(col_clases, datos["clase_recurrente_id"])
        if not clase:
            raise LookupError("La clase recurrente indicada no existe")

        ya_existe = col_excepciones.find_one({
            "clase_recurrente_id": datos["clase_recurrente_id"],
            "fecha": fecha,
        })
        if ya_existe:
            raise ValueError("Ya existe una excepcion registrada para esa clase en esa fecha")

        if tipo == "cambio_profesor":
            suplente = datos["profesor_suplente_id"]
            if suplente == clase.get("profesor_id"):
                raise ValueError("El profesor suplente debe ser distinto al profesor titular")

            dia_semana = date.fromisoformat(fecha).weekday()
            for otra in col_clases.find({"dia_semana": dia_semana, "profesor_id": suplente}):
                if _hay_solapamiento(clase["hora_inicio"], clase["hora_fin"], otra["hora_inicio"], otra["hora_fin"]):
                    raise ValueError("El profesor suplente ya tiene otra clase en ese horario")

    doc = dict(datos)
    resultado = col_excepciones.insert_one(doc)
    doc["id"] = str(resultado.inserted_id)
    doc.pop("_id", None)
    return doc
