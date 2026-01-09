from django import forms

class UploadExcelForm(forms.Form):
    sheet = forms.ChoiceField(
        choices=(
            ('BD_FACTURACION', 'BD FACTURACIÓN'),
            ('BD2', 'BD2'),
            ('BD3', 'BD3'),
        )
    )
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError("Solo se permiten archivos .xlsx")
        return file
