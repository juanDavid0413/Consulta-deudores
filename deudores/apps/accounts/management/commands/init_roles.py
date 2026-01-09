from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Inicializa grupos y permisos del sistema"

    def handle(self, *args, **kwargs):
        admin_group, _ = Group.objects.get_or_create(name="admin")
        consultor_group, _ = Group.objects.get_or_create(name="consultor")

        can_upload = Permission.objects.get(codename="can_upload_excel")
        can_consult = Permission.objects.get(codename="can_consult_debtors")

        admin_group.permissions.set([can_upload, can_consult])
        consultor_group.permissions.set([can_consult])

        self.stdout.write(self.style.SUCCESS("Roles y permisos configurados correctamente"))
