from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .utils import registrar_log

@receiver(user_logged_in)
def log_iniciar_sesion(sender, request, user, **kwargs):
    """
    Señal de Django que se activa cuando un usuario inicia sesión correctamente.
    """
    descripcion = f"El usuario '{user.username}' ({user.get_rol_display()}) inició sesión en el sistema."
    registrar_log(user, 'LOGIN', 'Usuario', descripcion)

@receiver(user_logged_out)
def log_cerrar_sesion(sender, request, user, **kwargs):
    """
    Señal de Django que se activa cuando un usuario cierra sesión en el sistema.
    """
    if user:
        descripcion = f"El usuario '{user.username}' ({user.get_rol_display()}) cerró sesión en el sistema."
        registrar_log(user, 'LOGOUT', 'Usuario', descripcion)
