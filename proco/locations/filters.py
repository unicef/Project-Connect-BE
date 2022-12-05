from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from proco.locations.models import Country


class CountryFilterList(SimpleListFilter):
    title = _('Country')
    parameter_name = 'country_id'

    def lookups(self, request, model_admin):
        return Country.objects.defer('geometry', 'geometry_simplified').values_list('id', 'name')

    def queryset(self, request, queryset):
        return queryset.filter(**{self.parameter_name: self.value()}) if self.value() else queryset


class SchoolCountryFilterList(CountryFilterList):
    parameter_name = 'school__country_id'
