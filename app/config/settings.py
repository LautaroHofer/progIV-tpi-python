# Configuración mínima de Django (Módulo Horarios y Turnos)
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-desarrollo")
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

# La persistencia del servicio se realiza en MongoDB mediante PyMongo (ADR 002)
DATABASES = {}

USE_TZ = True
TIME_ZONE = "America/Argentina/Buenos_Aires"
