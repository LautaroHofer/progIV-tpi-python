from django.urls import path
from app.infra.http.controladores import horario_controlador

urlpatterns = [
    path("", horario_controlador.listar_horarios),
    path("generar-grilla", horario_controlador.generar_grilla),
]
