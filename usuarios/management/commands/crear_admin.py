import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

# Obtener el modelo de usuario personalizado de la aplicación
Usuario = get_user_model()

class Command(BaseCommand):
    help = 'Crea un superusuario administrador de forma no interactiva a partir de variables de entorno'

    def handle(self, *args, **options):
        # Leer las credenciales desde las variables de entorno configuradas
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        # Si faltan las variables esenciales, omitir para no romper el despliegue
        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "ADVERTENCIA: DJANGO_SUPERUSER_USERNAME o DJANGO_SUPERUSER_PASSWORD no están definidos. "
                    "Se omitirá la creación automática del administrador en este paso."
                )
            )
            return

        # Correo por defecto si no se definió uno
        email = email or "admin@consultoriogaviotas.com"

        # Verificar si ya existe un usuario registrado con ese nombre de usuario
        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"El usuario administrador '{username}' ya existe en el sistema. No se realizaron cambios."
                )
            )
            return

        try:
            # Crear el superusuario estándar de Django
            user = Usuario.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            # Asignar el rol del modelo personalizado como ADMINISTRADOR para los permisos
            user.rol = 'ADMINISTRADOR'
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Superusuario '{username}' creado exitosamente con rol ADMINISTRADOR."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error inesperado al intentar crear el superusuario: {str(e)}"
                )
            )
