from django.utils import timezone
from rest_framework import serializers

from .models import Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    site_code = serializers.CharField(source='site.site_code', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)
    category_display = serializers.CharField(
        source='get_category_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Equipment
        fields = (
            'id', 'site', 'site_code', 'site_name', 'name',
            'category', 'category_display', 'manufacturer', 'model_number',
            'serial_number', 'quantity', 'installation_date',
            'status', 'status_display', 'notes', 'created_at', 'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be at least 1.')
        return value

    def validate_installation_date(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError(
                'Installation date cannot be in the future.'
            )
        return value