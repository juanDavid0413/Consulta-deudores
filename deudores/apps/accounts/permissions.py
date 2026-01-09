from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def create_custom_permissions():
    from uploads.models import SheetUploadLog

    content_type = ContentType.objects.get_for_model(SheetUploadLog)

    Permission.objects.get_or_create(
        codename='can_upload_excel',
        name='Puede cargar archivos Excel',
        content_type=content_type,
    )

    Permission.objects.get_or_create(
        codename='can_consult_debtors',
        name='Puede consultar deudores',
        content_type=content_type,
    )

