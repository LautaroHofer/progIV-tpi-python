# Validador de entrada para reservar turno
# No toca base de datos: solo valida que el cuerpo de la petición tenga los
# campos obligatorios con los tipos correctos antes de llegar al servicio.


def validar_reservar_turno(data):
    """Valida los datos de entrada para crear una reserva.

    Retorna una tupla (datos_limpios, errores).
    Si errores está vacía, los datos son válidos.
    """
    errores = []

    alumno_id = data.get("alumno_id")
    clase_id = data.get("clase_id")

    if alumno_id is None:
        errores.append("alumno_id es obligatorio")
    elif not isinstance(alumno_id, int) or isinstance(alumno_id, bool) or alumno_id <= 0:
        errores.append("alumno_id debe ser un entero positivo")

    if clase_id is None:
        errores.append("clase_id es obligatorio")
    elif not isinstance(clase_id, int) or isinstance(clase_id, bool) or clase_id <= 0:
        errores.append("clase_id debe ser un entero positivo")

    return {"alumno_id": alumno_id, "clase_id": clase_id}, errores
