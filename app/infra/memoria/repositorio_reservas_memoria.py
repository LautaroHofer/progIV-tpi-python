# Adaptador en memoria para tests de dominio

class RepositorioReservasMemoria:
    def __init__(self):
        self.reservas = {}
        self.contador_id = 1

    def crear(self, datos: dict):
        reserva = {"id": self.contador_id, **datos}
        self.reservas[self.contador_id] = reserva
        self.contador_id += 1
        return reserva

    def obtener_por_id(self, id: int):
        return self.reservas.get(id)
