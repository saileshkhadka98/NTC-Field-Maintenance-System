from django.contrib import admin

from .models import MaintenanceRecord


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('site', 'maintenance_date', 'maintenance_type',
                    'technician', 'next_due_date')
    search_fields = ('site__site_code', 'site__name', 'description',
                     'technician__username')
    list_filter = ('maintenance_type', 'maintenance_date')
    date_hierarchy = 'maintenance_date'

    def save_model(self, request, obj, form, change):
        if not change and not obj.technician:
            obj.technician = request.user
        super().save_model(request, obj, form, change)