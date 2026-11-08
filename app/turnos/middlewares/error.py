# Manejador global de errores HTTP en Django
from django.http import JsonResponse

def manejador_errores(request, exception=None):
    return JsonResponse(
        {"error": "Error interno del servidor"},
        status=500
    )
