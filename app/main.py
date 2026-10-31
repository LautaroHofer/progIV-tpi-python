from fastapi import FastAPI
from app.config.env import config

app = FastAPI(title="API Python - TP Prog IV")


@app.get("/salud")
def salud():
    return {"estado": "ok", "servicio": "api-python", "puerto": config.PORT}


@app.get("/")
def raiz():
    return {"mensaje": "API Python funcionando"}
