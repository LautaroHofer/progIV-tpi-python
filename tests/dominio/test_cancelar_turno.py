# Tests de servicio: cancelar_turno (con db mock y credito_cliente mock)
import unittest
from datetime import datetime, timedelta
import app.turnos.services.cancelar_turno as modulo_cancelar_turno
import app.turnos.services.credito_cliente as modulo_credito_cliente


def _crear_db_mock():
    clases = {
        "clase_1": {
            "_id": "clase_1",
            "cupo": 2,
            "fecha_inicio": (datetime.now() + timedelta(days=2)).isoformat(),
        },
    }
    reservas = {
        "reserva_1": {
            "_id": "reserva_1",
            "alumno_id": "alumno_1",
            "clase_id": "clase_1",
            "estado": "confirmada",
            "fecha_reserva": datetime.now().isoformat(),
        },
        "reserva_cancelada": {
            "_id": "reserva_cancelada",
            "alumno_id": "alumno_1",
            "clase_id": "clase_1",
            "estado": "cancelada",
            "fecha_reserva": datetime.now().isoformat(),
        },
    }

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

        def update_one(self, filtro, operacion):
            for d in self._datos:
                if all(d.get(k) == v for k, v in filtro.items()):
                    if "$set" in operacion:
                        d.update(operacion["$set"])
                    if "$inc" in operacion:
                        for k, v in operacion["$inc"].items():
                            d[k] = d.get(k, 0) + v
                    return

    return ColeccionMock(clases), ColeccionMock(reservas)


def _crear_credito_cliente_mock(exito=True):
    class CreditoMock:
        @staticmethod
        def agregar_credito(alumno_id, cantidad, motivo):
            if not exito:
                raise Exception("Error de conexión con Node")
            return {"id": "credito_1", "alumno_id": alumno_id, "cantidad": cantidad}

    return CreditoMock


class CancelarTurnoTests(unittest.TestCase):
    def setUp(self):
        self.db_clases, self.db_reservas = _crear_db_mock()
        modulo_credito_cliente.agregar_credito = _crear_credito_cliente_mock(exito=True).agregar_credito

    def test_cancelar_turno_exitoso(self):
        resultado = modulo_cancelar_turno.cancelar_turno("reserva_1", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        self.assertEqual(resultado["estado"], "cancelada")
        self.assertTrue(resultado["credito_devuelto"])

    def test_cancelar_turno_ya_cancelada(self):
        with self.assertRaises(ValueError) as ctx:
            modulo_cancelar_turno.cancelar_turno("reserva_cancelada", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        self.assertIn("ya está cancelada", str(ctx.exception).lower())

    def test_cancelar_reserva_inexistente(self):
        with self.assertRaises(ValueError) as ctx:
            modulo_cancelar_turno.cancelar_turno("reserva_no_existe", db={"clases_recurrentes": self.db_clases, "reservas": self.db_reservas})
        self.assertIn("no encontrada", str(ctx.exception).lower())

    def test_cancelar_fuera_de_ventana(self):
        db_clases, db_reservas = _crear_db_mock()
        # Modificar clase_1 para que esté en 1 hora (dentro de ventana de 4h)
        db_clases._datos[0]["fecha_inicio"] = (datetime.now() + timedelta(hours=1)).isoformat()
        modulo_credito_cliente.agregar_credito = _crear_credito_cliente_mock(exito=True).agregar_credito

        try:
            modulo_cancelar_turno.cancelar_turno("reserva_1", db={"clases_recurrentes": db_clases, "reservas": db_reservas})
            assert False, "Debería haber lanzado ValueError"
        except ValueError as e:
            self.assertIn("4 horas", str(e))

    def test_error_devolver_credito(self):
        db_clases, db_reservas = _crear_db_mock()
        modulo_credito_cliente.agregar_credito = _crear_credito_cliente_mock(exito=False).agregar_credito

        try:
            modulo_cancelar_turno.cancelar_turno("reserva_1", db={"clases_recurrentes": db_clases, "reservas": db_reservas})
            assert False, "Debería haber lanzado ValueError"
        except ValueError as e:
            self.assertIn("crédito", str(e).lower() or "credito" in str(e).lower())
