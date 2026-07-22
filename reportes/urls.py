from django.urls import path
from .views import menu_reportes, reporte_pacientes, reporte_consultas, reporte_citas

urlpatterns = [
    path('', menu_reportes, name='menu_reportes'),
    path('pacientes/', reporte_pacientes, name='reporte_pacientes'),
    path('consultas/', reporte_consultas, name='reporte_consultas'),
    path('citas/', reporte_citas, name='reporte_citas'),
]
