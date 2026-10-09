from rest_framework import filters, viewsets

from accounts.permissions import StaffWriteAdminDelete
from config.utils import int_param

from .models import Equipment
from .serializers import EquipmentSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentSerializer
    permission_classes = [StaffWriteAdminDelete]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'serial_number', 'model_number',
                     'manufacturer', 'site__site_code', 'site__name']
    ordering_fields = ['name', 'status', 'installation_date', 'created_at']

    def get_queryset(self):
        qs = Equipment.objects.select_related('site')
        params = self.request.query_params
        site_id = int_param(self.request, 'site')
        if site_id is not None:
            qs = qs.filter(site_id=site_id)
        if params.get('category'):
            qs = qs.filter(category=params['category'])
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)