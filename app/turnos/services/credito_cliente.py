# Cliente HTTP para comunicarse con la API de Node.js (créditos)
# Usa solo librería estándar de Python para no agregar dependencias.
import os
import json
import urllib.request
import urllib.error


def _obtener_url_node():
    return os.getenv("NODE_API_URL", "http://localhost:3000")


def descontar_credito(alumno_id, cantidad, motivo):
    """Descuenta créditos de un alumno llamando a la API de Node.

    Retorna el cuerpo de la respuesta parseado como JSON.
    Lanza excepción si la respuesta no es exitosa.
    """
    url = f"{_obtener_url_node()}/api/creditos/{alumno_id}/descontar"
    data = json.dumps({"cantidad": cantidad, "motivo": motivo}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise Exception(f"Error descontando credito: {e.code} {body}")


def agregar_credito(alumno_id, cantidad, motivo):
    """Agrega créditos a un alumno llamando a la API de Node.

    Retorna el cuerpo de la respuesta parseado como JSON.
    Lanza excepción si la respuesta no es exitosa.
    """
    url = f"{_obtener_url_node()}/api/creditos/{alumno_id}/agregar"
    data = json.dumps({"cantidad": cantidad, "motivo": motivo}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise Exception(f"Error agregando credito: {e.code} {body}")
