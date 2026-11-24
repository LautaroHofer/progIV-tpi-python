# Caso de uso: Cancelar turno (implementación real)
from datetime import datetime, timedelta
from app.infra.db.mongo import obtener_db_mongo
from app.turnos.services import credito_cliente

COLECCION_CLASES = "clases_recurrentes"
COLECCION_RESERVAS = "reservas"

VENTANA_CANCELACION_HORAS = 4


def cancelar_turno(reserva_id, db=None):
    """Cancela una reserva y devuelve el crédito si está dentro de la ventana.

    Es idempotente: cancelar dos veces la misma reserva solo devuelve el
    crédito una vez.
    """
    base = db if db is not None else obtener_db_mongo()

    # Buscar la reserva
    reserva = base[COLECCION_RESERVAS].find_one({"_id": reserva_id})
    if not reserva:
        raise ValueError("Reserva no encontrada")

    # Idempotencia: si ya está cancelada, no devolver otro crédito
    if reserva.get("estado") == "cancelada":
        raise ValueError("La reserva ya está cancelada")

    # Obtener la clase para verificar la ventana de cancelación
    clase = base[COLECCION_CLASES].find_one({"_id": reserva["clase_id"]})
    if not clase:
        raise ValueError("Clase asociada no encontrada")

    # Verificar ventana de cancelación (4 horas antes del inicio)
    fecha_inicio = clase.get("fecha_inicio")
    if fecha_inicio:
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
        ahora = datetime.now()
        if fecha_inicio - ahora <= timedelta(hours=VENTANA_CANCELACION_HORAS):
            raise ValueError("No se puede cancelar dentro de las 4 horas previas a la clase")

    # Devolver crédito vía Node
    try:
        credito_cliente.agregar_credito(reserva["alumno_id"], 1, f"Cancelación de clase {reserva['clase_id']}")
    except Exception as e:
        raise ValueError(f"No se pudo devolver crédito: {e}")

    # Marcar reserva como cancelada
    base[COLECCION_RESERVAS].update_one(
        {"_id": reserva_id},
        {"$set": {"estado": "cancelada", "fecha_cancelacion": datetime.now().isoformat()}},
    )

    # Incrementar cupo de la clase
    base[COLECCION_CLASES].update_one(
        {"_id": reserva["clase_id"]},
        {"$inc": {"cupo": 1}},
    )

    return {
        "id": str(reserva_id),
        "estado": "cancelada",
        "credito_devuelto": True,
    }
