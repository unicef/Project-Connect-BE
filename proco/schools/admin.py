from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from mapbox_location_field.admin import MapAdmin

from proco.locations.filters import CountryFilterList
from proco.schools.forms import ImportSchoolsCSVForm, SchoolAdminForm
from proco.schools.models import FileImport, School
from proco.schools.tasks import process_loaded_file
from proco.utils.admin import CountryNameDisplayAdminMixin


class ImportFormMixin(object):
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context['import_form'] = ImportSchoolsCSVForm()

        return super(ImportFormMixin, self).changelist_view(request, extra_context)


@admin.register(School)
class SchoolAdmin(ImportFormMixin, CountryNameDisplayAdminMixin, MapAdmin):
    form = SchoolAdminForm
    list_display = ('name', 'get_country_name', 'address', 'education_level', 'school_type','giga_id_school','education_level_regional')
    list_filter = (CountryFilterList, 'education_level', 'environment', 'school_type')
    search_fields = ('name', 'country__name', 'location__name')
    change_list_template = 'admin/schools/change_list.html'
    ordering = ('country', 'name')
    readonly_fields = ('get_weekly_stats_url',)
    raw_id_fields = ('country', 'location', 'last_weekly_status')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/csv/', self.import_csv, name='schools_school_import_csv'),
        ]
        return custom_urls + urls

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(country__in=request.user.countries_available.all())
        return qs.prefetch_related('country').defer('location')

    def import_csv(self, request):
        user = request.user
        if user.is_authenticated and user.has_perm('schools.add_fileimport') and request.method == 'POST':
            form = ImportSchoolsCSVForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                cleaned_data = form.clean()
                imported_file = FileImport.objects.create(
                    uploaded_file=cleaned_data['csv_file'], uploaded_by=request.user,
                )
                process_loaded_file.delay(imported_file.id, force=cleaned_data['force'])

                messages.success(request, 'Your file was uploaded and will be processed soon.')
                return redirect('admin:schools_fileimport_change', imported_file.id)

        raise PermissionDenied()

    def get_weekly_stats_url(self, obj):
        stats_url = reverse('admin:connection_statistics_schoolweeklystatus_changelist')
        return mark_safe(f'<a href="{stats_url}?school={obj.id}" target="_blank">Here</a>')  # noqa: S703,S308

    get_weekly_stats_url.short_description = 'Weekly Stats'


@admin.register(FileImport)
class FileImportAdmin(ImportFormMixin, admin.ModelAdmin):
    change_form_template = 'admin/schools/file_imports_change_form.html'

    list_display = ('id', 'country', 'uploaded_file', 'status', 'uploaded_by', 'modified')
    list_select_related = ('uploaded_by', 'country')
    list_filter = ('status',)
    readonly_fields = ('country', 'uploaded_file', 'status', 'statistic', 'errors', 'uploaded_by', 'modified')
    ordering = ('-id',)
    raw_id_fields = ('country',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(uploaded_by=request.user)
        return qs.defer('country__geometry')
