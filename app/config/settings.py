# Configuración mínima de Django (Módulo Horarios y Turnos con Cloud Firestore)
import os
from app.config.env import BASE_DIR, config

SECRET_KEY = config["secret_key"]
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "app.config.urls"

# La persistencia se gestiona mediante Cloud Firestore (app/infra/db/conexion.py)
DATABASES = {}

USE_TZ = True
TIME_ZONE = "America/Argentina/Buenos_Aires"
