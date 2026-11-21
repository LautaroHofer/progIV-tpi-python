# Controlador / Vistas de Horarios y Grilla (Django)
import json
import re
from django.http import JsonResponse
from app.turnos.middlewares.auth import requiere_auth, requiere_rol
from app.turnos.services.validar_solapamiento import crear_clase_recurrente

CAMPOS_PERMITIDOS = {
    "sucursal_id",
    "sala_id",
    "profesor_id",
    "actividad",
    "dia_semana",
    "hora_inicio",
    "hora_fin",
    "zona_horaria",
    "cupo",
}
PATRON_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _validar_clase_recurrente(data):
    """Valida los campos del body para crear una clase recurrente."""
    if not isinstance(data, dict):
        return "El cuerpo debe ser un objeto JSON"

    extras = set(data.keys()) - CAMPOS_PERMITIDOS
    if extras:
        return f"Campos no permitidos: {', '.join(sorted(extras))}"

    faltantes = CAMPOS_PERMITIDOS - set(data.keys())
    if faltantes:
        return f"Faltan campos obligatorios: {', '.join(sorted(faltantes))}"

    dia = data["dia_semana"]
    if not isinstance(dia, int) or isinstance(dia, bool) or not (0 <= dia <= 6):
        return "dia_semana debe ser un entero entre 0 (lunes) y 6 (domingo)"

    cupo = data["cupo"]
    if not isinstance(cupo, int) or isinstance(cupo, bool) or cupo <= 0:
        return "cupo debe ser un entero positivo"

    inicio = data["hora_inicio"]
    fin = data["hora_fin"]
    if not isinstance(inicio, str) or not PATRON_HORA.match(inicio):
        return "hora_inicio debe tener formato HH:MM"
    if not isinstance(fin, str) or not PATRON_HORA.match(fin):
        return "hora_fin debe tener formato HH:MM"
    if inicio >= fin:
        return "hora_inicio debe ser menor a hora_fin"

    zona = data["zona_horaria"]
    if not isinstance(zona, str) or not zona.strip():
        return "zona_horaria es obligatoria (ej. America/Argentina/Buenos_Aires)"

    return None


def listar_horarios(request):
    return JsonResponse([], safe=False)


def generar_grilla(request):
    return JsonResponse({"mensaje": "Generación de grilla (placeholder)"}, status=201)


@requiere_auth
@requiere_rol(["admin"])
def crear_clase_recurrente_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Cuerpo JSON inválido"}, status=400)

    error = _validar_clase_recurrente(data)
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        clase = crear_clase_recurrente(data)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=409)

    return JsonResponse(clase, status=201)
