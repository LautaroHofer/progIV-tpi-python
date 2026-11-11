# Validador de entrada para cancelar turno
# Valida que el identificador de reserva provisto sea un entero positivo.


def validar_cancelar_turno(data):
    """Valida los datos de entrada para cancelar una reserva.

    Retorna una tupla (datos_limpios, errores).
    Si errores está vacía, los datos son válidos.
    """
    errores = []

    reserva_id = data.get("id")

    if reserva_id is None:
        errores.append("id es obligatorio")
    elif not isinstance(reserva_id, int) or isinstance(reserva_id, bool) or reserva_id <= 0:
        errores.append("id debe ser un entero positivo")

    return {"id": reserva_id}, errores
