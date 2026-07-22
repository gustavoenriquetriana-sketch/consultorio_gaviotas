from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from decouple import config
from usuarios.decorators import rol_requerido
from .models import RegistroActividad
from .utils import registrar_log
import os
import subprocess

User = get_user_model()

@rol_requerido('ADMINISTRADOR')
def listar_logs(request):
    """
    Vista de control para auditar y listar la bitácora de actividad del sistema.
    Acceso restringido únicamente para usuarios con rol de ADMINISTRADOR.
    Permite filtrado dinámico por usuario, tipo de acción y rango de fechas.
    """
    # Recuperamos filtros de la petición GET
    usuario_id = request.GET.get('usuario', '').strip()
    accion_filtro = request.GET.get('accion', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()

    logs = RegistroActividad.objects.all().select_related('usuario')

    # Aplicamos filtros si están presentes
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    
    if accion_filtro:
        logs = logs.filter(accion=accion_filtro)

    if fecha_inicio:
        logs = logs.filter(fecha_hora__date__gte=fecha_inicio)
        
    if fecha_fin:
        logs = logs.filter(fecha_hora__date__lte=fecha_fin)

    # Paginación: 30 registros de logs de auditoría por página
    paginator = Paginator(logs, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtenemos listado de todos los usuarios registrados para el selector del filtro
    todos_usuarios = User.objects.all().order_by('last_name', 'first_name')

    contexto = {
        'page_obj': page_obj,
        'todos_usuarios': todos_usuarios,
        'acciones': RegistroActividad.Acciones.choices,
        'usuario_filtro': usuario_id,
        'accion_filtro': accion_filtro,
        'fecha_inicio_filtro': fecha_inicio,
        'fecha_fin_filtro': fecha_fin,
    }
    return render(request, 'bitacora/listado_logs.html', contexto)


@rol_requerido('ADMINISTRADOR')
def generar_respaldo(request):
    """
    Vista para realizar el volcado completo de la base de datos local 'gaviotas_db'
    y descargar el archivo SQL resultante desde la interfaz web.
    Usa el ejecutable 'pg_dump' y lee credenciales seguras de settings/env.
    """
    # Leer datos de conexión desde settings.py
    db_config = settings.DATABASES['default']
    db_name = db_config.get('NAME')
    db_user = db_config.get('USER')
    db_password = db_config.get('PASSWORD')
    db_host = db_config.get('HOST', 'localhost')
    db_port = db_config.get('PORT', '5432')

    # Leer la ruta de pg_dump desde el archivo .env, con fallback al comando global
    pg_dump_path = config('PG_DUMP_PATH', default='pg_dump')

    # Copiar variables de entorno actuales e inyectar la contraseña temporalmente
    env = os.environ.copy()
    if db_password:
        env['PGPASSWORD'] = str(db_password)

    # Construir el comando pg_dump
    cmd = [
        pg_dump_path,
        '-h', db_host,
        '-p', str(db_port),
        '-U', db_user,
        '-F', 'p',  # Formato texto plano (SQL)
        db_name
    ]

    try:
        # Ejecutar el comando pg_dump mediante subprocess
        process = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            shell=True if os.name == 'nt' else False  # En Windows facilita la resolución de path ejecutables
        )

        # Si la ejecución fue exitosa
        if process.returncode == 0:
            sql_content = process.stdout
            
            # Formatear el nombre del archivo con fecha y hora actual
            timestamp = timezone.localtime(timezone.now()).strftime('%Y-%m-%d_%H%M')
            nombre_archivo = f"respaldo_gaviotas_{timestamp}.sql"

            # Registrar la actividad en la bitácora de auditoría
            registrar_log(
                usuario=request.user,
                accion='CREAR',
                modelo_afectado='Respaldo BDD',
                descripcion=f"Generó y descargó el respaldo de la base de datos '{db_name}' ({nombre_archivo}) de forma exitosa."
            )

            # Responder con el archivo para su descarga directa en el navegador
            from django.http import HttpResponse
            response = HttpResponse(sql_content, content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            return response
        else:
            # Capturar el mensaje de error de postgresql
            error_msg = process.stderr.decode('utf-8', errors='ignore')
            messages.error(request, f"Error al generar respaldo de base de datos: {error_msg}")
    
    except FileNotFoundError:
        messages.error(
            request, 
            "El ejecutable 'pg_dump' no fue encontrado. Verifique que PostgreSQL esté instalado "
            "y que la ruta esté configurada correctamente en la variable de entorno PG_DUMP_PATH."
        )
    except Exception as e:
        messages.error(request, f"Ocurrió un error inesperado al intentar generar el respaldo: {str(e)}")

    # Retornar a la bitácora si falla
    return redirect('listar_logs')
