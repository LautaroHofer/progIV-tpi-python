# Servicio de clases recurrentes y validacion de solapamiento de horarios
from app.infra.db.mongo import obtener_db_mongo

COLECCION_CLASES = "clases_recurrentes"


def hay_solapamiento(inicio_a, fin_a, inicio_b, fin_b):
    """Devuelve True si dos rangos horarios (HH:MM) se superponen."""
    return inicio_a < fin_b and inicio_b < fin_a


def buscar_solapamiento(coleccion, dia_semana, hora_inicio, hora_fin, sala_id, profesor_id):
    """Revisa en MongoDB si ya existe una clase que se pise en la misma sala o con el mismo profesor."""
    filtro = {
        "dia_semana": dia_semana,
        "$or": [
            {"sala_id": sala_id},
            {"profesor_id": profesor_id},
        ],
    }

    for clase in coleccion.find(filtro):
        if hay_solapamiento(hora_inicio, hora_fin, clase["hora_inicio"], clase["hora_fin"]):
            if clase["sala_id"] == sala_id:
                return "La sala ya tiene una clase asignada en ese horario"
            return "El profesor ya tiene otra clase asignada en ese horario"

    return None


def crear_clase_recurrente(datos, db=None):
    """Crea una clase recurrente en MongoDB validando que no haya solapamientos."""
    base = db if db is not None else obtener_db_mongo()
    coleccion = base[COLECCION_CLASES]

    motivo_conflicto = buscar_solapamiento(
        coleccion=coleccion,
        dia_semana=datos["dia_semana"],
        hora_inicio=datos["hora_inicio"],
        hora_fin=datos["hora_fin"],
        sala_id=datos["sala_id"],
        profesor_id=datos["profesor_id"],
    )
    if motivo_conflicto:
        raise ValueError(motivo_conflicto)

    documento = {
        "sucursal_id": datos["sucursal_id"],
        "sala_id": datos["sala_id"],
        "profesor_id": datos["profesor_id"],
        "actividad": datos["actividad"],
        "dia_semana": datos["dia_semana"],
        "hora_inicio": datos["hora_inicio"],
        "hora_fin": datos["hora_fin"],
        "zona_horaria": datos["zona_horaria"],
        "cupo": datos["cupo"],
    }

    resultado = coleccion.insert_one(documento)
    documento["id"] = str(resultado.inserted_id)
    documento.pop("_id", None)
    return documento
