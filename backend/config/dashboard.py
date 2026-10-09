from django.db.models import Count, OuterRef, Q, Subquery
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from equipment.models import Equipment
from equipment.serializers import EquipmentSerializer
from maintenance.models import MaintenanceRecord
from maintenance.serializers import MaintenanceRecordSerializer
from sites_app.models import Site

RECENT_LIMIT = 5
ATTENTION_LIMIT = 10
OVERDUE_LIMIT = 10


class DashboardView(APIView):
    """Live summary figures. Any logged-in user can read it."""

    def get(self, request):
        today = timezone.localdate()

        # Each site's most recent maintenance record
        latest = (
            MaintenanceRecord.objects
            .filter(site=OuterRef('pk'))
            .order_by('-maintenance_date', '-created_at')
        )
        sites = Site.objects.annotate(
            last_date=Subquery(latest.values('maintenance_date')[:1]),
            last_due=Subquery(latest.values('next_due_date')[:1]),
        )

        # Overdue = the latest record's "next due" date has passed
        overdue_qs = sites.filter(last_due__lt=today).order_by('last_due')
        overdue_items = [
            {
                'id': s.id,
                'site_code': s.site_code,
                'name': s.name,
                'last_maintenance_date': s.last_date,
                'next_due_date': s.last_due,
                'days_overdue': (today - s.last_due).days,
            }
            for s in overdue_qs[:OVERDUE_LIMIT]
        ]

        equipment_stats = Equipment.objects.aggregate(
            total=Count('id'),
            faulty=Count('id', filter=Q(status=Equipment.Status.FAULTY)),
            under_maintenance=Count(
                'id', filter=Q(status=Equipment.Status.UNDER_MAINTENANCE)
            ),
        )
        tech_stats = Site.objects.aggregate(
            g2=Count('id', filter=Q(has_2g=True)),
            g3=Count('id', filter=Q(has_3g=True)),
            g4=Count('id', filter=Q(has_4g=True)),
            g5=Count('id', filter=Q(has_5g=True)),
        )

        recent = MaintenanceRecord.objects.select_related(
            'site', 'technician'
        )[:RECENT_LIMIT]
        attention = (
            Equipment.objects
            .select_related('site')
            .filter(status__in=[
                Equipment.Status.FAULTY, Equipment.Status.UNDER_MAINTENANCE,
            ])
            .order_by('status', '-updated_at')[:ATTENTION_LIMIT]
        )

        return Response({
            'totals': {
                'sites': Site.objects.count(),
                'equipment': equipment_stats['total'],
                'maintenance_records': MaintenanceRecord.objects.count(),
                'faulty_equipment': equipment_stats['faulty'],
                'under_maintenance_equipment': equipment_stats['under_maintenance'],
            },
            'technologies': {
                '2g': tech_stats['g2'], '3g': tech_stats['g3'],
                '4g': tech_stats['g4'], '5g': tech_stats['g5'],
            },
            'recent_maintenance': MaintenanceRecordSerializer(
                recent, many=True
            ).data,
            'attention_equipment': EquipmentSerializer(
                attention, many=True
            ).data,
            'overdue_sites': {
                'count': overdue_qs.count(),
                'items': overdue_items,
            },
            'never_maintained_sites': sites.filter(
                last_date__isnull=True
            ).count(),
        })