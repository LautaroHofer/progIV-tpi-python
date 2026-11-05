from django.urls import path
from app.infra.http.controladores import lista_espera_controlador

urlpatterns = [
    path("", lista_espera_controlador.unirse_lista_espera),
    path("<int:clase_id>", lista_espera_controlador.listar_espera),
]
