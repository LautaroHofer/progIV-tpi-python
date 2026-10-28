from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="API Python - TP Prog IV")


@app.get("/salud")
def salud():
    return {"estado": "ok", "servicio": "api-python"}


@app.get("/")
def raiz():
    return {"mensaje": "API Python funcionando"}
