from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from usuarios.decorators import rol_requerido
from bitacora.utils import registrar_log
from pacientes.models import Paciente
from .models import HistorialClinico, Receta
from .forms import HistorialClinicoForm, RecetaForm

@rol_requerido('ADMINISTRADOR', 'MEDICO')
def registrar_consulta(request, paciente_id):
    """
    Vista para registrar una nueva consulta médica (Historial Clínico)
    y opcionalmente una receta vinculada para un paciente específico.
    """
    paciente = get_object_or_404(Paciente, pk=paciente_id)

    if request.method == 'POST':
        consulta_form = HistorialClinicoForm(request.POST)
        receta_form = RecetaForm(request.POST)

        if consulta_form.is_valid():
            # Guardamos la consulta médica sin confirmación de base de datos para asignar campos automáticos
            consulta = consulta_form.save(commit=False)
            consulta.paciente = paciente
            consulta.medico = request.user
            consulta.save()

            # Verificamos si se ingresaron indicaciones en la receta para guardarla
            indicaciones = request.POST.get('indicaciones_medicamentos', '').strip()
            if indicaciones:
                if receta_form.is_valid():
                    receta = receta_form.save(commit=False)
                    receta.historial_clinico = consulta
                    receta.save()
                else:
                    # En caso de error en receta (aunque sean opcionales, para robustez)
                    messages.warning(request, "La consulta fue guardada, pero la receta médica contenía errores y no pudo registrarse.")
            
            messages.success(request, f"Consulta médica de '{paciente.nombres} {paciente.apellidos}' registrada exitosamente.")
            registrar_log(request.user, 'CREAR', 'HistorialClinico', f"Registró consulta médica para {paciente.nombres} {paciente.apellidos} (Cédula: {paciente.cedula})")
            return redirect('detalle_paciente', pk=paciente.pk)
        else:
            messages.error(request, "Error al registrar la consulta. Por favor, verifique los datos.")
    else:
        consulta_form = HistorialClinicoForm()
        receta_form = RecetaForm()

    contexto = {
        'paciente': paciente,
        'consulta_form': consulta_form,
        'receta_form': receta_form,
    }
    return render(request, 'historias/registrar_consulta.html', contexto)


@rol_requerido('ADMINISTRADOR', 'MEDICO')
def editar_consulta(request, historial_id):
    """
    Vista para editar una consulta médica (Historial Clínico) existente
    y su receta médica asociada (si existe o es creada en esta edición).
    """
    consulta = get_object_or_404(HistorialClinico, pk=historial_id)
    paciente = consulta.paciente
    
    # Intentamos obtener la receta vinculada (OneToOne)
    try:
        receta = consulta.receta
    except Receta.DoesNotExist:
        receta = None

    if request.method == 'POST':
        consulta_form = HistorialClinicoForm(request.POST, instance=consulta)
        receta_form = RecetaForm(request.POST, instance=receta) if receta else RecetaForm(request.POST)

        if consulta_form.is_valid():
            consulta_form.save()
            
            indicaciones = request.POST.get('indicaciones_medicamentos', '').strip()
            
            if indicaciones:
                if receta_form.is_valid():
                    nueva_receta = receta_form.save(commit=False)
                    nueva_receta.historial_clinico = consulta
                    nueva_receta.save()
                else:
                    messages.warning(request, "La consulta se actualizó, pero la receta médica no pudo ser guardada debido a errores.")
            else:
                # Si se borraron las indicaciones de una receta existente, la eliminamos físicamente
                if receta:
                    receta.delete()

            messages.success(request, f"Consulta de '{paciente.nombres} {paciente.apellidos}' modificada exitosamente.")
            registrar_log(request.user, 'EDITAR', 'HistorialClinico', f"Modificó consulta médica del paciente {paciente.nombres} {paciente.apellidos} (Cédula: {paciente.cedula})")
            return redirect('detalle_paciente', pk=paciente.pk)
        else:
            messages.error(request, "Error de validación. Compruebe los campos clínicos.")
    else:
        consulta_form = HistorialClinicoForm(instance=consulta)
        receta_form = RecetaForm(instance=receta) if receta else RecetaForm()

    contexto = {
        'paciente': paciente,
        'consulta': consulta,
        'consulta_form': consulta_form,
        'receta_form': receta_form,
    }
    return render(request, 'historias/editar_consulta.html', contexto)


@rol_requerido('ADMINISTRADOR')
def eliminar_consulta(request, historial_id):
    """
    Vista para eliminar físicamente una consulta médica del sistema.
    Muestra una pantalla de confirmación y elimina la consulta (y su receta en cascada) vía POST.
    """
    consulta = get_object_or_404(HistorialClinico, pk=historial_id)
    paciente = consulta.paciente

    if request.method == 'POST':
        consulta.delete()
        registrar_log(request.user, 'ELIMINAR', 'HistorialClinico', f"Eliminó físicamente la consulta del paciente {paciente.nombres} {paciente.apellidos} (Cédula: {paciente.cedula})")
        messages.success(request, f"Consulta médica del paciente '{paciente.nombres} {paciente.apellidos}' eliminada permanentemente.")
        return redirect('detalle_paciente', pk=paciente.pk)

    contexto = {
        'titulo_accion': "Eliminar Consulta Médica",
        'mensaje': f"¿Está seguro que desea eliminar permanentemente esta consulta médica del paciente '{paciente.nombres} {paciente.apellidos}' realizada el {consulta.fecha_consulta.strftime('%d/%m/%Y')}? Esta acción no se puede deshacer y borrará también la receta asociada.",
        'url_cancelar': reverse('detalle_paciente', args=[paciente.pk])
    }
    return render(request, 'confirmar_eliminar.html', contexto)
