from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from sites_app.models import Site


class MaintenanceRecord(models.Model):
    class MaintenanceType(models.TextChoices):
        ROUTINE = 'routine', 'Routine inspection'
        PREVENTIVE = 'preventive', 'Preventive maintenance'
        CORRECTIVE = 'corrective', 'Corrective maintenance'
        REPAIR = 'repair', 'Equipment repair'
        BATTERY = 'battery', 'Battery maintenance'
        POWER = 'power', 'Power maintenance'

    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, related_name='maintenance_records'
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='maintenance_records',
    )
    maintenance_date = models.DateField()
    maintenance_type = models.CharField(
        max_length=20, choices=MaintenanceType.choices,
        default=MaintenanceType.ROUTINE,
    )
    description = models.TextField(help_text='Work performed')
    next_due_date = models.DateField(
        null=True, blank=True, help_text='Optional: when the next visit is due'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-maintenance_date', '-created_at']

    def clean(self):
        if self.maintenance_date and self.maintenance_date > timezone.localdate():
            raise ValidationError(
                {'maintenance_date': 'Maintenance date cannot be in the future.'}
            )
        if (self.next_due_date and self.maintenance_date
                and self.next_due_date < self.maintenance_date):
            raise ValidationError(
                {'next_due_date': 'Next due date cannot be before the maintenance date.'}
            )

    def __str__(self):
        return f'{self.site.site_code} - {self.maintenance_date} ({self.get_maintenance_type_display()})'