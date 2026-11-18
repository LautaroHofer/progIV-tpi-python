# Lectura y validación de variables de entorno según ambiente (local, test, uat, prod)
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 1. Detectar ambiente
python_env = os.getenv("PYTHON_ENV") or os.getenv("NODE_ENV") or "development"
os.environ["PYTHON_ENV"] = python_env

# 2. Cargar archivos .env según prioridad (.env.local, .env.<ambiente>, .env)
env_local = BASE_DIR / ".env.local"
if env_local.exists():
    load_dotenv(dotenv_path=env_local)

env_specific = BASE_DIR / f".env.{python_env}"
if env_specific.exists():
    load_dotenv(dotenv_path=env_specific)

load_dotenv(dotenv_path=BASE_DIR / ".env")


def resolver_database_id():
    custom_id = (
        os.getenv("FB_DATABASE_ID")
        or os.getenv("FIRESTORE_DATABASE_ID")
        or os.getenv("FIREBASE_DATABASE_ID")
    )
    if custom_id:
        return custom_id

    if python_env in ("uat", "staging"):
        return "turnapp-uat"
    if python_env in ("production", "prod"):
        return "turnapp-prod"
    return "(default)"


def validar_variables_entorno():
    requeridas = ["SECRET_KEY"]

    if python_env in ("uat", "production", "prod"):
        tiene_credencial = (
            os.getenv("FB_SERVICE_ACCOUNT_KEY")
            or os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
            or os.getenv("FB_SERVICE_ACCOUNT_PATH")
            or os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or os.getenv("K_SERVICE")
            or (BASE_DIR / "serviceAccountKey.json").exists()
        )
        if not tiene_credencial:
            print(
                f"Error: En ambiente {python_env} se requiere credenciales de Firebase.",
                file=sys.stderr,
            )
            sys.exit(1)

    faltantes = [clave for clave in requeridas if not os.getenv(clave)]
    if faltantes:
        print(
            f"Error: Faltan variables de entorno obligatorias: {', '.join(faltantes)}",
            file=sys.stderr,
        )
        sys.exit(1)


config = {
    "env": python_env,
    "port": int(os.getenv("PORT", "8000")),
    "secret_key": os.getenv("SECRET_KEY", "clave-secreta-desarrollo"),
    "node_api_url": os.getenv("NODE_API_URL", "http://localhost:3000"),
    "firebase": {
        "project_id": (
            os.getenv("FB_PROJECT_ID")
            or os.getenv("FIREBASE_PROJECT_ID")
            or os.getenv("GCLOUD_PROJECT")
            or ("demo-tp-prog4" if python_env == "test" else None)
        ),
        "database_id": resolver_database_id(),
        "service_account_path": (
            os.getenv("FB_SERVICE_ACCOUNT_PATH")
            or os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        ),
        "service_account_key": (
            os.getenv("FB_SERVICE_ACCOUNT_KEY")
            or os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
        ),
        "emulator_host": os.getenv("FIRESTORE_EMULATOR_HOST"),
    },
}
