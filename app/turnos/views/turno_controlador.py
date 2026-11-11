# Controlador / Vistas de Turnos y Reservas (Django)
import json
from django.http import JsonResponse
from app.turnos.validators import validar_reservar_turno, validar_cancelar_turno


def _parse_body(request):
    """Intenta parsear el cuerpo de la petición como JSON."""
    if not request.body:
        return {}
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return None


def listar_turnos(request):
    return JsonResponse([], safe=False)


def reservar_turno(request):
    data = _parse_body(request)
    if data is None:
        return JsonResponse(
            {"error": "Cuerpo JSON inválido"},
            status=400,
        )

    datos_validos, errores = validar_reservar_turno(data)
    if errores:
        return JsonResponse(
            {"error": "Datos inválidos", "detalles": errores},
            status=400,
        )

    # Entrada válida: aquí se conectará el servicio de reserva una vez
    # definido el repositorio de persistencia.
    return JsonResponse(
        {
            "mensaje": "Turno reservado (placeholder)",
            "datos_validados": datos_validos,
        },
        status=201,
    )


def cancelar_turno(request, id):
    datos_validos, errores = validar_cancelar_turno({"id": id})
    if errores:
        return JsonResponse(
            {"error": "Datos inválidos", "detalles": errores},
            status=400,
        )

    return JsonResponse({"mensaje": f"Turno {id} cancelado (placeholder)"})
