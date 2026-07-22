from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from usuarios.decorators import rol_requerido
from bitacora.utils import registrar_log
from pacientes.models import Paciente
from .models import Cita
from .forms import CitaForm

@rol_requerido('ADMINISTRADOR', 'RECEPCIONISTA')
def agendar_cita(request, paciente_id):
    """
    Vista para registrar y agendar una nueva cita para un paciente específico.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.paciente = paciente
            cita.estado = Cita.EstadoCita.PENDIENTE
            cita.save()
            registrar_log(request.user, 'CREAR', 'Cita', f"Agendó cita para el paciente '{paciente.nombres} {paciente.apellidos}' (Cédula: {paciente.cedula}) para el {cita.fecha_hora.strftime('%d/%m/%Y %I:%M %p')}")
            messages.success(request, f"Cita para '{paciente.nombres} {paciente.apellidos}' programada exitosamente.")
            return redirect('detalle_paciente', pk=paciente.pk)
        else:
            messages.error(request, "Error de validación. Por favor revise la fecha y hora seleccionada.")
    else:
        form = CitaForm()

    contexto = {
        'paciente': paciente,
        'form': form
    }
    return render(request, 'citas/agendar_cita.html', contexto)


@login_required
def listar_citas(request):
    """
    Vista general de la agenda de citas del consultorio.
    Permite filtrar por estado (PENDIENTE, ATENDIDA, CANCELADA) mediante GET.
    """
    estado_filtro = request.GET.get('estado', '').strip().upper()
    citas = Cita.objects.all().select_related('paciente', 'medico')

    # Si se seleccionó un filtro válido, se aplica a la consulta
    if estado_filtro in [choice[0] for choice in Cita.EstadoCita.choices]:
        citas = citas.filter(estado=estado_filtro)
    else:
        estado_filtro = '' # Reset si se pasa un valor inválido

    # Ordenar cronológicamente (las más próximas primero)
    citas = citas.order_by('fecha_hora')

    contexto = {
        'citas': citas,
        'estado_filtro': estado_filtro,
        'estados': Cita.EstadoCita.choices
    }
    return render(request, 'citas/listado_citas.html', contexto)


@login_required
def cambiar_estado_cita(request, cita_id, nuevo_estado):
    """
    Vista rápida para actualizar el estado de una cita médica (Pendiente, Atendida, Cancelada).
    Redirige de vuelta a la página desde la cual se llamó.
    """
    cita = get_object_or_404(Cita, pk=cita_id)
    nuevo_estado = nuevo_estado.upper()

    if nuevo_estado in [choice[0] for choice in Cita.EstadoCita.choices]:
        cita.estado = nuevo_estado
        cita.save()
        registrar_log(request.user, 'EDITAR', 'Cita', f"Cambió estado de la cita del paciente '{cita.paciente.nombres} {cita.paciente.apellidos}' (Cédula: {cita.paciente.cedula}) a '{cita.get_estado_display()}'")
        messages.success(request, f"El estado de la cita de {cita.paciente.nombres} fue actualizado a '{cita.get_estado_display()}'.")
    else:
        messages.error(request, "Estado de cita inválido.")

    # Redirigimos de vuelta a la página anterior
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('listar_citas')


@rol_requerido('ADMINISTRADOR', 'RECEPCIONISTA')
def editar_cita(request, cita_id):
    """
    Vista para editar la fecha, médico o motivo de una cita programada.
    """
    cita = get_object_or_404(Cita, pk=cita_id)
    paciente = cita.paciente

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            registrar_log(request.user, 'EDITAR', 'Cita', f"Modificó cita del paciente '{paciente.nombres} {paciente.apellidos}' (Cédula: {paciente.cedula}) programada para el {cita.fecha_hora.strftime('%d/%m/%Y %I:%M %p')}")
            messages.success(request, f"Cita del paciente '{paciente.nombres} {paciente.apellidos}' modificada exitosamente.")
            return redirect('detalle_paciente', pk=paciente.pk)
        else:
            messages.error(request, "Error al actualizar la cita. Verifique los datos.")
    else:
        form = CitaForm(instance=cita)

    contexto = {
        'form': form,
        'cita': cita,
        'paciente': paciente,
    }
    return render(request, 'citas/editar_cita.html', contexto)


@rol_requerido('ADMINISTRADOR', 'RECEPCIONISTA')
def eliminar_cita(request, cita_id):
    """
    Vista para eliminar físicamente una cita programada del sistema.
    """
    cita = get_object_or_404(Cita, pk=cita_id)
    paciente = cita.paciente

    if request.method == 'POST':
        cita.delete()
        registrar_log(request.user, 'ELIMINAR', 'Cita', f"Eliminó cita del paciente '{paciente.nombres} {paciente.apellidos}' (Cédula: {paciente.cedula}) que estaba programada para el {cita.fecha_hora.strftime('%d/%m/%Y %I:%M %p')}")
        messages.success(request, f"Cita del paciente '{paciente.nombres} {paciente.apellidos}' eliminada de la agenda.")
        return redirect('detalle_paciente', pk=paciente.pk)

    contexto = {
        'titulo_accion': "Eliminar Cita Médica",
        'mensaje': f"¿Está seguro que desea cancelar y eliminar permanentemente la cita del paciente '{paciente.nombres} {paciente.apellidos}' programada para el {cita.fecha_hora.strftime('%d/%m/%Y %I:%M %p')}? Esta acción no se puede deshacer.",
        'url_cancelar': reverse('detalle_paciente', args=[paciente.pk])
    }
    return render(request, 'confirmar_eliminar.html', contexto)
