from django.contrib import admin
from .models import HistorialClinico, Receta

class RecetaInline(admin.StackedInline):
    model = Receta
    extra = 0

@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    """
    Configuración de administración para Historial Clinico.
    """
    list_display = ('paciente', 'medico', 'fecha_consulta', 'diagnostico')
    search_fields = ('paciente__cedula', 'paciente__nombres', 'paciente__apellidos', 'diagnostico')
    list_filter = ('fecha_consulta', 'medico')
    inlines = [RecetaInline]

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    """
    Configuración de administración para Receta Médica.
    """
    list_display = ('id', 'historial_clinico', 'fecha_emision')
    search_fields = ('historial_clinico__paciente__cedula', 'historial_clinico__paciente__nombres', 'indicaciones_medicamentos')
    list_filter = ('fecha_emision',)
