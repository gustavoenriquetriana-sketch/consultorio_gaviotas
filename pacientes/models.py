from django.db import models

class Paciente(models.Model):
    """
    Modelo para gestionar la información personal de los pacientes registrados
    en el C.A. Consultorio Médico Las Gaviotas.
    """
    class Sexo(models.TextChoices):
        FEMENINO = 'F', 'Femenino'
        MASCULINO = 'M', 'Masculino'
        OTRO = 'O', 'Otro'

    cedula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Cédula de Identidad",
        help_text="Número de documento de identidad único del paciente"
    )
    nombres = models.CharField(
        max_length=100,
        verbose_name="Nombres"
    )
    apellidos = models.CharField(
        max_length=100,
        verbose_name="Apellidos"
    )
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de Nacimiento"
    )
    sexo = models.CharField(
        max_length=1,
        choices=Sexo.choices,
        verbose_name="Sexo Biológico"
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono Principal"
    )
    direccion = models.TextField(
        verbose_name="Dirección de Habitación"
    )
    correo_electronico = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo Electrónico",
        help_text="Campo opcional"
    )
    contacto_emergencia_nombre = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Nombre de Contacto de Emergencia"
    )
    contacto_emergencia_telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono de Contacto de Emergencia"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Paciente Activo",
        help_text="Define si el paciente está habilitado o deshabilitado (borrado lógico)"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro en Sistema"
    )

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.cedula} - {self.apellidos}, {self.nombres}"
