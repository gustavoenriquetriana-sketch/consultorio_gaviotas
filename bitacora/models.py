from django.db import models
from django.conf import settings

class RegistroActividad(models.Model):
    """
    Modelo para la Bitácora de Auditoría del C.A. Consultorio Médico Las Gaviotas.
    Registra las operaciones y acciones críticas realizadas por los usuarios.
    """
    class Acciones(models.TextChoices):
        CREAR = 'CREAR', 'Crear'
        EDITAR = 'EDITAR', 'Editar'
        ELIMINAR = 'ELIMINAR', 'Eliminar'
        DESACTIVAR = 'DESACTIVAR', 'Desactivar'
        LOGIN = 'LOGIN', 'Iniciar Sesión'
        LOGOUT = 'LOGOUT', 'Cerrar Sesión'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario responsable",
        help_text="Usuario que ejecutó la acción. Nulo si el usuario fue eliminado."
    )
    accion = models.CharField(
        max_length=20,
        choices=Acciones.choices,
        verbose_name="Acción ejecutada"
    )
    modelo_afectado = models.CharField(
        max_length=100,
        verbose_name="Módulo / Tabla afectada",
        help_text="Nombre de la entidad involucrada (ej: Paciente, Cita, Consulta)"
    )
    descripcion = models.TextField(
        verbose_name="Descripción de la actividad",
        help_text="Detalle legible de los cambios o acción realizada"
    )
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora del suceso"
    )

    class Meta:
        verbose_name = "Registro de Actividad"
        verbose_name_plural = "Registros de Actividades"
        ordering = ['-fecha_hora']

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema/Anónimo"
        fecha_str = self.fecha_hora.strftime('%d/%m/%Y %I:%M %p') if self.fecha_hora else ""
        return f"{usuario_str} - {self.get_accion_display()} - {fecha_str}"
