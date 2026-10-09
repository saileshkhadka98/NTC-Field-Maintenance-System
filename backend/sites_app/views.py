from django.db.models import Count, ProtectedError
from rest_framework import filters, mixins, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from accounts.permissions import AdminWriteElseRead, StaffWriteAdminDelete
from config.utils import int_param

from .models import Site, SitePhoto
from .serializers import SitePhotoSerializer, SiteSerializer


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


class SitePhotoViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SitePhotoSerializer
    permission_classes = [StaffWriteAdminDelete]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = SitePhoto.objects.select_related('site')
        site_id = int_param(self.request, 'site')
        if site_id is not None:
            qs = qs.filter(site_id=site_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)