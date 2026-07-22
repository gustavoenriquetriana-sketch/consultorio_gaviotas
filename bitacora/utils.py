from .models import RegistroActividad

def registrar_log(usuario, accion, modelo_afectado, descripcion):
    """
    Función auxiliar explicativa para registrar actividades en la bitácora.
    Diseñada de forma simple y explícita para facilitar su justificación
    durante la defensa oral de la tesis.
    """
    try:
        # Se crea el registro de actividad de manera directa en la base de datos
        RegistroActividad.objects.create(
            usuario=usuario,
            accion=accion,
            modelo_afectado=modelo_afectado,
            descripcion=descripcion
        )
    except Exception as e:
        # Capturamos excepciones para evitar que un fallo en el registro de logs
        # interrumpa el flujo del negocio principal
        print(f"Error al guardar en la bitácora: {e}")
