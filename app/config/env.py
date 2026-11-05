# Lectura y validación de variables de entorno al arrancar
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def validar_variables_entorno():
    requeridas = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    faltantes = [clave for clave in requeridas if not os.getenv(clave)]
    if faltantes:
        print(f"Error: Faltan variables de entorno obligatorias: {', '.join(faltantes)}", file=sys.stderr)
        sys.exit(1)
