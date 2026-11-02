# Adaptador en memoria de Horarios para tests de dominio

class RepositorioHorariosMemoria:
    def __init__(self):
        self.horarios = {}
        self.contador_id = 1
