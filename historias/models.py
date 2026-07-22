from django.db import models
from django.conf import settings
from pacientes.models import Paciente

class HistorialClinico(models.Model):
    """
    Modelo para registrar cada consulta e historial clínico centralizado de los pacientes
    en el C.A. Consultorio Médico Las Gaviotas.
    """
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='historias_clinicas',
        verbose_name="Paciente"
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={'rol': 'MEDICO'},
        related_name='consultas_realizadas',
        verbose_name="Médico Tratante"
    )
    fecha_consulta = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora de Consulta"
    )
    motivo_consulta = models.TextField(
        verbose_name="Motivo de Consulta"
    )
    antecedentes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Antecedentes Médicos / Personales"
    )
    diagnostico = models.TextField(
        verbose_name="Diagnóstico"
    )
    notas_observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas u Observaciones Adicionales"
    )

    class Meta:
        verbose_name = "Historial Clínico"
        verbose_name_plural = "Historiales Clínicos"
        ordering = ['-fecha_consulta']

    def __str__(self):
        fecha_str = self.fecha_consulta.strftime('%d/%m/%Y') if self.fecha_consulta else ""
        return f"Consulta de {self.paciente.nombres} {self.paciente.apellidos} - {fecha_str}"


class Receta(models.Model):
    """
    Modelo para gestionar las recetas médicas vinculadas directamente a una consulta / historial clínico.
    """
    historial_clinico = models.OneToOneField(
        HistorialClinico,
        on_delete=models.CASCADE,
        related_name='receta',
        verbose_name="Consulta / Historial Clínico Asociado"
    )
    fecha_emision = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Emisión"
    )
    indicaciones_medicamentos = models.TextField(
        verbose_name="Indicaciones y Medicamentos Recetados"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones Adicionales"
    )

    class Meta:
        verbose_name = "Receta Médica"
        verbose_name_plural = "Recetas Médicas"
        ordering = ['-fecha_emision']

    def __str__(self):
        fecha_str = self.fecha_emision.strftime('%d/%m/%Y') if self.fecha_emision else ""
        return f"Receta #{self.id} - {self.historial_clinico.paciente} ({fecha_str})"
