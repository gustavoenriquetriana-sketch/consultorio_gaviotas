from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from usuarios.decorators import rol_requerido
from bitacora.utils import registrar_log
from .models import Paciente
from .forms import PacienteForm

@login_required
def buscar_pacientes(request):
    """
    Vista de búsqueda avanzada de pacientes.
    Permite filtrar por nombre/apellido (parcial), número de cédula (parcial)
    y fecha de nacimiento (exacta) usando un formulario HTML.
    Excluye por defecto a los pacientes inactivos (activo=False), a menos que
    se proporcione el parámetro GET 'incluir_inactivos'.
    """
    nombre = request.GET.get('nombre', '').strip()
    cedula = request.GET.get('cedula', '').strip()
    fecha_nacimiento = request.GET.get('fecha_nacimiento', '').strip()
    incluir_inactivos = request.GET.get('incluir_inactivos') == 'on'

    if incluir_inactivos:
        pacientes = Paciente.objects.all()
    else:
        pacientes = Paciente.objects.filter(activo=True)

    busqueda_realizada = False

    # Aplicamos filtros opcionales de búsqueda
    if nombre:
        pacientes = pacientes.filter(Q(nombres__icontains=nombre) | Q(apellidos__icontains=nombre))
        busqueda_realizada = True
    
    if cedula:
        pacientes = pacientes.filter(cedula__icontains=cedula)
        busqueda_realizada = True
        
    if fecha_nacimiento:
        pacientes = pacientes.filter(fecha_nacimiento=fecha_nacimiento)
        busqueda_realizada = True

    contexto = {
        'pacientes': pacientes,
        'nombre_filtro': nombre,
        'cedula_filtro': cedula,
        'fecha_nacimiento_filtro': fecha_nacimiento,
        'incluir_inactivos': incluir_inactivos,
        'busqueda_realizada': busqueda_realizada,
    }
    return render(request, 'pacientes/buscar.html', contexto)


@login_required
def detalle_paciente(request, pk):
    """
    Vista detallada de la ficha completa del paciente.
    Muestra los datos personales e historial clínico (consultas y recetas asociadas).
    """
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Se obtienen todas las historias clínicas asociadas con sus recetas y médicos correspondientes
    historias = paciente.historias_clinicas.all().select_related('medico', 'receta')
    
    # Se obtienen las citas del paciente ordenadas
    citas = paciente.citas.all().select_related('medico')

    contexto = {
        'paciente': paciente,
        'historias': historias,
        'citas': citas,
    }
    return render(request, 'pacientes/detalle.html', contexto)


@rol_requerido('ADMINISTRADOR', 'RECEPCIONISTA')
def registrar_paciente(request):
    """
    Vista para registrar un nuevo paciente en el consultorio.
    Maneja el método GET mostrando un formulario vacío y el método POST
    para validar la información y guardar al nuevo paciente.
    """
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            try:
                nuevo_paciente = form.save()
                registrar_log(request.user, 'CREAR', 'Paciente', f"Registró al paciente '{nuevo_paciente.nombres} {nuevo_paciente.apellidos}' (Cédula: {nuevo_paciente.cedula})")
                messages.success(request, f"Paciente '{nuevo_paciente.nombres} {nuevo_paciente.apellidos}' registrado exitosamente.")
                return redirect('detalle_paciente', pk=nuevo_paciente.pk)
            except Exception as e:
                messages.error(request, "Ocurrió un error inesperado al guardar la información. Por favor intente de nuevo.")
        else:
            messages.error(request, "Error de validación. Revise los datos introducidos en el formulario.")
    else:
        form = PacienteForm()

    contexto = {
        'form': form
    }
    return render(request, 'pacientes/registrar.html', contexto)


@rol_requerido('ADMINISTRADOR', 'RECEPCIONISTA')
def editar_paciente(request, paciente_id):
    """
    Vista para editar la información de un paciente existente.
    Reutiliza PacienteForm precargado con los datos actuales.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            registrar_log(request.user, 'EDITAR', 'Paciente', f"Actualizó datos del paciente '{paciente.nombres} {paciente.apellidos}' (Cédula: {paciente.cedula})")
            messages.success(request, f"Información del paciente '{paciente.nombres} {paciente.apellidos}' actualizada exitosamente.")
            return redirect('detalle_paciente', pk=paciente.pk)
        else:
            messages.error(request, "Error al actualizar los datos. Revise el formulario.")
    else:
        form = PacienteForm(instance=paciente)

    contexto = {
        'form': form,
        'paciente': paciente,
    }
    return render(request, 'pacientes/editar_paciente.html', contexto)


@rol_requerido('ADMINISTRADOR')
def desactivar_paciente(request, paciente_id):
    """
    Vista para desactivar un paciente (borrado lógico, activo=False).
    Muestra una página de confirmación previa y procesa la desactivación vía POST.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if request.method == 'POST':
        paciente.activo = False
        paciente.save()
        registrar_log(request.user, 'DESACTIVAR', 'Paciente', f"Desactivó (borrado lógico) al paciente '{paciente.nombres} {paciente.apellidos}' (Cédula: {paciente.cedula})")
        messages.success(request, f"Paciente '{paciente.nombres} {paciente.apellidos}' desactivado exitosamente del sistema.")
        return redirect('buscar_pacientes')
    
    contexto = {
        'titulo_accion': "Desactivar Paciente",
        'mensaje': f"¿Está seguro que desea desactivar al paciente '{paciente.nombres} {paciente.apellidos}' (Cédula: {paciente.cedula})? Este cambio ocultará al paciente de la agenda activa y las búsquedas generales.",
        'url_cancelar': reverse('detalle_paciente', args=[paciente.pk])
    }
    return render(request, 'confirmar_eliminar.html', contexto)
