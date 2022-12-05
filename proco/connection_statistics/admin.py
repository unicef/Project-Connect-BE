from django.contrib import admin

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.locations.filters import CountryFilterList, SchoolCountryFilterList
from proco.utils.admin import CountryNameDisplayAdminMixin, SchoolNameDisplayAdminMixin


@admin.register(CountryWeeklyStatus)
class CountryWeeklyStatusAdmin(CountryNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_country_name', 'year', 'week', 'integration_status', 'connectivity_speed', 'schools_total',
                    'schools_connected', 'schools_connectivity_unknown', 'schools_connectivity_no',
                    'schools_connectivity_moderate', 'schools_connectivity_good')
    list_filter = ('integration_status', CountryFilterList)
    list_select_related = ('country',)
    search_fields = ('country__name', 'year', 'week')
    ordering = ('-id',)
    readonly_fields = ('year', 'week', 'integration_status')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(country__in=request.user.countries_available.all())
        return qs.defer(
            'country__geometry',
            'country__geometry_simplified',
        )

    def has_change_permission(self, request, obj=None):
        perm = super().has_change_permission(request, obj)
        if not request.user.is_superuser and obj:
            perm = obj.country in request.user.countries_available.all()
        return perm


@admin.register(SchoolWeeklyStatus)
class SchoolWeeklyStatusAdmin(SchoolNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_school_name', 'year', 'week', 'connectivity_speed',
                    'connectivity_latency', 'num_students', 'num_teachers')
    list_filter = (SchoolCountryFilterList,)
    list_select_related = ('school',)
    search_fields = ('school__name', 'year', 'week')
    ordering = ('-id',)
    readonly_fields = ('year', 'week')
    raw_id_fields = ('school',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(school__country__in=request.user.countries_available.all())
        return qs


@admin.register(CountryDailyStatus)
class CountryDailyStatusAdmin(CountryNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_country_name', 'date', 'connectivity_speed', 'connectivity_latency')
    list_select_related = ('country',)
    list_filter = (CountryFilterList,)
    search_fields = ('country__name',)
    ordering = ('-id',)
    date_hierarchy = 'date'
    raw_id_fields = ('country',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(country__in=request.user.countries_available.all())
        return qs.defer(
            'country__geometry',
            'country__geometry_simplified',
        )


@admin.register(SchoolDailyStatus)
class SchoolDailyStatusAdmin(SchoolNameDisplayAdminMixin, admin.ModelAdmin):
    list_display = ('get_school_name', 'date', 'connectivity_speed', 'connectivity_latency')
    list_select_related = ('school',)
    search_fields = ('school__name',)
    list_filter = (SchoolCountryFilterList,)
    ordering = ('-id',)
    raw_id_fields = ('school',)
    show_full_result_count = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(school__country__in=request.user.countries_available.all())
        return qs


@admin.register(RealTimeConnectivity)
class RealTimeConnectivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'connectivity_speed', 'connectivity_latency')
    ordering = ('-id',)
    readonly_fields = ('school', 'created', 'modified')
    show_full_result_count = False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True
