# Controlador / Vistas de Lista de Espera (Django)
from django.http import JsonResponse

def listar_espera(request, clase_id):
    return JsonResponse([], safe=False)

def unirse_lista_espera(request):
    return JsonResponse({"mensaje": "Agregado a lista de espera (placeholder)"}, status=201)
