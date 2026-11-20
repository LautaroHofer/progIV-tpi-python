# Tests unitarios de dominio (Horarios y Turnos, sin levantar HTTP ni base de datos)
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
django.setup()

from app.turnos.models.horario import Horario
from app.turnos.models.reserva import Reserva
from app.turnos.models.lista_espera import ListaEspera


def test_crear_horario():
    h = Horario(id=1, sala_id=1, profesor_id=1, actividad="Pilates Reformer", cupo=6)
    assert h.id == 1
    assert h.sala_id == 1
    assert h.profesor_id == 1
    assert h.actividad == "Pilates Reformer"
    assert h.cupo == 6
    assert h.fecha_inicio is None
    assert h.fecha_fin is None


def test_crear_horario_con_fechas():
    h = Horario(
        id=2,
        sala_id=2,
        profesor_id=3,
        actividad="Yoga",
        fecha_inicio="2026-12-01T09:00:00",
        fecha_fin="2026-12-01T10:00:00",
        cupo=10,
    )
    assert h.cupo == 10
    assert h.fecha_inicio == "2026-12-01T09:00:00"
    assert h.fecha_fin == "2026-12-01T10:00:00"


def test_crear_reserva():
    r = Reserva(id=1, alumno_id=42, clase_id=7)
    assert r.id == 1
    assert r.alumno_id == 42
    assert r.clase_id == 7
    assert r.estado == "confirmada"
    assert r.fecha_reserva is None


def test_crear_reserva_estado_personalizado():
    r = Reserva(id=2, alumno_id=43, clase_id=8, estado="lista_espera")
    assert r.estado == "lista_espera"


def test_crear_lista_espera():
    le = ListaEspera(id=1, clase_id=5, alumno_id=10, posicion=3)
    assert le.id == 1
    assert le.clase_id == 5
    assert le.alumno_id == 10
    assert le.posicion == 3


def test_crear_lista_espera_sin_posicion():
    le = ListaEspera(clase_id=5, alumno_id=10)
    assert le.id is None
    assert le.posicion is None
