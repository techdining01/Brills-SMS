# school_sms/settings_model.py
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Single instance model to hold global application settings
class AppSetting(models.Model):
    # The PTA platform toggle
    pta_enabled = models.BooleanField(
        default=True, 
        verbose_name="Enable PTA Communication Platform",
        help_text="If unchecked, only Admins/Staff can see the center, and Parents cannot use the chat features."
    )

    class Meta:
        verbose_name = "Application Setting"
        verbose_name_plural = "Application Settings"

    # Restrict the model to a single instance
    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)

# Ensure one instance exists upon migration/creation
@receiver(post_save, sender=AppSetting)
def ensure_single_instance(sender, instance, **kwargs):
    if sender.objects.count() > 1:
        # Delete any extra instances, keeping the one just saved
        sender.objects.exclude(pk=instance.pk).delete()