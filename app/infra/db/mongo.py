import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_cliente = None

def obtener_db_mongo():
    """Devuelve la instancia de la base de datos MongoDB reutilizando el pool de conexiones."""
    global _cliente
    if _cliente is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        _cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db_name = os.getenv("MONGO_DB_NAME", "tp_prog4")
    return _cliente[db_name]