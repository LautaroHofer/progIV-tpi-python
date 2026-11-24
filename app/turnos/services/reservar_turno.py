# Caso de uso: Reservar turno (implementación real)
from datetime import datetime
from app.infra.db.mongo import obtener_db_mongo
from app.turnos.services import credito_cliente

COLECCION_CLASES = "clases_recurrentes"
COLECCION_RESERVAS = "reservas"


def reservar_turno(alumno_id, clase_id, db=None):
    """Reserva un turno para un alumno en una clase.

    Valida que la clase exista y tenga cupo, descuenta un crédito vía
    la API de Node, crea la reserva en MongoDB y decrementa el cupo
    de la clase.
    """
    base = db if db is not None else obtener_db_mongo()

    # Verificar que la clase exista y tenga cupo
    clase = base[COLECCION_CLASES].find_one({"_id": clase_id})
    if not clase:
        raise ValueError("Clase no encontrada")

    if clase.get("cupo", 0) <= 0:
        raise ValueError("No hay cupo disponible para esta clase")

    # Verificar que el alumno no tenga ya una reserva confirmada para esta clase
    reserva_existente = base[COLECCION_RESERVAS].find_one({
        "alumno_id": alumno_id,
        "clase_id": clase_id,
        "estado": "confirmada",
    })
    if reserva_existente:
        raise ValueError("El alumno ya tiene una reserva confirmada para esta clase")

    # Descontar crédito vía Node
    try:
        credito_cliente.descontar_credito(alumno_id, 1, f"Reserva de clase {clase_id}")
    except Exception as e:
        raise ValueError(f"No se pudo descontar crédito: {e}")

    # Crear reserva
    reserva = {
        "alumno_id": alumno_id,
        "clase_id": clase_id,
        "estado": "confirmada",
        "fecha_reserva": datetime.now().isoformat(),
    }
    resultado = base[COLECCION_RESERVAS].insert_one(reserva)

    # Decrementar cupo de la clase
    base[COLECCION_CLASES].update_one(
        {"_id": clase_id},
        {"$inc": {"cupo": -1}},
    )

    return {
        "id": str(resultado.inserted_id),
        **reserva,
    }
