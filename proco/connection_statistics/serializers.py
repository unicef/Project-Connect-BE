from rest_framework import serializers

from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)


class CountryWeeklyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryWeeklyStatus
        fields = (
            'schools_total',
            'schools_connected',
            'schools_connectivity_unknown',
            'schools_connectivity_no',
            'schools_connectivity_moderate',
            'schools_connectivity_good',
            'schools_coverage_unknown',
            'schools_coverage_no',
            'schools_coverage_moderate',
            'schools_coverage_good',
            'connectivity_speed',
            'integration_status',
            'connectivity_availability',
            'coverage_availability',
            'avg_distance_school',
            'created',
            'modified',
        )
        read_only_fields = fields


class SchoolWeeklyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolWeeklyStatus
        fields = (
            'num_students',
            'num_teachers',
            'num_classroom',
            'num_latrines',
            'running_water',
            'electricity_availability',
            'computer_lab',
            'num_computers',
            'connectivity',
            'connectivity_type',
            'connectivity_speed',
            'connectivity_latency',
            'coverage_availability',
            'coverage_type',
            'created',
            'modified',
        )
        read_only_fields = fields


class CountryDailyStatusSerializer(serializers.ModelSerializer):
    year = serializers.ReadOnlyField(source='date.year')
    week = serializers.SerializerMethodField()
    weekday = serializers.SerializerMethodField()

    class Meta:
        model = CountryDailyStatus
        fields = (
            'date',
            'year',
            'week',
            'weekday',
            'connectivity_speed',
            'connectivity_latency',
        )
        read_only_fields = fields

    def get_week(self, obj):
        return obj.date.isocalendar()[1]

    def get_weekday(self, obj):
        return obj.date.isocalendar()[2]


class SchoolDailyStatusSerializer(serializers.ModelSerializer):
    year = serializers.ReadOnlyField(source='date.year')
    week = serializers.SerializerMethodField()
    weekday = serializers.SerializerMethodField()

    class Meta:
        model = SchoolDailyStatus
        fields = (
            'date',
            'year',
            'week',
            'weekday',
            'connectivity_speed',
            'connectivity_latency',
        )
        read_only_fields = fields

    def get_week(self, obj):
        return obj.date.isocalendar()[1]

    def get_weekday(self, obj):
        return obj.date.isocalendar()[2]
