# Adaptador simulado de notificaciones por consola

class NotificadorConsola:
    def enviar_recordatorio(self, email: str, clase_id: int):
        print(f"[Notificación] Recordatorio enviado a {email} para la clase {clase_id}")
        return {"enviado": True}
