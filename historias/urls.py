from django.urls import path
from .views import registrar_consulta, editar_consulta, eliminar_consulta

urlpatterns = [
    path('nueva/<int:paciente_id>/', registrar_consulta, name='registrar_consulta'),
    path('<int:historial_id>/editar/', editar_consulta, name='editar_consulta'),
    path('<int:historial_id>/eliminar/', eliminar_consulta, name='eliminar_consulta'),
]
