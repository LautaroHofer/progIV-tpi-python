# Tests unitarios de dominio (Horarios y Turnos, sin levantar HTTP ni base de datos)
import unittest

from app.turnos.models.horario import Horario
from app.turnos.services.validar_solapamiento import hay_solapamiento


class HorarioDominioTests(unittest.TestCase):
    def test_crear_horario_con_todos_los_atributos(self):
        h = Horario(
            id=1,
            sala_id=2,
            profesor_id=3,
            actividad="Pilates Reformer",
            fecha_inicio="2026-11-20T09:00:00",
            fecha_fin="2026-11-20T10:00:00",
            cupo=6,
        )
        self.assertEqual(h.id, 1)
        self.assertEqual(h.sala_id, 2)
        self.assertEqual(h.profesor_id, 3)
        self.assertEqual(h.actividad, "Pilates Reformer")
        self.assertEqual(h.fecha_inicio, "2026-11-20T09:00:00")
        self.assertEqual(h.fecha_fin, "2026-11-20T10:00:00")
        self.assertEqual(h.cupo, 6)

    def test_crear_horario_valores_por_defecto_none(self):
        h = Horario()
        self.assertIsNone(h.id)
        self.assertIsNone(h.sala_id)
        self.assertIsNone(h.profesor_id)
        self.assertIsNone(h.actividad)
        self.assertIsNone(h.fecha_inicio)
        self.assertIsNone(h.fecha_fin)
        self.assertIsNone(h.cupo)

    def test_hay_solapamiento_parcial(self):
        self.assertTrue(hay_solapamiento("09:00", "10:00", "09:30", "10:30"))

    def test_hay_solapamiento_contenido_dentro_de_otro(self):
        self.assertTrue(hay_solapamiento("09:00", "11:00", "09:30", "10:00"))

    def test_hay_solapamiento_mismo_horario(self):
        self.assertTrue(hay_solapamiento("09:00", "10:00", "09:00", "10:00"))

    def test_no_hay_solapamiento_horarios_contiguos(self):
        self.assertFalse(hay_solapamiento("09:00", "10:00", "10:00", "11:00"))

    def test_no_hay_solapamiento_horarios_separados(self):
        self.assertFalse(hay_solapamiento("09:00", "10:00", "11:00", "12:00"))
