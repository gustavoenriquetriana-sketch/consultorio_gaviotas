from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from pacientes.models import Paciente
from historias.models import HistorialClinico
from citas.models import Cita

class CustomLoginView(LoginView):
    """
    Vista personalizada para el Inicio de Sesión del personal del consultorio.
    Utiliza el sistema de autenticación nativo de Django.
    """
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return '/dashboard/'


@login_required
def dashboard_view(request):
    """
    Vista del Panel de Control (Dashboard) después del inicio de sesión.
    Saluda al usuario y muestra información, opciones de acceso rápido y estadísticas
    calculadas dinámicamente de la base de datos según su rol.
    """
    usuario = request.user
    
    # Calcular estadísticas dinámicas para el Administrador o Personal de salud
    hoy = timezone.localtime(timezone.now()).date()
    inicio_mes = timezone.localtime(timezone.now()).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    total_pacientes = Paciente.objects.filter(activo=True).count()
    citas_pendientes = Cita.objects.filter(estado='PENDIENTE', fecha_hora__date__gte=hoy).count()
    consultas_mes = HistorialClinico.objects.filter(fecha_consulta__gte=inicio_mes).count()
    
    # Obtener las citas programadas para el día de hoy
    citas_hoy = Cita.objects.filter(fecha_hora__date=hoy).select_related('paciente', 'medico').order_by('fecha_hora')
    
    contexto = {
        'usuario': usuario,
        'rol_nombre': usuario.get_rol_display(),
        'stat_pacientes': total_pacientes,
        'stat_citas': citas_pendientes,
        'stat_consultas': consultas_mes,
        'citas_hoy': citas_hoy,
    }
    return render(request, 'usuarios/dashboard.html', contexto)


def custom_logout_view(request):
    """
    Vista para cerrar la sesión del usuario y redirigir al login.
    """
    logout(request)
    return redirect('login')
