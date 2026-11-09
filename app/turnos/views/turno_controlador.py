# Controlador / Vistas de Turnos y Reservas (Django)
from django.http import JsonResponse

def listar_turnos(request):
    return JsonResponse([], safe=False)

def reservar_turno(request):
    return JsonResponse({"mensaje": "Turno reservado (placeholder)"}, status=201)

def cancelar_turno(request, id):
    return JsonResponse({"mensaje": f"Turno {id} cancelado (placeholder)"})
