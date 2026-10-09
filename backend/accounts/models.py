from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        TECHNICIAN = 'technician', 'Field technician'
        READ_ONLY = 'read_only', 'Read-only user'

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.READ_ONLY
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'