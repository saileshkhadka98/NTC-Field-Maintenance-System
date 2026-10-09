from .image_utils import validate_upload
from decimal import Decimal

from rest_framework import serializers

from .models import Site, SitePhoto

# Rough bounding box of Nepal
NEPAL_LAT = (Decimal('26.3'), Decimal('30.5'))
NEPAL_LON = (Decimal('80.0'), Decimal('88.3'))


class SitePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitePhoto
        fields = ('id', 'site', 'image', 'thumbnail', 'photo_type',
                  'caption', 'uploaded_at')
        read_only_fields = ('thumbnail', 'uploaded_at')

    def validate_image(self, value):
        return validate_upload(value)


class SiteSerializer(serializers.ModelSerializer):
    photos = SitePhotoSerializer(many=True, read_only=True)
    latest_maintenance = serializers.SerializerMethodField()
    navigation_url = serializers.SerializerMethodField()
    equipment_count = serializers.IntegerField(read_only=True)
    confirm_outside_nepal = serializers.BooleanField(
        write_only=True, required=False, default=False
    )

    class Meta:
        model = Site
        fields = (
            'id', 'site_code', 'name', 'address',
            'latitude', 'longitude', 'directions_note', 'navigation_url',
            'has_2g', 'has_3g', 'has_4g', 'has_5g',
            'power_source', 'battery_type', 'battery_count',
            'battery_capacity_ah',
            'photos', 'latest_maintenance', 'equipment_count',
            'confirm_outside_nepal', 'created_at', 'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_navigation_url(self, obj):
        return (
            'https://www.google.com/maps/dir/?api=1&destination='
            f'{obj.latitude},{obj.longitude}'
        )

    def get_latest_maintenance(self, obj):
        records = list(obj.maintenance_records.all())  # newest first
        if not records:
            return None
        rec = records[0]
        return {
            'id': rec.id,
            'date': rec.maintenance_date,
            'type': rec.get_maintenance_type_display(),
            'technician': rec.technician.username if rec.technician else None,
            'description': rec.description,
        }

    def validate_site_code(self, value):
        value = value.strip().upper()
        qs = Site.objects.filter(site_code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'A site with this code already exists.'
            )
        return value

    def validate(self, attrs):
        confirm = attrs.pop('confirm_outside_nepal', False)
        lat = attrs.get('latitude', getattr(self.instance, 'latitude', None))
        lon = attrs.get('longitude', getattr(self.instance, 'longitude', None))
        if lat is not None and lon is not None:
            inside = (NEPAL_LAT[0] <= lat <= NEPAL_LAT[1]
                      and NEPAL_LON[0] <= lon <= NEPAL_LON[1])
            if not inside and not confirm:
                raise serializers.ValidationError({
                    'coordinates': (
                        'These coordinates look outside Nepal. Check that '
                        'latitude and longitude are not swapped. To save '
                        'anyway, send confirm_outside_nepal=true.'
                    )
                })
        return attrs