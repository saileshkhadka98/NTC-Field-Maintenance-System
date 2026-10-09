from django.utils import timezone
from rest_framework import serializers

from .models import MaintenanceRecord


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    site_code = serializers.CharField(source='site.site_code', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)
    type_display = serializers.CharField(
        source='get_maintenance_type_display', read_only=True
    )
    technician_name = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRecord
        fields = (
            'id', 'site', 'site_code', 'site_name',
            'technician_name', 'maintenance_date',
            'maintenance_type', 'type_display', 'description',
            'next_due_date', 'created_at',
        )
        read_only_fields = ('created_at',)

    def get_technician_name(self, obj):
        return obj.technician.username if obj.technician else None

    def validate(self, attrs):
        date = attrs.get(
            'maintenance_date', getattr(self.instance, 'maintenance_date', None)
        )
        due = attrs.get(
            'next_due_date', getattr(self.instance, 'next_due_date', None)
        )
        errors = {}
        if date and date > timezone.localdate():
            errors['maintenance_date'] = 'Maintenance date cannot be in the future.'
        if date and due and due < date:
            errors['next_due_date'] = (
                'Next due date cannot be before the maintenance date.'
            )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs