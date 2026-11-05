# Entidad: Horario (Clase o turno programado en la grilla)

class Horario:
    def __init__(self, id=None, sala_id=None, profesor_id=None, actividad=None, fecha_inicio=None, fecha_fin=None, cupo=None):
        self.id = id
        self.sala_id = sala_id
        self.profesor_id = profesor_id
        self.actividad = actividad
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.cupo = cupo
