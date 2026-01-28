from django.apps import AppConfig


class PayrollConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payroll'

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import PayrollRecord

        bursar, _ = Group.objects.get_or_create(name="Bursar")
        service_provider, _ = Group.objects.get_or_create(name="Bursar")

        content_type = ContentType.objects.get_for_model(PayrollRecord)
        perms = Permission.objects.filter(content_type=content_type)

        content_type = ContentType.objects.get_for_model(PayrollRecord)
        perms = Permission.objects.filter(content_type=content_type)

        bursar.permissions.set(perms)
        service_provider.permissions.set(perms)
