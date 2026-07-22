from django.urls import path
from .views import buscar_pacientes, detalle_paciente, registrar_paciente, editar_paciente, desactivar_paciente

urlpatterns = [
    path('buscar/', buscar_pacientes, name='buscar_pacientes'),
    path('nuevo/', registrar_paciente, name='registrar_paciente'),
    path('<int:pk>/', detalle_paciente, name='detalle_paciente'),
    path('<int:paciente_id>/editar/', editar_paciente, name='editar_paciente'),
    path('<int:paciente_id>/desactivar/', desactivar_paciente, name='desactivar_paciente'),
]
