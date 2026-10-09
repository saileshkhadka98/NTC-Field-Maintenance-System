from rest_framework.routers import SimpleRouter

from .views import SitePhotoViewSet, SiteViewSet

router = SimpleRouter()
router.register('sites', SiteViewSet, basename='site')
router.register('site-photos', SitePhotoViewSet, basename='site-photo')

urlpatterns = router.urls