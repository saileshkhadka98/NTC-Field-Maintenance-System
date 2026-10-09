from rest_framework.routers import SimpleRouter

from .views import MaintenanceRecordViewSet

router = SimpleRouter()
router.register('maintenance', MaintenanceRecordViewSet, basename='maintenance')

urlpatterns = router.urls