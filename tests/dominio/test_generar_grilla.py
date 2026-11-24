# Tests de generacion de grilla, excepciones, idempotencia y cambio horario (DST)
import json, os, unittest
from unittest.mock import patch
import django, jwt
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
django.setup()

from app.turnos.views.horario_controlador import generar_grilla, listar_horarios  # noqa: E402

SECRET = "clave-secreta-de-prueba-con-al-menos-32-bytes"


class _FakeCol:
    def __init__(self, docs=None):
        self.docs = list(docs or [])

    def create_index(self, *args, **kwargs):
        return "idx_ok"

    def find(self, filtro):
        res = []
        for doc in self.docs:
            ok = True
            for k, v in filtro.items():
                if isinstance(v, dict):
                    val = doc.get(k, "")
                    if "$gte" in v and val < v["$gte"]:
                        ok = False
                    if "$lte" in v and val > v["$lte"]:
                        ok = False
                elif doc.get(k) != v:
                    ok = False
            if ok:
                res.append(doc)
        return res

    def bulk_write(self, operaciones, ordered=False):
        upserted, matched = 0, 0
        for op in operaciones:
            filtro = op._filter
            existente = next(
                (d for d in self.docs if all(d.get(k) == v for k, v in filtro.items())),
                None,
            )
            if existente:
                existente.update(op._doc.get("$set", {}))
                matched += 1
            else:
                nuevo = {"_id": f"ocu_{len(self.docs) + 1}"}
                nuevo.update(op._doc.get("$setOnInsert", {}))
                nuevo.update(op._doc.get("$set", {}))
                self.docs.append(nuevo)
                upserted += 1
        return type("BulkRes", (), {"upserted_count": upserted, "matched_count": matched})()


class GenerarGrillaTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.token_admin = jwt.encode({"sub": "adm_1", "rol": "admin"}, SECRET, algorithm="HS256")
        self.p_env = patch.dict(os.environ, {"JWT_SECRET": SECRET})
        self.p_env.start()

    def tearDown(self):
        self.p_env.stop()

    def _preparar_db(self, clases, excepciones=None):
        fake_db = {
            "clases_recurrentes": _FakeCol(clases),
            "excepciones_horarios": _FakeCol(excepciones or []),
            "ocurrencias_horarios": _FakeCol(),
        }
        patcher = patch("app.turnos.services.generar_grilla.obtener_db_mongo", return_value=fake_db)
        patcher.start()
        self.addCleanup(patcher.stop)
        return fake_db

    def _post_grilla(self, body, token=None):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
        req = self.factory.post(
            "/api/horarios/generar-grilla",
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )
        return generar_grilla(req)

    def test_generacion_con_excepciones_y_listado(self):
        # Lunes de diciembre 2026: 07, 14, 21, 28
        clases = [{
            "_id": "clase_1", "sucursal_id": "suc_1", "sala_id": "sala_1",
            "profesor_id": "prof_1", "actividad": "Pilates", "dia_semana": 0,
            "hora_inicio": "08:00", "hora_fin": "09:00",
            "zona_horaria": "America/Argentina/Buenos_Aires", "cupo": 6,
        }]
        excepciones = [
            {"tipo": "feriado", "fecha": "2026-12-07", "sucursal_id": "suc_1", "motivo": "Feriado"},
            {"tipo": "clase_suspendida", "fecha": "2026-12-14", "clase_recurrente_id": "clase_1", "motivo": "Mantenimiento"},
            {"tipo": "cambio_profesor", "fecha": "2026-12-21", "clase_recurrente_id": "clase_1", "profesor_suplente_id": "prof_sup", "motivo": "Licencia"},
        ]
        self._preparar_db(clases, excepciones)

        res = self._post_grilla({"fecha_inicio": "2026-12-01", "meses": 1}, token=self.token_admin)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.content)
        self.assertEqual(data["creadas"], 4)
        self.assertEqual(data["canceladas_por_excepcion"], 2)
        self.assertEqual(data["con_suplencia"], 1)

        res_list = listar_horarios(self.factory.get("/api/horarios/?sucursal_id=suc_1&estado=programada"))
        self.assertEqual(res_list.status_code, 200)
        programadas = json.loads(res_list.content)
        self.assertEqual(len(programadas), 2)
        suplencia = next(o for o in programadas if o["fecha"] == "2026-12-21")
        self.assertEqual(suplencia["profesor_id"], "prof_sup")
        self.assertTrue(suplencia["es_suplencia"])

    def test_reejecucion_idempotente_sin_borrar_reservas(self):
        clases = [{
            "_id": "clase_1", "sucursal_id": "suc_1", "sala_id": "sala_1",
            "profesor_id": "prof_1", "actividad": "Yoga", "dia_semana": 0,
            "hora_inicio": "10:00", "hora_fin": "11:00",
            "zona_horaria": "America/Argentina/Buenos_Aires", "cupo": 8,
        }]
        fake_db = self._preparar_db(clases)

        res1 = self._post_grilla({"fecha_inicio": "2026-12-01", "meses": 1}, token=self.token_admin)
        self.assertEqual(res1.status_code, 201)
        total_inicial = len(fake_db["ocurrencias_horarios"].docs)
        fake_db["ocurrencias_horarios"].docs[0]["cupo_ocupado"] = 4

        res2 = self._post_grilla({"fecha_inicio": "2026-12-01", "meses": 1}, token=self.token_admin)
        self.assertEqual(res2.status_code, 201)
        data2 = json.loads(res2.content)
        self.assertEqual(data2["creadas"], 0)
        self.assertEqual(data2["actualizadas"], total_inicial)
        self.assertEqual(len(fake_db["ocurrencias_horarios"].docs), total_inicial)
        self.assertEqual(fake_db["ocurrencias_horarios"].docs[0]["cupo_ocupado"], 4)

    def test_cambio_horario_dst_zona_horaria(self):
        # America/New_York cambia a horario de verano (DST) el domingo 2026-03-08 (-05:00 -> -04:00)
        clases = [{
            "_id": "clase_ny", "sucursal_id": "suc_ny", "sala_id": "sala_ny",
            "profesor_id": "prof_1", "actividad": "Pilates", "dia_semana": 0,
            "hora_inicio": "09:00", "hora_fin": "10:00",
            "zona_horaria": "America/New_York", "cupo": 6,
        }]
        fake_db = self._preparar_db(clases)

        res = self._post_grilla({"fecha_inicio": "2026-03-01", "meses": 1}, token=self.token_admin)
        self.assertEqual(res.status_code, 201)
        por_fecha = {d["fecha"]: d for d in fake_db["ocurrencias_horarios"].docs}
        self.assertEqual(por_fecha["2026-03-02"]["inicio_utc"], "2026-03-02T14:00:00Z")
        self.assertEqual(por_fecha["2026-03-09"]["inicio_utc"], "2026-03-09T13:00:00Z")

    def test_seguridad_y_validaciones_endpoint(self):
        self._preparar_db([])
        token_alu = jwt.encode({"sub": "alu_1", "rol": "alumno"}, SECRET, algorithm="HS256")
        self.assertEqual(self._post_grilla({}, token=None).status_code, 401)
        self.assertEqual(self._post_grilla({}, token=token_alu).status_code, 403)
        self.assertEqual(self._post_grilla({"extra": 1}, token=self.token_admin).status_code, 400)
        self.assertEqual(self._post_grilla({"meses": 0}, token=self.token_admin).status_code, 400)
        self.assertEqual(self._post_grilla({"fecha_inicio": "invalida"}, token=self.token_admin).status_code, 400)
        self.assertEqual(listar_horarios(self.factory.get("/api/horarios/?limite=abc")).status_code, 400)
