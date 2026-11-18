# Enrutador principal de Django
from django.urls import path, include
from django.http import JsonResponse
from app.config.env import config
from app.infra.db.conexion import db

def health(request):
    return JsonResponse({"estado": "ok", "servicio": "api-python-horarios-turnos"})

def ready(request):
    return JsonResponse({
        "listo": db is not None,
        "servicio": "api-python-horarios-turnos",
        "ambiente": config["env"],
        "databaseId": config["firebase"]["database_id"],
    })

urlpatterns = [
    path("health", health),
    path("ready", ready),
    path("salud", health),
    path("api/horarios/", include("app.turnos.routes.rutas_horarios")),
    path("api/turnos/", include("app.turnos.routes.rutas_turnos")),
    path("api/lista-espera/", include("app.turnos.routes.rutas_lista_espera")),
]
