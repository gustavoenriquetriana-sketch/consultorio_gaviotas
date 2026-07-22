from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    """
    Formulario basado en modelo (ModelForm) para el registro y gestión de Pacientes
    en el C.A. Consultorio Médico Las Gaviotas.
    """
    class Meta:
        model = Paciente
        fields = [
            'cedula',
            'nombres',
            'apellidos',
            'fecha_nacimiento',
            'sexo',
            'telefono',
            'direccion',
            'correo_electronico',
            'contacto_emergencia_nombre',
            'contacto_emergencia_telefono',
        ]
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V-12345678 o E-87654321'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres del paciente'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos del paciente'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0414-1234567'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa de habitación'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com (Opcional)'}),
            'contacto_emergencia_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del contacto de emergencia'}),
            'contacto_emergencia_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del contacto'}),
        }

    def clean_cedula(self):
        """
        Valida que el número de cédula sea único en el sistema.
        Si ya existe otro paciente registrado con la misma cédula, lanza un error de validación.
        """
        cedula = self.cleaned_data.get('cedula')
        # Filtramos excluyendo la instancia actual si ya posee un ID (por ejemplo, en edición futura)
        query = Paciente.objects.filter(cedula=cedula)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError("Ya existe un paciente registrado con esta cédula de identidad.")
        return cedula
