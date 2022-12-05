from rest_framework import serializers

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.connection_statistics.serializers import SchoolWeeklyStatusSerializer
from proco.locations.fields import GeoPointCSVField
from proco.schools.models import School


class BaseSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = (
            'id', 'name', 'geopoint',
        )
        read_only_fields = fields


class SchoolPointSerializer(BaseSchoolSerializer):
    country_integration_status = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = ('geopoint', 'country_id', 'country_integration_status')

    def __init__(self, *args, **kwargs):
        self.countries_statuses = kwargs.pop('countries_statuses', None)
        super(SchoolPointSerializer, self).__init__(*args, **kwargs)

    def get_country_integration_status(self, obj):
        return self.countries_statuses[obj.country_id]


class CountryToSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        self.country = kwargs.pop('country', None)
        super(CountryToSerializerMixin, self).__init__(*args, **kwargs)


class ListSchoolSerializer(CountryToSerializerMixin, BaseSchoolSerializer):
    connectivity_status = serializers.SerializerMethodField()
    coverage_status = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = BaseSchoolSerializer.Meta.fields + (
            'connectivity_status', 'coverage_status', 'is_verified',
        )

    def get_connectivity_status(self, obj):
        availability = self.country.last_weekly_status.connectivity_availability
        if not availability or not obj.last_weekly_status:
            return None
        return obj.last_weekly_status.get_connectivity_status(availability)

    def get_coverage_status(self, obj):
        availability = self.country.last_weekly_status.coverage_availability
        if not availability or not obj.last_weekly_status:
            return None
        return obj.last_weekly_status.get_coverage_status(availability)

    def get_is_verified(self, obj):
        if not self.country.last_weekly_status:
            return None
        return self.country.last_weekly_status.integration_status not in [
            CountryWeeklyStatus.COUNTRY_CREATED, CountryWeeklyStatus.SCHOOL_OSM_MAPPED,
        ]


class CSVSchoolsListSerializer(ListSchoolSerializer):
    geopoint = GeoPointCSVField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = ('name', 'geopoint', 'connectivity_status')


class SchoolSerializer(CountryToSerializerMixin, BaseSchoolSerializer):
    statistics = serializers.SerializerMethodField()
    connectivity_status = serializers.SerializerMethodField()
    coverage_status = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = BaseSchoolSerializer.Meta.fields + (
            'statistics', 'connectivity_status', 'coverage_status',
            'gps_confidence', 'address', 'postal_code',
            'admin_1_name', 'admin_2_name', 'admin_3_name', 'admin_4_name',
            'timezone', 'altitude', 'email', 'education_level', 'environment', 'school_type', 'is_verified',
        )

    def get_statistics(self, instance):
        return SchoolWeeklyStatusSerializer(instance.last_weekly_status).data

    def get_connectivity_status(self, obj):
        availability = self.country.last_weekly_status.connectivity_availability
        if not availability or not obj.last_weekly_status:
            return None
        return obj.last_weekly_status.get_connectivity_status(availability)

    def get_coverage_status(self, obj):
        availability = self.country.last_weekly_status.coverage_availability
        if not availability or not obj.last_weekly_status:
            return None
        return obj.last_weekly_status.get_coverage_status(availability)

    def get_is_verified(self, obj):
        if not self.country.last_weekly_status:
            return None
        return self.country.last_weekly_status.integration_status not in [
            CountryWeeklyStatus.COUNTRY_CREATED, CountryWeeklyStatus.SCHOOL_OSM_MAPPED,
        ]
