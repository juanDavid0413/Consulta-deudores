from django import forms


class ConsultaCedulaForm(forms.Form):
    cedula = forms.CharField(
        label="Número de cédula",
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese la cédula del cliente"
        })
    )

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"].strip()
        if not cedula:
            raise forms.ValidationError("La cédula es obligatoria.")
        return cedula
