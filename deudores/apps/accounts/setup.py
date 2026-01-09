from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.utils import OperationalError, ProgrammingError
from django.contrib.auth import get_user_model


def setup_roles():
    """
    Crea grupos y permisos de negocio de forma segura.
    """
    try:
        User = get_user_model()
        content_type = ContentType.objects.get_for_model(User)

        # =========================
        # PERMISOS DE NEGOCIO
        # =========================
        can_upload_excel, _ = Permission.objects.get_or_create(
            codename='can_upload_excel',
            name='Puede cargar archivos Excel',
            content_type=content_type,
        )

        can_consult_debtors, _ = Permission.objects.get_or_create(
            codename='can_consult_debtors',
            name='Puede consultar deudores',
            content_type=content_type,
        )

        # =========================
        # GRUPOS
        # =========================
        admin_group, _ = Group.objects.get_or_create(name='admin')
        consultor_group, _ = Group.objects.get_or_create(name='consultor')

        # =========================
        # ASIGNACIÓN DE PERMISOS
        # =========================

        # Admin: todo
        admin_group.permissions.add(
            can_upload_excel,
            can_consult_debtors,
            Permission.objects.get(codename='add_user'),
            Permission.objects.get(codename='view_user'),
        )

        # Consultor: solo consulta
        consultor_group.permissions.add(
            can_consult_debtors,
        )

    except (OperationalError, ProgrammingError):
        # Evita errores antes de migraciones
        pass
