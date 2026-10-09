from rest_framework import filters, viewsets

from accounts.permissions import StaffCreateAdminModify
from config.utils import date_param, int_param

from .models import MaintenanceRecord
from .serializers import MaintenanceRecordSerializer


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [StaffCreateAdminModify]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['site__site_code', 'site__name', 'description',
                     'technician__username']
    ordering_fields = ['maintenance_date', 'created_at']

    def get_queryset(self):
        qs = MaintenanceRecord.objects.select_related('site', 'technician')
        params = self.request.query_params

        site_id = int_param(self.request, 'site')
        if site_id is not None:
            qs = qs.filter(site_id=site_id)
        if params.get('maintenance_type'):
            qs = qs.filter(maintenance_type=params['maintenance_type'])

        date_from = date_param(self.request, 'date_from')
        if date_from:
            qs = qs.filter(maintenance_date__gte=date_from)
        date_to = date_param(self.request, 'date_to')
        if date_to:
            qs = qs.filter(maintenance_date__lte=date_to)
        return qs

    def perform_create(self, serializer):
        serializer.save(technician=self.request.user)