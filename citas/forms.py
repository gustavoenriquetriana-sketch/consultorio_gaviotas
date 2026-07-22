from django import forms
from django.contrib.auth import get_user_model
from .models import Cita

User = get_user_model()

class CitaForm(forms.ModelForm):
    """
    Formulario basado en modelo para la creación y agendamiento de citas médicas.
    Filtra los médicos para mostrar únicamente a los usuarios con rol 'MEDICO'.
    """
    medico = forms.ModelChoiceField(
        queryset=User.objects.filter(rol='MEDICO'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Médico Asignado",
        help_text="Seleccione el médico tratante para la consulta"
    )

    class Meta:
        model = Cita
        fields = ['fecha_hora', 'medico', 'motivo']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Consulta rutinaria, control anual, etc.'}),
        }
