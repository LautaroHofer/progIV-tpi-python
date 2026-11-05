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
    path("api/horarios/", include("app.infra.http.rutas.rutas_horarios")),
    path("api/turnos/", include("app.infra.http.rutas.rutas_turnos")),
    path("api/lista-espera/", include("app.infra.http.rutas.rutas_lista_espera")),
]
