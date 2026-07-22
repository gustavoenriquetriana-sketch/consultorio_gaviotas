from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para el C.A. Consultorio Médico Las Gaviotas.
    Extiende AbstractUser de Django para añadir control de roles y datos adicionales.
    """
    class Rol(models.TextChoices):
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
        MEDICO = 'MEDICO', 'Médico'
        RECEPCIONISTA = 'RECEPCIONISTA', 'Recepcionista'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.RECEPCIONISTA,
        verbose_name="Rol en el sistema",
        help_text="Define los permisos del usuario dentro de la aplicación"
    )
    cedula = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Cédula de Identidad"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono de contacto"
    )
    especialidad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Especialidad Médica",
        help_text="Campo opcional. Aplica principalmente si el usuario tiene el rol de Médico"
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        nombre_completo = self.get_full_name()
        if nombre_completo:
            return f"{nombre_completo} ({self.username}) - {self.get_rol_display()}"
        return f"{self.username} - {self.get_rol_display()}"
