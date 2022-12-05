from django.contrib import admin, messages
from django.contrib.gis.admin import GeoModelAdmin
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from proco.background.models import BackgroundTask
from proco.background.tasks import reset_countries_data, validate_countries
from proco.locations.filters import CountryFilterList
from proco.locations.models import Country, Location
from proco.utils.admin import CountryNameDisplayAdminMixin


@admin.register(Country)
class CountryAdmin(GeoModelAdmin):
    modifiable = False

    list_display = ('name', 'code', 'flag_preview')
    search_fields = ('name',)
    exclude = ('geometry', 'geometry_simplified')
    raw_id_fields = ('last_weekly_status',)
    actions = ('update_country_status_to_joined', 'clearing_all_data')

    def flag_preview(self, obj):
        if not obj.flag:
            return ''
        return mark_safe(f'<img src="{obj.flag.url}" style="max-width:50px; max-height:50px;" />')  # noqa: S703,S308

    flag_preview.short_description = 'Flag'

    def get_queryset(self, request):
        return super().get_queryset(request).defer('geometry', 'geometry_simplified')

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mark-as-joined/', self.update_country_status_to_joined, name='update_country_status_to_joined'),
            path('delete-schools-and-statistics/', self.clearing_all_data, name='delete-schools-and-statistics'),
        ]
        return custom_urls + urls

    @staticmethod
    def check_access(request, queryset):
        access = True if request.user.is_superuser else False
        if not access:
            countries_available = request.user.countries_available.values('id')
            qs_not_available = queryset.exclude(id__in=countries_available)
            result = (False, qs_not_available) if not qs_not_available.exists() else (True, None)
        else:
            result = True, None
        return result

    def update_country_status_to_joined(self, request, queryset=None):
        access, qs_not_available = self.check_access(request, queryset)

        if not access:
            message = f'You do not have access to change countries: ' \
                      f'{", ".join(qs_not_available.values_list("name", flat=True))}'
            level = messages.ERROR
            self.message_user(request, message, level=level)
            return HttpResponseRedirect(reverse('admin:locations_country_changelist'))

        else:
            if request.method == 'POST' and 'post' in request.POST:
                objects = request.POST.get('post')
                task = validate_countries.apply_async((objects.split(','),), countdown=2)
                BackgroundTask.objects.get_or_create(task_id=task.id)
                message = 'Countries validation started. Please wait.'
                level = messages.INFO
                self.message_user(request, message, level=level)
                return HttpResponseRedirect(reverse('admin:background_backgroundtask_change', args=[task.id]))
            else:
                objects = ','.join(str(i) for i in queryset.values_list('id', flat=True))
                context = {'opts': self.model._meta, 'objects': objects, 'action': 'mark_as_joined'}
                return TemplateResponse(request, 'admin/locations/action_confirm.html', context)

    update_country_status_to_joined.short_description = 'Mark country data source as verified (non-OSM)'

    @transaction.atomic
    def clearing_all_data(self, request, queryset=None):
        access, qs_not_available = self.check_access(request, queryset)
        if not access:
            message = f'You do not have access to change countries: ' \
                      f'{", ".join(qs_not_available.values_list("name", flat=True))}'
            level = messages.ERROR
            self.message_user(request, message, level=level)
            return HttpResponseRedirect(reverse('admin:locations_country_changelist'))

        else:
            if request.method == 'POST' and 'post' in request.POST:
                objects = request.POST.get('post')
                task = reset_countries_data.apply_async((objects.split(','),), countdown=2)
                BackgroundTask.objects.get_or_create(task_id=task.id)
                message = 'Country data clearing started. Please wait.'
                level = messages.INFO
                self.message_user(request, message, level=level)
                return HttpResponseRedirect(reverse('admin:background_backgroundtask_change', args=[task.id]))
            else:
                objects = ','.join(str(i) for i in queryset.values_list('id', flat=True))
                context = {'opts': self.model._meta, 'objects': objects, 'action': 'delete_schools_and_statistics'}
                return TemplateResponse(request, 'admin/locations/action_confirm.html', context)

    clearing_all_data.short_description = 'Delete school points & saved statistics'


@admin.register(Location)
class LocationAdmin(CountryNameDisplayAdminMixin, GeoModelAdmin):
    modifiable = False
    show_full_result_count = False

    list_display = ('name', 'get_country_name')
    list_filter = (CountryFilterList,)
    search_fields = ('name', 'country__name')
    exclude = ('geometry_simplified',)
    raw_id_fields = ('parent', 'country')
    ordering = ('id',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch('country', Country.objects.defer('geometry', 'geometry_simplified')),
        )
