from functools import wraps
from django.shortcuts import render, redirect
from django.conf import settings

def rol_requerido(*roles_permitidos):
    """
    Decorador para restringir el acceso a las vistas de acuerdo al rol de usuario
    definido en el sistema del C.A. Consultorio Médico Las Gaviotas.
    Verifica autenticación y roles, retornando una plantilla 403 personalizada en caso de restricción.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)
            
            # 2. Si el rol del usuario está en los permitidos o es Administrador, conceder acceso
            if request.user.rol == 'ADMINISTRADOR' or request.user.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            
            # 3. Acceso denegado: renderizar plantilla 403
            return render(request, '403.html', {
                'usuario': request.user,
                'rol_requerido': roles_permitidos
            }, status=403)
            
        return _wrapped_view
    return decorator
