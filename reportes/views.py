from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from pacientes.models import Paciente
from historias.models import HistorialClinico
from citas.models import Cita
from bitacora.utils import registrar_log
from .utils import generar_pdf

User = get_user_model()

@login_required
def menu_reportes(request):
    """
    Vista del menú principal de reportes de gestión.
    Permite el acceso a todos los roles autenticados.
    """
    return render(request, 'reportes/menu_reportes.html')


@login_required
def reporte_pacientes(request):
    """
    Vista para el reporte de pacientes registrados en el sistema.
    Filtros opcionales: Rango de fechas de registro e inclusión de inactivos.
    Permite previsualizar en pantalla o exportar a PDF.
    """
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    incluir_inactivos = request.GET.get('incluir_inactivos') == 'on'

    # Consulta base
    if incluir_inactivos:
        pacientes = Paciente.objects.all()
    else:
        pacientes = Paciente.objects.filter(activo=True)

    # Filtros de fecha de registro
    if fecha_inicio:
        pacientes = pacientes.filter(fecha_registro__date__gte=fecha_inicio)
    if fecha_fin:
        pacientes = pacientes.filter(fecha_registro__date__lte=fecha_fin)

    pacientes = pacientes.order_by('apellidos', 'nombres')

    # Si se solicita exportación a PDF
    if request.GET.get('exportar') == 'pdf':
        # Registrar en bitácora de auditoría
        desc_filtros = f"Filtros: Inicio={fecha_inicio or 'N/A'}, Fin={fecha_fin or 'N/A'}, Incluir inactivos={incluir_inactivos}"
        registrar_log(
            usuario=request.user,
            accion='CREAR',
            modelo_afectado='Reporte',
            descripcion=f"Generó Reporte de Pacientes en PDF. {desc_filtros}"
        )
        
        contexto = {
            'pacientes': pacientes,
            'usuario': request.user,
            'fecha_generacion': timezone.now(),
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'incluir_inactivos': incluir_inactivos,
        }
        return generar_pdf(request, 'reportes/pdf_pacientes.html', contexto)

    contexto = {
        'pacientes': pacientes,
        'fecha_inicio_filtro': fecha_inicio,
        'fecha_fin_filtro': fecha_fin,
        'incluir_inactivos': incluir_inactivos,
        'busqueda_realizada': ('filtrar' in request.GET),
    }
    return render(request, 'reportes/filtros_pacientes.html', contexto)


@login_required
def reporte_consultas(request):
    """
    Vista para el reporte de consultas médicas registradas.
    Filtro obligatorio: Rango de fechas de consulta.
    Filtro opcional: Médico tratante.
    """
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    medico_id = request.GET.get('medico', '').strip()

    consultas = []
    rango_valido = False

    # El rango de fechas es estrictamente obligatorio para evitar consultas masivas
    if fecha_inicio and fecha_fin:
        rango_valido = True
        consultas = HistorialClinico.objects.filter(
            fecha_consulta__date__range=[fecha_inicio, fecha_fin]
        ).select_related('paciente', 'medico')
        
        if medico_id:
            consultas = consultas.filter(medico_id=medico_id)
        
        consultas = consultas.order_by('-fecha_consulta')
    elif 'filtrar' in request.GET or 'exportar' in request.GET:
        messages.error(request, "El rango de fechas (Desde / Hasta) es obligatorio para generar este reporte.")

    # Cargar médicos del sistema para el selector
    medicos = User.objects.filter(rol__in=['MEDICO', 'ADMINISTRADOR']).order_by('last_name', 'first_name')

    # Si se solicita exportación a PDF y los datos son válidos
    if request.GET.get('exportar') == 'pdf' and rango_valido:
        # Registrar en bitácora
        medico_obj = User.objects.filter(pk=medico_id).first() if medico_id else None
        medico_nombre = medico_obj.get_full_name() if medico_obj else "Todos"
        desc_filtros = f"Filtros: Rango=[{fecha_inicio} a {fecha_fin}], Médico={medico_nombre}"
        
        registrar_log(
            usuario=request.user,
            accion='CREAR',
            modelo_afectado='Reporte',
            descripcion=f"Generó Reporte de Consultas Médicas en PDF. {desc_filtros}"
        )

        contexto = {
            'consultas': consultas,
            'usuario': request.user,
            'fecha_generacion': timezone.now(),
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'medico_nombre': medico_nombre,
        }
        return generar_pdf(request, 'reportes/pdf_consultas.html', contexto)

    contexto = {
        'consultas': consultas,
        'medicos': medicos,
        'fecha_inicio_filtro': fecha_inicio,
        'fecha_fin_filtro': fecha_fin,
        'medico_filtro': medico_id,
        'rango_valido': rango_valido,
        'busqueda_realizada': ('filtrar' in request.GET),
    }
    return render(request, 'reportes/filtros_consultas.html', contexto)


@login_required
def reporte_citas(request):
    """
    Vista para el reporte de citas médicas de la agenda.
    Filtros opcionales: Rango de fechas y estado de la cita.
    """
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    estado = request.GET.get('estado', '').strip().upper()

    citas = Cita.objects.all().select_related('paciente', 'medico')

    # Aplicamos filtros opcionales
    if fecha_inicio:
        citas = citas.filter(fecha_hora__date__gte=fecha_inicio)
    if fecha_fin:
        citas = citas.filter(fecha_hora__date__lte=fecha_fin)
    if estado:
        citas = citas.filter(estado=estado)

    citas = citas.order_by('fecha_hora')

    # Si se solicita exportación a PDF
    if request.GET.get('exportar') == 'pdf':
        # Registrar en bitácora
        desc_filtros = f"Filtros: Inicio={fecha_inicio or 'N/A'}, Fin={fecha_fin or 'N/A'}, Estado={estado or 'Todos'}"
        registrar_log(
            usuario=request.user,
            accion='CREAR',
            modelo_afectado='Reporte',
            descripcion=f"Generó Reporte de Citas en PDF. {desc_filtros}"
        )

        contexto = {
            'citas': citas,
            'usuario': request.user,
            'fecha_generacion': timezone.now(),
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'estado_nombre': dict(Cita.EstadoCita.choices).get(estado, "Todos") if estado else "Todos",
        }
        return generar_pdf(request, 'reportes/pdf_citas.html', contexto)

    contexto = {
        'citas': citas,
        'estados': Cita.EstadoCita.choices,
        'fecha_inicio_filtro': fecha_inicio,
        'fecha_fin_filtro': fecha_fin,
        'estado_filtro': estado,
        'busqueda_realizada': ('filtrar' in request.GET),
    }
    return render(request, 'reportes/filtros_citas.html', contexto)
