from django.db.models import Count, ProtectedError
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from accounts.permissions import AdminWriteElseRead

from .models import Site
from .serializers import SiteSerializer


class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    permission_classes = [AdminWriteElseRead]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['site_code', 'name', 'address']
    ordering_fields = ['site_code', 'name', 'created_at']

    def get_queryset(self):
        qs = (
            Site.objects
            .prefetch_related('photos', 'maintenance_records__technician')
            .annotate(equipment_count=Count('equipment', distinct=True))
        )
        params = self.request.query_params
        for tech in ('2g', '3g', '4g', '5g'):
            if params.get(f'has_{tech}') in ('true', '1'):
                qs = qs.filter(**{f'has_{tech}': True})
        if params.get('power_source'):
            qs = qs.filter(power_source=params['power_source'])
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'This site has maintenance records and cannot be deleted.'},
                status=status.HTTP_409_CONFLICT,
            )