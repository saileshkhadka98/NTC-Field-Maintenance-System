from django.contrib import admin

from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'category', 'manufacturer',
                    'model_number', 'quantity', 'status')
    search_fields = ('name', 'serial_number', 'model_number',
                     'manufacturer', 'site__site_code', 'site__name')
    list_filter = ('category', 'status')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)