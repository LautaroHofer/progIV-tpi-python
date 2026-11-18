# Conexion a Firebase Firestore
import json
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from app.config.env import BASE_DIR, config

# Evitar inicializar la app mas de una vez
if not firebase_admin._apps:
    project_id = config["firebase"]["project_id"] or "demo-tp-prog4"
    options = {"projectId": project_id}

    es_emulador = bool(config["firebase"]["emulator_host"])
    ruta_key = config["firebase"]["service_account_path"] or "serviceAccountKey.json"
    archivo_key = BASE_DIR / ruta_key

    if es_emulador:
        firebase_admin.initialize_app(options=options)
    elif config["firebase"]["service_account_key"]:
        # Credenciales pasadas como JSON en variable de entorno
        datos_json = json.loads(config["firebase"]["service_account_key"])
        cred = credentials.Certificate(datos_json)
        firebase_admin.initialize_app(cred, options)
    elif archivo_key.exists():
        # Credenciales leidas desde el archivo serviceAccountKey.json local
        cred = credentials.Certificate(str(archivo_key))
        firebase_admin.initialize_app(cred, options)
    else:
        # Fallback para correr tests locales sin conexion
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
        os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:8080")
        firebase_admin.initialize_app(options=options)

app = firebase_admin.get_app()

# Si se indico una base especifica (ej. uat o prod) la usamos, sino usa (default)
db_id = config["firebase"]["database_id"]
if db_id and db_id != "(default)":
    db = firestore.client(app=app, database_id=db_id)
else:
    db = firestore.client(app=app)


def obtener_conexion():
    return db
