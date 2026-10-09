from django.conf import settings
from django.db import models

from sites_app.models import Site


class Equipment(models.Model):
    class Category(models.TextChoices):
        BTS = 'bts', 'BTS equipment'
        ANTENNA = 'antenna', 'Antenna'
        BATTERY = 'battery', 'Battery'
        GENERATOR = 'generator', 'Generator'
        RECTIFIER = 'rectifier', 'Rectifier'
        ROUTER = 'router', 'Router'
        SWITCH = 'switch', 'Switch'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        WORKING = 'working', 'Working'
        FAULTY = 'faulty', 'Faulty'
        UNDER_MAINTENANCE = 'under_maintenance', 'Under maintenance'

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name='equipment'
    )
    name = models.CharField(max_length=150)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OTHER
    )
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    installation_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.WORKING
    )
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='created_equipment',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['site__site_code', 'category', 'name']
        verbose_name_plural = 'equipment'

    def __str__(self):
        return f'{self.name} @ {self.site.site_code}'