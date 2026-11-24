# Controlador / Vistas de Turnos y Reservas (Django)
import json
from django.http import JsonResponse
from app.turnos.middlewares.auth import requiere_auth, requiere_rol
from app.turnos.validators import validar_reservar_turno, validar_cancelar_turno
from app.turnos.services import reservar_turno, cancelar_turno


def _parse_body(request):
    """Intenta parsear el cuerpo de la petición como JSON."""
    if not request.body:
        return {}
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return None


@requiere_auth
def listar_turnos(request):
    return JsonResponse([], safe=False)


@requiere_auth
@requiere_rol(["alumno", "admin"])
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

    # El alumno_id viene del token JWT, no del cuerpo de la petición
    alumno_id = request.usuario.get("sub")
    clase_id = datos_validos.get("clase_id")

    try:
        reserva = reservar_turno(alumno_id, clase_id)
        return JsonResponse(reserva, status=201)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)


@requiere_auth
@requiere_rol(["alumno", "admin"])
def cancelar_turno(request, id):
    try:
        resultado = cancelar_turno(id)
        return JsonResponse(resultado)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
