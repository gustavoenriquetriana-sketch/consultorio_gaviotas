from django.contrib import admin
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """
    Configuración de administración para el modelo Paciente.
    """
    list_display = ('cedula', 'apellidos', 'nombres', 'sexo', 'telefono', 'fecha_nacimiento', 'fecha_registro')
    search_fields = ('cedula', 'nombres', 'apellidos', 'telefono')
    list_filter = ('sexo', 'fecha_registro')
    ordering = ('apellidos', 'nombres')
