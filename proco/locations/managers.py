from django.db import models
from django.db.models import Case, Count, IntegerField, When


class CountryManager(models.Manager):
    def aggregate_integration_statuses(self):
        from proco.connection_statistics.models import CountryWeeklyStatus
        return self.get_queryset().aggregate(
            countries_joined=Count(Case(When(
                last_weekly_status__integration_status__in=[
                    CountryWeeklyStatus.SCHOOL_MAPPED,
                    CountryWeeklyStatus.STATIC_MAPPED,
                    CountryWeeklyStatus.REALTIME_MAPPED,
                ], then=1),
                output_field=IntegerField())),
            countries_connected_to_realtime=Count(Case(When(
                last_weekly_status__integration_status=CountryWeeklyStatus.REALTIME_MAPPED, then=1),
                output_field=IntegerField())),
            countries_with_static_data=Count(Case(When(
                last_weekly_status__integration_status=CountryWeeklyStatus.STATIC_MAPPED, then=1),
                output_field=IntegerField()),
            ),
            countries_with_static_and_realtime_data=Count(Case(When(
                last_weekly_status__integration_status= (CountryWeeklyStatus.STATIC_MAPPED or CountryWeeklyStatus.REALTIME_MAPPED), then=1),
                output_field=IntegerField()) ,
            ),
        )
