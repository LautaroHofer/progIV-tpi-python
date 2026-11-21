# Tests de excepciones de grilla (feriados, suspensiones y cambio de profesor)
import json, os, unittest
from unittest.mock import patch
import django, jwt
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
django.setup()

from app.turnos.views.excepcion_controlador import crear_excepcion_view  # noqa: E402

SECRET = "clave-secreta-de-prueba-con-al-menos-32-bytes"


class _FakeCol:
    def __init__(self, docs=None):
        self.docs = list(docs or [])

    def find(self, filtro):
        return [d for d in self.docs if all(d.get(k) == v for k, v in filtro.items())]

    def find_one(self, filtro):
        encontrados = self.find(filtro)
        return encontrados[0] if encontrados else None

    def insert_one(self, doc):
        nuevo = {**doc, "_id": f"exc_{len(self.docs) + 1}"}
        self.docs.append(nuevo)
        return type("Res", (), {"inserted_id": nuevo["_id"]})()


class ExcepcionesHorariosTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        clases = [
            {"_id": "clase_1", "dia_semana": 0, "hora_inicio": "08:00", "hora_fin": "09:00", "profesor_id": "prof_1"},
            {"_id": "clase_2", "dia_semana": 0, "hora_inicio": "08:30", "hora_fin": "09:30", "profesor_id": "prof_ocupado"},
        ]
        self.fake_db = {"clases_recurrentes": _FakeCol(clases), "excepciones_horarios": _FakeCol()}
        self.token_admin = jwt.encode({"sub": "adm_1", "rol": "admin"}, SECRET, algorithm="HS256")
        self.p_env = patch.dict(os.environ, {"JWT_SECRET": SECRET})
        self.p_db = patch("app.turnos.services.excepciones_servicio.obtener_db_mongo", return_value=self.fake_db)
        self.p_env.start()
        self.p_db.start()

    def tearDown(self):
        self.p_db.stop()
        self.p_env.stop()

    def _post(self, body, token=None):
        req = self.factory.post("/api/horarios/excepciones", data=json.dumps(body),
                                content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token or self.token_admin}")
        return crear_excepcion_view(req)

    def test_feriado_y_suspension(self):
        feriado = {"tipo": "feriado", "fecha": "2026-12-08", "sucursal_id": "suc_1", "motivo": "Feriado nacional"}
        self.assertEqual(self._post(feriado).status_code, 201)
        self.assertEqual(self._post(feriado).status_code, 409)
        self.assertEqual(self._post({"tipo": "clase_suspendida", "fecha": "2026-12-07", "clase_recurrente_id": "clase_1", "motivo": "Mantenimiento"}).status_code, 201)
        self.assertEqual(self._post({"tipo": "clase_suspendida", "fecha": "2026-12-07", "clase_recurrente_id": "inexistente", "motivo": "X"}).status_code, 404)

    def test_cambio_profesor_y_seguridad(self):
        # 2026-12-07 y 2026-12-14 son lunes (dia_semana = 0)
        ok = {"tipo": "cambio_profesor", "fecha": "2026-12-07", "clase_recurrente_id": "clase_1", "profesor_suplente_id": "prof_libre", "motivo": "Licencia"}
        solapado = {**ok, "fecha": "2026-12-14", "profesor_suplente_id": "prof_ocupado"}
        self.assertEqual(self._post(ok).status_code, 201)
        self.assertEqual(self._post(solapado).status_code, 409)
        token_alu = jwt.encode({"sub": "alu_1", "rol": "alumno"}, SECRET, algorithm="HS256")
        self.assertEqual(self._post(ok, token=token_alu).status_code, 403)
        self.assertEqual(self._post({**ok, "extra": "invalido"}).status_code, 400)
