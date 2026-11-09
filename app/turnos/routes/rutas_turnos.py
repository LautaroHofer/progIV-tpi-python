from django.urls import path
from app.turnos.views import turno_controlador

urlpatterns = [
    path("", turno_controlador.listar_turnos),
    path("reservar", turno_controlador.reservar_turno),
    path("<int:id>/cancelar", turno_controlador.cancelar_turno),
]
