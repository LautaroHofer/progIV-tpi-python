# Tests de integracion de conexion a Firestore
from app.infra.db.conexion import db


def test_firestore_inicializado():
    assert db is not None
    assert hasattr(db, "collection")

