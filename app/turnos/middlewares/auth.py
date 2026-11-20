# Decoradores de autenticación y autorización por JWT (PyJWT)
from functools import wraps
import os
import jwt
from django.http import JsonResponse

ALGORITMO_JWT = "HS256"


def _extraer_token_bearer(request):
    """Extrae el token del header Authorization con formato 'Bearer <token>'."""
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header:
        return None

    partes = auth_header.split(" ", 1)
    if len(partes) != 2 or partes[0].lower() != "bearer":
        return None

    token = partes[1].strip()
    return token or None


def requiere_auth(view_func):
    """Verifica el JWT del header Authorization y adjunta el payload en request.usuario."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = _extraer_token_bearer(request)
        if not token:
            return JsonResponse(
                {"error": "Token de autenticación requerido o con formato inválido"},
                status=401,
            )

        secret = os.getenv("JWT_SECRET")
        if not secret:
            return JsonResponse(
                {"error": "Configuración de autenticación incompleta en el servidor"},
                status=500,
            )

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=[ALGORITMO_JWT],
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expirado"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Token inválido"}, status=401)

        request.usuario = payload
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def requiere_rol(roles_permitidos):
    """Verifica que el usuario autenticado posea alguno de los roles permitidos."""
    roles = set(roles_permitidos)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            usuario = getattr(request, "usuario", None)
            if not usuario:
                return JsonResponse({"error": "Usuario no autenticado"}, status=401)

            if usuario.get("rol") not in roles:
                return JsonResponse(
                    {"error": "No tenés permisos suficientes para realizar esta acción"},
                    status=403,
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def requiere_permiso(permiso_requerido):
    """Verifica que el usuario autenticado incluya el permiso requerido en el JWT."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            usuario = getattr(request, "usuario", None)
            if not usuario:
                return JsonResponse({"error": "Usuario no autenticado"}, status=401)

            permisos = usuario.get("permisos")
            if not isinstance(permisos, list) or permiso_requerido not in permisos:
                return JsonResponse(
                    {"error": "No tenés el permiso requerido para realizar esta acción"},
                    status=403,
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
