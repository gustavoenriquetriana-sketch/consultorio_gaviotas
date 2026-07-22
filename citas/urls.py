from django.urls import path
from .views import agendar_cita, listar_citas, cambiar_estado_cita, editar_cita, eliminar_cita

urlpatterns = [
    path('nueva/<int:paciente_id>/', agendar_cita, name='agendar_cita'),
    path('agenda/', listar_citas, name='listar_citas'),
    path('estado/<int:cita_id>/<str:nuevo_estado>/', cambiar_estado_cita, name='cambiar_estado_cita'),
    path('<int:cita_id>/editar/', editar_cita, name='editar_cita'),
    path('<int:cita_id>/eliminar/', eliminar_cita, name='eliminar_cita'),
]
