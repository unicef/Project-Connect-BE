from django.conf import settings
from django.db.models.functions.text import Lower
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView

from django_filters.rest_framework import DjangoFilterBackend

from proco.locations.backends.csv import SchoolsCSVWriterBackend
from proco.locations.models import Country
from proco.schools.models import School
from proco.schools.serializers import (
    CSVSchoolsListSerializer,
    ListSchoolSerializer,
    SchoolPointSerializer,
    SchoolSerializer,
)
from proco.utils.mixins import CachedListMixin


@method_decorator([cache_control(public=True, max_age=settings.CACHE_CONTROL_MAX_AGE)], name='dispatch')
class SchoolsViewSet(
    CachedListMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    LIST_CACHE_KEY_PREFIX = 'SCHOOLS'

    queryset = School.objects.all().select_related('last_weekly_status')
    pagination_class = None
    serializer_class = SchoolSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    related_model = Country

    def get_serializer(self, *args, **kwargs):
        kwargs['country'] = self.get_country()
        return super(SchoolsViewSet, self).get_serializer(*args, **kwargs)

    def get_list_cache_key(self):
        params = dict(self.request.query_params)
        params.pop(self.CACHE_KEY, None)
        return '{0}_{1}_{2}'.format(
            getattr(self.__class__, 'LIST_CACHE_KEY_PREFIX', self.__class__.__name__) or self.__class__.__name__,
            self.kwargs['country_code'].lower(),
            '_'.join(map(lambda x: '{0}_{1}'.format(x[0], x[1]), sorted(params.items()))),
        )

    def get_country(self):
        if not hasattr(self, '_country'):
            self._country = get_object_or_404(
                Country.objects.defer(
                    'geometry', 'geometry_simplified',
                ).select_related('last_weekly_status').annotate(code_lower=Lower('code')),
                code_lower=self.kwargs.get('country_code'),
            )
        return self._country

    def get_queryset(self):
        return super().get_queryset().filter(country=self.get_country())

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'list':
            serializer_class = ListSchoolSerializer
        if self.action == 'export_csv_schools':
            serializer_class = CSVSchoolsListSerializer
        return serializer_class

    @action(methods=['get'], detail=False, url_path='export-csv-schools', url_name='export_csv_schools')
    def export_csv_schools(self, request, *args, **kwargs):
        country = get_object_or_404(
            self.get_queryset().annotate(code_lower=Lower('code')),
            code_lower=self.kwargs.get('country_code'),
        )
        serializer = self.get_serializer(self.get_queryset(), many=True)
        csvwriter = SchoolsCSVWriterBackend(serializer, country)
        response = csvwriter.write()
        return response


@method_decorator([cache_control(public=True, max_age=settings.CACHE_CONTROL_MAX_AGE)], name='dispatch')
class RandomSchoolsListAPIView(CachedListMixin, ListAPIView):
    LIST_CACHE_KEY_PREFIX = 'RANDOM_SCHOOLS'

    queryset = School.objects.order_by('?')[:settings.RANDOM_SCHOOLS_DEFAULT_AMOUNT]
    serializer_class = SchoolPointSerializer
    pagination_class = None

    def get_serializer(self, *args, **kwargs):
        countries_statuses = Country.objects.all().defer('geometry', 'geometry_simplified').select_related(
            'last_weekly_status',
        ).values_list(
            'id', 'last_weekly_status__integration_status',
        )
        kwargs['countries_statuses'] = dict(countries_statuses)
        return super(RandomSchoolsListAPIView, self).get_serializer(*args, **kwargs)
