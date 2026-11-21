# Tests de clases recurrentes y validacion de solapamientos
import json, os, unittest
from unittest.mock import patch
import django, jwt
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
django.setup()

from app.turnos.services.validar_solapamiento import hay_solapamiento  # noqa: E402
from app.turnos.views.horario_controlador import crear_clase_recurrente_view  # noqa: E402

SECRET = "clave-secreta-de-prueba-con-al-menos-32-bytes"


class _FakeColeccion:
    def __init__(self):
        self.docs = []

    def find(self, filtro):
        dia = filtro["dia_semana"]
        sala, prof = filtro["$or"][0]["sala_id"], filtro["$or"][1]["profesor_id"]
        return [d for d in self.docs if d["dia_semana"] == dia and (d["sala_id"] == sala or d["profesor_id"] == prof)]

    def insert_one(self, doc):
        nuevo = {**doc, "_id": f"clase_{len(self.docs) + 1}"}
        self.docs.append(nuevo)
        return type("Res", (), {"inserted_id": nuevo["_id"]})()


def _body(**extra):
    return {
        "sucursal_id": "suc_1", "sala_id": "sala_1", "profesor_id": "prof_1",
        "actividad": "Pilates", "dia_semana": 1, "hora_inicio": "08:00",
        "hora_fin": "09:00", "zona_horaria": "America/Argentina/Buenos_Aires", "cupo": 6,
        **extra,
    }


class ClasesRecurrentesTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.fake_db = {"clases_recurrentes": _FakeColeccion()}
        self.token_admin = jwt.encode({"sub": "adm_1", "rol": "admin"}, SECRET, algorithm="HS256")
        self.p_env = patch.dict(os.environ, {"JWT_SECRET": SECRET})
        self.p_db = patch("app.turnos.services.validar_solapamiento.obtener_db_mongo", return_value=self.fake_db)
        self.p_env.start()
        self.p_db.start()

    def tearDown(self):
        self.p_db.stop()
        self.p_env.stop()

    def _post(self, body, token=None):
        req = self.factory.post("/api/horarios/clases-recurrentes", data=json.dumps(body),
                                content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token or self.token_admin}")
        return crear_clase_recurrente_view(req)

    def test_solapamiento_y_creacion(self):
        self.assertTrue(hay_solapamiento("08:00", "09:00", "08:30", "09:30"))
        self.assertFalse(hay_solapamiento("08:00", "09:00", "09:00", "10:00"))
        self.assertEqual(self._post(_body()).status_code, 201)
        # Solapamiento de profesor (misma hora, distinta sala) -> 409
        self.assertEqual(self._post(_body(sala_id="sala_2", hora_inicio="08:30", hora_fin="09:30")).status_code, 409)
        # Solapamiento de sala (misma hora, distinto profesor) -> 409
        self.assertEqual(self._post(_body(profesor_id="prof_2", hora_inicio="08:30", hora_fin="09:30")).status_code, 409)

    def test_seguridad_rol_y_campos_extra(self):
        token_alu = jwt.encode({"sub": "alu_1", "rol": "alumno"}, SECRET, algorithm="HS256")
        self.assertEqual(self._post(_body(), token=token_alu).status_code, 403)
        self.assertEqual(self._post(_body(extra="no_valido")).status_code, 400)
