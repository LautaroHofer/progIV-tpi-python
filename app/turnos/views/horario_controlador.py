# Controlador / Vistas de Horarios y Grilla (Django)
from django.http import JsonResponse

def listar_horarios(request):
    return JsonResponse([], safe=False)

def generar_grilla(request):
    return JsonResponse({"mensaje": "Generación de grilla (placeholder)"}, status=201)
