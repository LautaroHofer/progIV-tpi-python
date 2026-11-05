# Tests unitarios de dominio (Horarios y Turnos, sin levantar HTTP ni base de datos)
from app.dominio.entidades.horario import Horario

def test_crear_horario():
    h = Horario(id=1, sala_id=1, profesor_id=1, actividad="Pilates Reformer", cupo=6)
    assert h.cupo == 6
