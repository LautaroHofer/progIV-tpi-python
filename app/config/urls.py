# Enrutador principal de Django
from django.urls import path, include
from django.http import JsonResponse

def health(request):
    return JsonResponse({"estado": "ok", "servicio": "api-python-horarios-turnos"})

def ready(request):
    return JsonResponse({"listo": True, "servicio": "api-python-horarios-turnos"})

urlpatterns = [
    path("health", health),
    path("ready", ready),
    path("salud", health),
    path("api/horarios/", include("app.turnos.routes.rutas_horarios")),
    path("api/turnos/", include("app.turnos.routes.rutas_turnos")),
    path("api/lista-espera/", include("app.turnos.routes.rutas_lista_espera")),
]
