from django.urls import path
from app.turnos.views import horario_controlador, excepcion_controlador

urlpatterns = [
    path("", horario_controlador.listar_horarios),
    path("clases-recurrentes", horario_controlador.crear_clase_recurrente_view),
    path("generar-grilla", horario_controlador.generar_grilla),
    path("excepciones", excepcion_controlador.crear_excepcion_view),
]
