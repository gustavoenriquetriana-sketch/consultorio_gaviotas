from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración de la administración para el modelo de Usuario personalizado.
    """
    fieldsets = UserAdmin.fieldsets + (
        ('Información del Consultorio', {'fields': ('rol', 'cedula', 'telefono', 'especialidad')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del Consultorio', {'fields': ('rol', 'cedula', 'telefono', 'especialidad')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'cedula', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'cedula', 'email')
