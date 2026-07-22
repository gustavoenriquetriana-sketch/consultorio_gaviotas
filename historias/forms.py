from django import forms
from .models import HistorialClinico, Receta

class HistorialClinicoForm(forms.ModelForm):
    """
    Formulario basado en modelo para registrar una nueva consulta médica (Historial Clínico)
    en el C.A. Consultorio Médico Las Gaviotas.
    Excluye paciente y médico, los cuales se asignan automáticamente en la vista.
    """
    class Meta:
        model = HistorialClinico
        fields = ['motivo_consulta', 'antecedentes', 'diagnostico', 'notas_observaciones']
        widgets = {
            'motivo_consulta': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Describa el motivo de la consulta del paciente...'
            }),
            'antecedentes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Antecedentes médicos patológicos o personales relevantes...'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Ingrese el diagnóstico médico final...'
            }),
            'notas_observaciones': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Notas u observaciones adicionales sobre el tratamiento o evolución...'
            }),
        }


class RecetaForm(forms.ModelForm):
    """
    Formulario basado en modelo para la prescripción de una receta médica.
    Se marca como opcional de forma que pueda guardarse en blanco si no se receta medicación.
    """
    # Sobrescribimos el campo para que no sea obligatorio en la validación del formulario
    indicaciones_medicamentos = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'Escriba los medicamentos, dosis e indicaciones de administración...'
        }),
        label="Indicaciones y Medicamentos"
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2, 
            'placeholder': 'Recomendaciones adicionales (ej: reposo, control en 7 días)...'
        }),
        label="Observaciones de la Receta"
    )

    class Meta:
        model = Receta
        fields = ['indicaciones_medicamentos', 'observaciones']
