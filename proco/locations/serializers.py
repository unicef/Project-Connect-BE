from rest_framework import serializers

from proco.connection_statistics.serializers import CountryWeeklyStatusSerializer
from proco.locations.models import Country


class BaseCountrySerializer(serializers.ModelSerializer):
    map_preview = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = (
            'id', 'name', 'code', 'flag',
            'map_preview', 'description', 'data_source', 'date_schools_mapped',
        )
        read_only_fields = fields

    def get_map_preview(self, instance):
        if not instance.map_preview:
            return ''

        request = self.context.get('request')
        photo_url = instance.map_preview.url
        return request.build_absolute_uri(photo_url)


class CountrySerializer(BaseCountrySerializer):
    pass


class BoundaryListCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id', 'code', 'geometry_simplified',
        )
        read_only_fields = fields


class ListCountrySerializer(BaseCountrySerializer):
    integration_status = serializers.SerializerMethodField()
    schools_with_data_percentage = serializers.SerializerMethodField()
    schools_total = serializers.SerializerMethodField()
    connectivity_availability = serializers.SerializerMethodField()
    coverage_availability = serializers.SerializerMethodField()

    class Meta(BaseCountrySerializer.Meta):
        fields = BaseCountrySerializer.Meta.fields + (
            'integration_status', 'date_of_join', 'schools_with_data_percentage', 'schools_total',
            'connectivity_availability', 'coverage_availability',
        )

    def get_integration_status(self, instance):
        return instance.last_weekly_status.integration_status

    def get_schools_total(self, instance):
        return instance.last_weekly_status.schools_total if instance.last_weekly_status.schools_total else None

    def get_schools_with_data_percentage(self, instance):
        return (instance.last_weekly_status.schools_with_data_percentage
                if instance.last_weekly_status.schools_with_data_percentage else None)

    def get_connectivity_availability(self, instance):
        return instance.last_weekly_status.connectivity_availability

    def get_coverage_availability(self, instance):
        return instance.last_weekly_status.coverage_availability


class DetailCountrySerializer(BaseCountrySerializer):
    statistics = serializers.SerializerMethodField()

    class Meta(BaseCountrySerializer.Meta):
        fields = BaseCountrySerializer.Meta.fields + ('statistics', 'geometry')

    def get_statistics(self, instance):
        return CountryWeeklyStatusSerializer(instance.last_weekly_status if instance.last_weekly_status else None).data
