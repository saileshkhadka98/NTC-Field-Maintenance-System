from .image_utils import process_image
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Site(models.Model):
    class PowerSource(models.TextChoices):
        GRID = 'grid', 'Grid electricity'
        SOLAR = 'solar', 'Solar'
        GENERATOR = 'generator', 'Generator'
        HYBRID = 'hybrid', 'Hybrid (more than one)'

    # Identity
    site_code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255, blank=True)

    # Location (decimal degrees)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    directions_note = models.TextField(
        blank=True,
        help_text='How to reach the site, landmarks, who holds the key, etc.',
    )

    # Network technologies
    has_2g = models.BooleanField(default=False)
    has_3g = models.BooleanField(default=False)
    has_4g = models.BooleanField(default=False)
    has_5g = models.BooleanField(default=False)

    # Power and battery
    power_source = models.CharField(
        max_length=20, choices=PowerSource.choices, default=PowerSource.GRID
    )
    battery_type = models.CharField(max_length=60, blank=True)
    battery_count = models.PositiveIntegerField(null=True, blank=True)
    battery_capacity_ah = models.PositiveIntegerField(
        null=True, blank=True, help_text='Capacity per battery, in Ah'
    )

    # Bookkeeping
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='created_sites',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['site_code']

    def save(self, *args, **kwargs):
        self.site_code = self.site_code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.site_code} - {self.name}'


class SitePhoto(models.Model):
    class PhotoType(models.TextChoices):
        ACCESS_ROAD = 'access_road', 'Access road / approach'
        GATE = 'gate', 'Entrance / gate'
        SHELTER = 'shelter', 'Shelter / equipment room'
        TOWER = 'tower', 'Tower'
        SURROUNDINGS = 'surroundings', 'Surroundings / landmark'

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name='photos'
    )
    image = models.ImageField(upload_to='site_photos/%Y/%m/')
    thumbnail = models.ImageField(
        upload_to='site_photos/thumbs/%Y/%m/', blank=True, editable=False
    )
    photo_type = models.CharField(
        max_length=20, choices=PhotoType.choices, default=PhotoType.SURROUNDINGS
    )
    caption = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='uploaded_photos',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        # A newly uploaded file is resized and gets a thumbnail, whether it
        # came from the API or from the admin site.
        if self.image and not self.image._committed:
            full, thumb = process_image(self.image.file)
            self.image.save(full.name, full, save=False)
            self.thumbnail.save(thumb.name, thumb, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.site.site_code} - {self.get_photo_type_display()}'