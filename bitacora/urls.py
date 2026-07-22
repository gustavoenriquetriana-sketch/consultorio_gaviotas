from django.urls import path
from .views import listar_logs, generar_respaldo

urlpatterns = [
    path('logs/', listar_logs, name='listar_logs'),
    path('respaldo/', generar_respaldo, name='generar_respaldo'),
]
