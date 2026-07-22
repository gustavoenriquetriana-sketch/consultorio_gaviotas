from django.contrib import admin
from .models import RegistroActividad

@admin.register(RegistroActividad)
class RegistroActividadAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para la Bitácora de Auditoría.
    Establece la tabla como solo lectura para resguardar la validez de los logs
    frente a manipulaciones manuales en el admin.
    """
    list_display = ('usuario', 'accion', 'modelo_afectado', 'fecha_hora')
    list_filter = ('accion', 'modelo_afectado', 'fecha_hora')
    search_fields = ('usuario__username', 'descripcion', 'modelo_afectado')
    
    # Todos los campos son de solo lectura
    readonly_fields = ('usuario', 'accion', 'modelo_afectado', 'descripcion', 'fecha_hora')

    # Desactivar permisos para añadir nuevos logs
    def has_add_permission(self, request):
        return False

    # Desactivar permisos para modificar logs existentes
    def has_change_permission(self, request, obj=None):
        return False

    # Desactivar permisos para eliminar registros
    def has_delete_permission(self, request, obj=None):
        return False
