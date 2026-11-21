# Tests unitarios de dominio (Horarios y Turnos, sin levantar HTTP ni base de datos)
import os
import django
import unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
django.setup()

from app.turnos.models.horario import Horario
from app.turnos.models.reserva import Reserva
from app.turnos.models.lista_espera import ListaEspera


class HorarioModelTests(unittest.TestCase):
    def test_crear_horario(self):
        h = Horario(id=1, sala_id=1, profesor_id=1, actividad="Pilates Reformer", cupo=6)
        self.assertEqual(h.id, 1)
        self.assertEqual(h.sala_id, 1)
        self.assertEqual(h.profesor_id, 1)
        self.assertEqual(h.actividad, "Pilates Reformer")
        self.assertEqual(h.cupo, 6)
        self.assertIsNone(h.fecha_inicio)
        self.assertIsNone(h.fecha_fin)

    def test_crear_horario_con_fechas(self):
        h = Horario(
            id=2,
            sala_id=2,
            profesor_id=3,
            actividad="Yoga",
            fecha_inicio="2026-12-01T09:00:00",
            fecha_fin="2026-12-01T10:00:00",
            cupo=10,
        )
        self.assertEqual(h.cupo, 10)
        self.assertEqual(h.fecha_inicio, "2026-12-01T09:00:00")
        self.assertEqual(h.fecha_fin, "2026-12-01T10:00:00")


class ReservaModelTests(unittest.TestCase):
    def test_crear_reserva(self):
        r = Reserva(id=1, alumno_id=42, clase_id=7)
        self.assertEqual(r.id, 1)
        self.assertEqual(r.alumno_id, 42)
        self.assertEqual(r.clase_id, 7)
        self.assertEqual(r.estado, "confirmada")
        self.assertIsNone(r.fecha_reserva)

    def test_crear_reserva_estado_personalizado(self):
        r = Reserva(id=2, alumno_id=43, clase_id=8, estado="lista_espera")
        self.assertEqual(r.estado, "lista_espera")


class ListaEsperaModelTests(unittest.TestCase):
    def test_crear_lista_espera(self):
        le = ListaEspera(id=1, clase_id=5, alumno_id=10, posicion=3)
        self.assertEqual(le.id, 1)
        self.assertEqual(le.clase_id, 5)
        self.assertEqual(le.alumno_id, 10)
        self.assertEqual(le.posicion, 3)

    def test_crear_lista_espera_sin_posicion(self):
        le = ListaEspera(clase_id=5, alumno_id=10)
        self.assertIsNone(le.id)
        self.assertIsNone(le.posicion)
