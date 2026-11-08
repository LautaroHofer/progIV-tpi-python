from django.urls import path
from app.turnos.views import lista_espera_controlador

urlpatterns = [
    path("", lista_espera_controlador.unirse_lista_espera),
    path("<int:clase_id>", lista_espera_controlador.listar_espera),
]
