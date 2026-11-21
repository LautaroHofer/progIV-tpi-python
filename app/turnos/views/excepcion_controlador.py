# Controlador de excepciones de la grilla (feriados, suspensiones y cambios de profesor)
from datetime import date
import json
from django.http import JsonResponse
from app.turnos.middlewares.auth import requiere_auth, requiere_rol
from app.turnos.services.excepciones_servicio import registrar_excepcion

CAMPOS_POR_TIPO = {
    "feriado": {"tipo", "fecha", "sucursal_id", "motivo"},
    "clase_suspendida": {"tipo", "fecha", "clase_recurrente_id", "motivo"},
    "cambio_profesor": {"tipo", "fecha", "clase_recurrente_id", "profesor_suplente_id", "motivo"},
}


def _validar_excepcion(data):
    """Valida los campos del body segun el tipo de excepcion."""
    if not isinstance(data, dict):
        return "El cuerpo debe ser un objeto JSON"

    tipo = data.get("tipo")
    if tipo not in CAMPOS_POR_TIPO:
        return "tipo debe ser: feriado, clase_suspendida o cambio_profesor"

    permitidos = CAMPOS_POR_TIPO[tipo]
    extras = set(data.keys()) - permitidos
    if extras:
        return f"Campos no permitidos: {', '.join(sorted(extras))}"

    faltantes = permitidos - set(data.keys())
    if faltantes:
        return f"Faltan campos obligatorios: {', '.join(sorted(faltantes))}"

    fecha = data["fecha"]
    if not isinstance(fecha, str) or len(fecha) != 10:
        return "fecha debe tener formato YYYY-MM-DD"
    try:
        date.fromisoformat(fecha)
    except ValueError:
        return "fecha invalida (usar formato YYYY-MM-DD)"

    for campo in permitidos - {"tipo", "fecha"}:
        if not isinstance(data[campo], str) or not data[campo].strip():
            return f"{campo} debe ser un texto no vacio"

    return None


@requiere_auth
@requiere_rol(["admin", "recepcionista"])
def crear_excepcion_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Cuerpo JSON inválido"}, status=400)

    error = _validar_excepcion(data)
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        excepcion = registrar_excepcion(data)
    except LookupError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=409)

    return JsonResponse(excepcion, status=201)
