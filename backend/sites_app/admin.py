from django.contrib import admin

from .models import Site, SitePhoto


class SitePhotoInline(admin.TabularInline):
    model = SitePhoto
    extra = 1
    fields = ('image', 'photo_type', 'caption')


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('site_code', 'name', 'latitude', 'longitude',
                    'power_source', 'has_2g', 'has_3g', 'has_4g', 'has_5g')
    search_fields = ('site_code', 'name', 'address')
    list_filter = ('power_source', 'has_4g', 'has_5g')
    inlines = [SitePhotoInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, SitePhoto) and not obj.uploaded_by:
                obj.uploaded_by = request.user
            obj.save()
        formset.save_m2m()


admin.site.register(SitePhoto)