# Lectura y validacion de variables de entorno
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")

python_env = os.getenv("PYTHON_ENV", "development")


def resolver_database_id():
    if os.getenv("FB_DATABASE_ID"):
        return os.getenv("FB_DATABASE_ID")
    if python_env == "uat":
        return "turnapp-uat"
    if python_env == "production":
        return "turnapp-prod"
    return "(default)"


def validar_variables_entorno():
    requeridas = ["SECRET_KEY"]
    faltantes = [clave for clave in requeridas if not os.getenv(clave)]
    if faltantes:
        print(f"Error: Faltan variables de entorno obligatorias: {', '.join(faltantes)}", file=sys.stderr)
        sys.exit(1)


config = {
    "env": python_env,
    "port": int(os.getenv("PORT", "8000")),
    "secret_key": os.getenv("SECRET_KEY", "clave-secreta-desarrollo"),
    "node_api_url": os.getenv("NODE_API_URL", "http://localhost:3000"),
    "firebase": {
        "project_id": os.getenv("FB_PROJECT_ID", "turnapp-node"),
        "database_id": resolver_database_id(),
        "service_account_path": os.getenv("FB_SERVICE_ACCOUNT_PATH"),
        "service_account_key": os.getenv("FB_SERVICE_ACCOUNT_KEY"),
        "emulator_host": os.getenv("FIRESTORE_EMULATOR_HOST"),
    },
}
