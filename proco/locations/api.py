from django.conf import settings
from django.db.models import BooleanField, F, Func
from django.db.models.functions.text import Lower
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView

from proco.locations.models import Country
from proco.locations.serializers import (
    BoundaryListCountrySerializer,
    CountrySerializer,
    DetailCountrySerializer,
    ListCountrySerializer,
)
from proco.utils.filters import NullsAlwaysLastOrderingFilter
from proco.utils.mixins import CachedListMixin, CachedRetrieveMixin


@method_decorator([cache_control(public=True, max_age=settings.CACHE_CONTROL_MAX_AGE)], name='dispatch')
class CountryViewSet(
    CachedListMixin,
    CachedRetrieveMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    LIST_CACHE_KEY_PREFIX = 'COUNTRIES_LIST'
    RETRIEVE_CACHE_KEY_PREFIX = 'COUNTRY_INFO'

    pagination_class = None
    queryset = Country.objects.all().annotate(
        geometry_empty=Func(F('geometry'), function='ST_IsEmpty', output_field=BooleanField()),
    ).select_related('last_weekly_status').filter(geometry_empty=False)
    serializer_class = CountrySerializer
    filter_backends = (
        NullsAlwaysLastOrderingFilter, SearchFilter,
    )
    ordering = ('name',)
    ordering_fields = ('name',)
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action == 'list':
            serializer_class = ListCountrySerializer
        else:
            serializer_class = DetailCountrySerializer
        return serializer_class

    def get_object(self):
        return get_object_or_404(self.queryset.annotate(code_lower=Lower('code')), code_lower=self.kwargs.get('pk'))

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.defer('geometry', 'geometry_simplified')
        return qs


@method_decorator([cache_control(public=True, max_age=settings.CACHE_CONTROL_MAX_AGE)], name='dispatch')
class CountryBoundaryListAPIView(CachedListMixin, ListAPIView):
    LIST_CACHE_KEY_PREFIX = 'COUNTRY_BOUNDARY'

    queryset = Country.objects.all().annotate(
        geometry_empty=Func(F('geometry'), function='ST_IsEmpty', output_field=BooleanField()),
    ).filter(geometry_empty=False).only('id', 'code', 'geometry_simplified')
    serializer_class = BoundaryListCountrySerializer
    pagination_class = None
