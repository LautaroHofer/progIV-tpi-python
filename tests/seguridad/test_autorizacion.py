# Tests de seguridad para autenticación y autorización JWT
from datetime import datetime, timedelta, timezone
import json
import os
import unittest
from unittest.mock import patch

import django
from django.http import JsonResponse
from django.test import RequestFactory
import jwt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
django.setup()

from app.turnos.middlewares.auth import (  # noqa: E402
    requiere_auth,
    requiere_permiso,
    requiere_rol,
)

TEST_SECRET = "clave-secreta-de-prueba-con-al-menos-32-bytes"


@requiere_auth
def _vista_solo_auth(request):
    return JsonResponse({"sub": request.usuario["sub"], "rol": request.usuario.get("rol")})


@requiere_auth
@requiere_rol(["alumno", "admin"])
def _vista_con_rol(request):
    return JsonResponse({"ok": True, "sub": request.usuario["sub"]})


@requiere_auth
@requiere_permiso("reservas:crear")
def _vista_con_permiso(request):
    return JsonResponse({"ok": True})


def _crear_token(payload, secret=TEST_SECRET, algorithm="HS256"):
    return jwt.encode(payload, secret, algorithm=algorithm)


def _body_json(response):
    return json.loads(response.content.decode("utf-8"))


class AutorizacionJWTTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.env_patcher = patch.dict(os.environ, {"JWT_SECRET": TEST_SECRET})
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_rechaza_sin_header_authorization(self):
        request = self.factory.get("/api/turnos/")
        response = _vista_solo_auth(request)
        self.assertEqual(response.status_code, 401)

    def test_rechaza_header_sin_prefijo_bearer(self):
        token = _crear_token({"sub": "u1", "rol": "alumno"})
        request = self.factory.get("/api/turnos/", HTTP_AUTHORIZATION=token)
        response = _vista_solo_auth(request)
        self.assertEqual(response.status_code, 401)

    def test_rechaza_token_firmado_con_otro_secreto(self):
        token = _crear_token(
            {"sub": "u1", "rol": "alumno"},
            secret="otro-secreto-completamente-distinto-1234",
        )
        request = self.factory.get("/api/turnos/", HTTP_AUTHORIZATION=f"Bearer {token}")
        response = _vista_solo_auth(request)
        self.assertEqual(response.status_code, 401)

    def test_rechaza_token_expirado(self):
        exp_pasado = datetime.now(timezone.utc) - timedelta(minutes=5)
        token = _crear_token({"sub": "u1", "rol": "alumno", "exp": exp_pasado})
        request = self.factory.get("/api/turnos/", HTTP_AUTHORIZATION=f"Bearer {token}")
        response = _vista_solo_auth(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(_body_json(response)["error"], "Token expirado")

    def test_rechaza_algoritmo_none(self):
        token_sin_firma = jwt.encode({"sub": "u1", "rol": "admin"}, None, algorithm="none")
        request = self.factory.get(
            "/api/turnos/", HTTP_AUTHORIZATION=f"Bearer {token_sin_firma}"
        )
        response = _vista_solo_auth(request)
        self.assertEqual(response.status_code, 401)

    def test_devuelve_500_si_falta_jwt_secret_en_servidor(self):
        token = _crear_token({"sub": "u1", "rol": "alumno"})
        request = self.factory.get("/api/turnos/", HTTP_AUTHORIZATION=f"Bearer {token}")
        with patch.dict(os.environ, {"JWT_SECRET": ""}):
            response = _vista_solo_auth(request)
        self.assertEqual(response.status_code, 500)

    def test_permite_token_valido_y_adjunta_usuario(self):
        exp_futuro = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = _crear_token({"sub": "usr_123", "rol": "alumno", "exp": exp_futuro})
        request = self.factory.get("/api/turnos/", HTTP_AUTHORIZATION=f"Bearer {token}")
        response = _vista_solo_auth(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_body_json(response), {"sub": "usr_123", "rol": "alumno"})

    def test_rechaza_rol_no_permitido_con_403(self):
        token = _crear_token({"sub": "prof_1", "rol": "profesor"})
        request = self.factory.post("/api/turnos/reservar", HTTP_AUTHORIZATION=f"Bearer {token}")
        response = _vista_con_rol(request)
        self.assertEqual(response.status_code, 403)

    def test_permite_rol_autorizado(self):
        token = _crear_token({"sub": "alu_1", "rol": "alumno"})
        request = self.factory.post("/api/turnos/reservar", HTTP_AUTHORIZATION=f"Bearer {token}")
        response = _vista_con_rol(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_body_json(response)["sub"], "alu_1")

    def test_rechaza_si_falta_permiso_requerido(self):
        token = _crear_token({"sub": "alu_1", "permisos": ["reservas:listar"]})
        request = self.factory.post("/api/turnos/reservar", HTTP_AUTHORIZATION=f"Bearer {token}")
        response = _vista_con_permiso(request)
        self.assertEqual(response.status_code, 403)

    def test_permite_si_tiene_permiso_requerido(self):
        token = _crear_token(
            {"sub": "alu_1", "permisos": ["reservas:listar", "reservas:crear"]}
        )
        request = self.factory.post("/api/turnos/reservar", HTTP_AUTHORIZATION=f"Bearer {token}")
        response = _vista_con_permiso(request)
        self.assertEqual(response.status_code, 200)
