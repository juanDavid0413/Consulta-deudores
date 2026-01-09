from django.db import models

# Create your models here.
class Meta:
    permissions = [
        ("can_upload_excel", "Puede cargar archivos Excel"),
        ("can_consult_debtors", "Puede consultar deudores"),
    ]
