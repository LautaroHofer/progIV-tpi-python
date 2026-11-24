# Controlador / Vistas de Horarios y Grilla (Django)
from datetime import date
import json
import re
from django.http import JsonResponse
from app.turnos.middlewares.auth import requiere_auth, requiere_rol
from app.turnos.services.validar_solapamiento import crear_clase_recurrente
from app.turnos.services.generar_grilla import generar_grilla_horarios, listar_ocurrencias

CAMPOS_GENERAR_GRILLA = {"fecha_inicio", "meses", "sucursal_id"}

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
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    filtros = {
        campo: request.GET.get(campo)
        for campo in ("sucursal_id", "sala_id", "profesor_id", "estado", "desde", "hasta")
        if request.GET.get(campo)
    }

    limite_raw = request.GET.get("limite", "100")
    try:
        limite = int(limite_raw)
        if limite <= 0:
            raise ValueError()
    except ValueError:
        return JsonResponse({"error": "limite debe ser un entero positivo"}, status=400)

    horarios = listar_ocurrencias(filtros=filtros, limite=limite)
    return JsonResponse(horarios, safe=False)


@requiere_auth
@requiere_rol(["admin"])
def generar_grilla(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Cuerpo JSON inválido"}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"error": "El cuerpo debe ser un objeto JSON"}, status=400)

    extras = set(data.keys()) - CAMPOS_GENERAR_GRILLA
    if extras:
        return JsonResponse({"error": f"Campos no permitidos: {', '.join(sorted(extras))}"}, status=400)

    fecha_inicio = data.get("fecha_inicio")
    if fecha_inicio is not None:
        if not isinstance(fecha_inicio, str) or len(fecha_inicio) != 10:
            return JsonResponse({"error": "fecha_inicio debe tener formato YYYY-MM-DD"}, status=400)
        try:
            date.fromisoformat(fecha_inicio)
        except ValueError:
            return JsonResponse({"error": "fecha_inicio inválida (usar YYYY-MM-DD)"}, status=400)

    meses = data.get("meses", 3)
    sucursal_id = data.get("sucursal_id")
    if sucursal_id is not None and (not isinstance(sucursal_id, str) or not sucursal_id.strip()):
        return JsonResponse({"error": "sucursal_id debe ser un texto no vacío"}, status=400)

    try:
        resumen = generar_grilla_horarios(
            fecha_inicio=fecha_inicio,
            meses=meses,
            sucursal_id=sucursal_id,
        )
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(resumen, status=201)


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
