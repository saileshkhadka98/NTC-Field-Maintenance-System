from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .dashboard import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/dashboard/', DashboardView.as_view()),
    path('api/', include('sites_app.urls')),
    path('api/', include('equipment.urls')),
    path('api/', include('maintenance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)