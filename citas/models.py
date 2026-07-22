from django.db import models
from django.conf import settings
from pacientes.models import Paciente

class Cita(models.Model):
    """
    Modelo para controlar el agendamiento y estado de las citas médicas en el
    C.A. Consultorio Médico Las Gaviotas.
    """
    class EstadoCita(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ATENDIDA = 'ATENDIDA', 'Atendida'
        CANCELADA = 'CANCELADA', 'Cancelada'

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name="Paciente"
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={'rol': 'MEDICO'},
        related_name='citas_programadas',
        verbose_name="Médico Asignado"
    )
    fecha_hora = models.DateTimeField(
        verbose_name="Fecha y Hora de la Cita"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoCita.choices,
        default=EstadoCita.PENDIENTE,
        verbose_name="Estado de la Cita"
    )
    motivo = models.CharField(
        max_length=255,
        verbose_name="Motivo de la Cita"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Agendamiento"
    )

    class Meta:
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"
        ordering = ['-fecha_hora']

    def __str__(self):
        fecha_str = self.fecha_hora.strftime('%d/%m/%Y %H:%M') if self.fecha_hora else ""
        return f"Cita: {self.paciente.nombres} {self.paciente.apellidos} - {fecha_str} ({self.get_estado_display()})"
