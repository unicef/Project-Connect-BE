import re
from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone

from proco.connection_statistics.aggregations import (
    aggregate_connectivity_by_availability,
    aggregate_connectivity_by_speed,
    aggregate_connectivity_default,
    aggregate_coverage_by_availability,
    aggregate_coverage_by_types,
    aggregate_coverage_default,
)
from proco.connection_statistics.models import (
    CountryDailyStatus,
    CountryWeeklyStatus,
    RealTimeConnectivity,
    SchoolDailyStatus,
    SchoolWeeklyStatus,
)
from proco.locations.models import Country
from proco.schools.constants import ColorMapSchema
from proco.schools.models import School
from proco.utils.dates import get_current_week, get_current_year


def aggregate_real_time_data_to_school_daily_status(country, date):
    schools = RealTimeConnectivity.objects.filter(
        created__date=date, school__country=country,
    ).order_by('school').values_list('school', flat=True).order_by('school_id').distinct('school_id')

    for school in schools:
        aggregate = RealTimeConnectivity.objects.filter(
            created__date=date, school=school,
        ).aggregate(
            Avg('connectivity_speed'),
            Avg('connectivity_latency'),
        )
        school_daily_status, _ = SchoolDailyStatus.objects.get_or_create(school_id=school, date=date)
        school_daily_status.connectivity_speed = aggregate['connectivity_speed__avg']
        school_daily_status.connectivity_latency = aggregate['connectivity_latency__avg']
        school_daily_status.save()


def aggregate_school_daily_to_country_daily(country, date) -> bool:
    aggregate = SchoolDailyStatus.objects.filter(
        school__country=country, date=date,
    ).aggregate(
        connectivity_speed__avg=Avg('connectivity_speed'),
        connectivity_latency__avg=Avg('connectivity_latency'),
    )
    if all(v is None for v in aggregate.values()):
        # nothing to do here
        return False

    CountryDailyStatus.objects.update_or_create(country=country, date=date, defaults={
        'connectivity_speed': aggregate['connectivity_speed__avg'],
        'connectivity_latency': aggregate['connectivity_latency__avg'],
    })

    return True


def aggregate_school_daily_status_to_school_weekly_status(country) -> bool:
    date = timezone.now().date()
    week_ago = date - timedelta(days=7)
    schools = School.objects.filter(
        country=country,
        id__in=SchoolDailyStatus.objects.filter(
            date__gte=week_ago,
        ).values_list('school', flat=True).order_by('school_id').distinct('school_id'),
    ).iterator()

    updated = False

    for school in schools:
        updated = True
        school_weekly, created = SchoolWeeklyStatus.objects.get_or_create(
            school=school, week=get_current_week(),
            year=get_current_year(),
        )

        aggregate = SchoolDailyStatus.objects.filter(
            school=school, date__gte=week_ago,
        ).aggregate(
            Avg('connectivity_speed'), Avg('connectivity_latency'),
        )

        school_weekly.connectivity = True
        school_weekly.connectivity_speed = aggregate['connectivity_speed__avg']
        school_weekly.connectivity_latency = aggregate['connectivity_latency__avg']

        prev_weekly = SchoolWeeklyStatus.objects.filter(school=school, date__lt=school_weekly.date).last()
        if prev_weekly:
            school_weekly.num_students = prev_weekly.num_students
            school_weekly.num_teachers = prev_weekly.num_teachers
            school_weekly.num_classroom = prev_weekly.num_classroom
            school_weekly.num_latrines = prev_weekly.num_latrines
            school_weekly.running_water = prev_weekly.running_water
            school_weekly.electricity_availability = prev_weekly.electricity_availability
            school_weekly.computer_lab = prev_weekly.computer_lab
            school_weekly.num_computers = prev_weekly.num_computers
            school_weekly.coverage_availability = prev_weekly.coverage_availability
            school_weekly.coverage_type = prev_weekly.coverage_type

        school_weekly.save()

    return updated


def update_country_weekly_status(country: Country):
    last_weekly_status_country = country.last_weekly_status
    country_status, created = CountryWeeklyStatus.objects.get_or_create(
        country=country, year=get_current_year(), week=get_current_week(),
    )
    if created:
        country.last_weekly_status = country_status
        country.save()
        country.last_weekly_status.integration_status = last_weekly_status_country.integration_status
        country.last_weekly_status.save(update_fields=('integration_status',))

    # calculate pie charts. first we need to understand which case is applicable for country
    latest_statuses = SchoolWeeklyStatus.objects.filter(school__country=country, _school__isnull=False)
    connectivity_types = CountryWeeklyStatus.CONNECTIVITY_TYPES_AVAILABILITY
    coverage_types = CountryWeeklyStatus.COVERAGE_TYPES_AVAILABILITY

    if RealTimeConnectivity.objects.filter(school__country=country).exists():
        country_status.connectivity_availability = connectivity_types.realtime_speed
        connectivity_stats = aggregate_connectivity_by_speed(latest_statuses)
    elif latest_statuses.filter(connectivity_speed__gte=0).exists():
        country_status.connectivity_availability = connectivity_types.static_speed
        connectivity_stats = aggregate_connectivity_by_speed(latest_statuses)
    elif latest_statuses.filter(connectivity__isnull=False).exists():
        country_status.connectivity_availability = connectivity_types.connectivity
        connectivity_stats = aggregate_connectivity_by_availability(latest_statuses)
    else:
        country_status.connectivity_availability = connectivity_types.no_connectivity
        connectivity_stats = aggregate_connectivity_default(latest_statuses)

    if latest_statuses.exclude(coverage_type=SchoolWeeklyStatus.COVERAGE_TYPES.unknown).exists():
        country_status.coverage_availability = coverage_types.coverage_type
        coverage_stats = aggregate_coverage_by_types(latest_statuses)
    elif latest_statuses.filter(coverage_availability__isnull=False).exists():
        country_status.coverage_availability = coverage_types.coverage_availability
        coverage_stats = aggregate_coverage_by_availability(latest_statuses)
    else:
        country_status.coverage_availability = coverage_types.no_coverage
        coverage_stats = aggregate_coverage_default(latest_statuses)

    # remember connectivity pie chart
    country_status.schools_connectivity_good = connectivity_stats[ColorMapSchema.GOOD]
    country_status.schools_connectivity_moderate = connectivity_stats[ColorMapSchema.MODERATE]
    country_status.schools_connectivity_no = connectivity_stats[ColorMapSchema.NO]
    country_status.schools_connectivity_unknown = connectivity_stats[ColorMapSchema.UNKNOWN]

    # remember coverage pie chart
    country_status.schools_coverage_good = coverage_stats[ColorMapSchema.GOOD]
    country_status.schools_coverage_moderate = coverage_stats[ColorMapSchema.MODERATE]
    country_status.schools_coverage_no = coverage_stats[ColorMapSchema.NO]
    country_status.schools_coverage_unknown = coverage_stats[ColorMapSchema.UNKNOWN]

    # calculate speed & latency where available
    schools_stats = latest_statuses.aggregate(
        total=Count('*'),
        connectivity_speed=Avg('connectivity_speed', filter=Q(connectivity_speed__gt=0)),
        connectivity_latency=Avg('connectivity_latency', filter=Q(connectivity_latency__gt=0)),
    )

    country_status.connectivity_speed = schools_stats['connectivity_speed']
    country_status.connectivity_latency = schools_stats['connectivity_latency']

    country_status.schools_total = schools_stats['total']
    schools_with_data = country_status.schools_connectivity_moderate + country_status.schools_connectivity_good
    country_status.schools_connected = schools_with_data
    if country_status.schools_total:
        country_status.schools_with_data_percentage = 1.0 * country_status.schools_connected
        country_status.schools_with_data_percentage /= country_status.schools_total
    else:
        country_status.schools_with_data_percentage = 0

    # move country status as far as we can
    if country_status.integration_status == CountryWeeklyStatus.COUNTRY_CREATED and country_status.schools_total:
        country_status.integration_status = CountryWeeklyStatus.SCHOOL_OSM_MAPPED

    if country_status.integration_status == CountryWeeklyStatus.JOINED and country_status.schools_total:
        country_status.integration_status = CountryWeeklyStatus.SCHOOL_MAPPED

    if country_status.integration_status == CountryWeeklyStatus.SCHOOL_MAPPED and any([
        country_status.schools_connectivity_good,
        country_status.schools_connectivity_moderate,
        country_status.schools_connectivity_no,
        country_status.schools_coverage_good,
        country_status.schools_coverage_moderate,
        country_status.schools_coverage_no,
    ]):
        country_status.integration_status = CountryWeeklyStatus.STATIC_MAPPED

    if country_status.integration_status == CountryWeeklyStatus.STATIC_MAPPED \
            and country_status.connectivity_availability == connectivity_types.realtime_speed:
        country_status.integration_status = CountryWeeklyStatus.REALTIME_MAPPED

    country_status.avg_distance_school = country.calculate_avg_distance_school()

    country_status.save()


def update_country_data_source_by_csv_filename(imported_file):
    match = re.search(r'-(\D+)(?:-\d+)*-[^-]+\.\w+$', imported_file.filename)  # noqa: DUO138
    if match:
        source = match.group(1)
    else:
        source = '.'.join(imported_file.filename.split('.')[:-1])
    pretty_source = source.replace('_', ' ')
    if imported_file.country.data_source:
        if pretty_source.lower() not in imported_file.country.data_source.lower():
            imported_file.country.data_source += f'\n{pretty_source.capitalize()}'
    else:
        imported_file.country.data_source = pretty_source.capitalize()

    imported_file.country.save()
