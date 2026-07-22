from django.contrib import admin
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """
    Configuración de administración para Citas Médicas.
    """
    list_display = ('paciente', 'medico', 'fecha_hora', 'estado', 'motivo')
    list_filter = ('estado', 'fecha_hora', 'medico')
    search_fields = ('paciente__cedula', 'paciente__nombres', 'paciente__apellidos', 'motivo')
    ordering = ('-fecha_hora',)
