# Tests de servicio: reservar_turno (con db mock y credito_cliente mock)
import unittest
from datetime import datetime, timedelta
import app.turnos.services.reservar_turno as modulo_reservar_turno
import app.turnos.services.credito_cliente as modulo_credito_cliente


def _crear_db_mock():
    clases = {
        "clase_1": {
            "_id": "clase_1",
            "cupo": 2,
            "fecha_inicio": (datetime.now() + timedelta(days=1)).isoformat(),
        },
        "clase_sin_cupo": {
            "_id": "clase_sin_cupo",
            "cupo": 0,
            "fecha_inicio": (datetime.now() + timedelta(days=1)).isoformat(),
        },
    }
    reservas = []

    class ColeccionMock:
        def __init__(self, datos):
            if isinstance(datos, dict):
                self._datos = list(datos.values())
            else:
                self._datos = list(datos)

        def find_one(self, filtro):
            for d in self._datos:
                if all(d.get(k) == v for k, v in filtro.items()):
                    return d
            return None

        def insert_one(self, doc):
            doc_id = f"doc_{len(self._datos) + 1}"
            doc_con_id = dict(doc)
            doc_con_id["_id"] = doc_id
            self._datos.append(doc_con_id)
            class Resultado:
                inserted_id = doc_id
            return Resultado()

        def update_one(self, filtro, operacion):
            for d in self._datos:
                if all(d.get(k) == v for k, v in filtro.items()):
                    if "$inc" in operacion:
                        for k, v in operacion["$inc"].items():
                            d[k] = d.get(k, 0) + v
                    if "$set" in operacion:
                        d.update(operacion["$set"])
                    return

    return ColeccionMock(clases), ColeccionMock(reservas)


def _crear_credito_cliente_mock(exito=True):
    class CreditoMock:
        @staticmethod
        def descontar_credito(alumno_id, cantidad, motivo):
            if not exito:
                raise Exception("Error de conexión con Node")
            return {"id": "credito_1", "alumno_id": alumno_id, "cantidad": cantidad}

    return CreditoMock


class ReservarTurnoTests(unittest.TestCase):
    def setUp(self):
        self.db_clases, self.db_reservas = _crear_db_mock()
        modulo_credito_cliente.descontar_credito = _crear_credito_cliente_mock(exito=True).descontar_credito

    def test_reservar_turno_exitoso(self):
        resultado = modulo_reservar_turno.reservar_turno("alumno_1", "clase_1", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        self.assertEqual(resultado["estado"], "confirmada")
        self.assertEqual(resultado["alumno_id"], "alumno_1")
        self.assertEqual(resultado["clase_id"], "clase_1")

    def test_reservar_clase_sin_cupo(self):
        with self.assertRaises(ValueError) as ctx:
            modulo_reservar_turno.reservar_turno("alumno_1", "clase_sin_cupo", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        self.assertIn("cupo", str(ctx.exception).lower())

    def test_reservar_clase_inexistente(self):
        with self.assertRaises(ValueError) as ctx:
            modulo_reservar_turno.reservar_turno("alumno_1", "clase_no_existe", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        self.assertIn("no encontrada", str(ctx.exception).lower())

    def test_reserva_duplicada(self):
        modulo_reservar_turno.reservar_turno("alumno_1", "clase_1", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        with self.assertRaises(ValueError) as ctx:
            modulo_reservar_turno.reservar_turno("alumno_1", "clase_1", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        self.assertIn("ya tiene una reserva", str(ctx.exception).lower())

    def test_error_descontar_credito(self):
        modulo_credito_cliente.descontar_credito = _crear_credito_cliente_mock(exito=False).descontar_credito
        with self.assertRaises(ValueError) as ctx:
            modulo_reservar_turno.reservar_turno("alumno_1", "clase_1", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        self.assertIn("crédito", str(ctx.exception).lower() or "credito" in str(ctx.exception).lower())
