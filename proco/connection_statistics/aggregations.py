from django.db.models import Count, Q

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.schools.constants import ColorMapSchema, statuses_schema


def aggregate_connectivity_by_speed(qs):
    return qs.aggregate(**{
        ColorMapSchema.GOOD: Count('school', filter=Q(
            connectivity_speed__gte=statuses_schema.CONNECTIVITY_SPEED_FOR_GOOD_CONNECTIVITY_STATUS,
        )),
        ColorMapSchema.MODERATE: Count('school', filter=Q(
            connectivity_speed__gt=0,
            connectivity_speed__lt=statuses_schema.CONNECTIVITY_SPEED_FOR_GOOD_CONNECTIVITY_STATUS,
        )),
        ColorMapSchema.NO: Count('school', filter=Q(connectivity_speed=0)),
        ColorMapSchema.UNKNOWN: Count('school', filter=Q(connectivity_speed__isnull=True)),
    })


def aggregate_connectivity_by_availability(qs):
    result = qs.aggregate(**{
        ColorMapSchema.GOOD: Count('school', filter=Q(connectivity=True)),
        ColorMapSchema.NO: Count('school', filter=Q(connectivity=False)),
        ColorMapSchema.UNKNOWN: Count('school', filter=Q(connectivity__isnull=True)),
    })
    result[ColorMapSchema.MODERATE] = 0
    return result


def aggregate_coverage_by_types(qs):
    return qs.aggregate(**{
        ColorMapSchema.GOOD: Count('school', filter=Q(
            coverage_type__in=[SchoolWeeklyStatus.COVERAGE_4G, SchoolWeeklyStatus.COVERAGE_3G],
        )),
        ColorMapSchema.MODERATE: Count('school', filter=Q(coverage_type=SchoolWeeklyStatus.COVERAGE_2G)),
        ColorMapSchema.NO: Count('school', filter=Q(coverage_type=SchoolWeeklyStatus.COVERAGE_NO)),
        ColorMapSchema.UNKNOWN: Count('school', filter=Q(coverage_type=SchoolWeeklyStatus.COVERAGE_UNKNOWN)),
    })


def aggregate_coverage_by_availability(qs):
    result = qs.aggregate(**{
        ColorMapSchema.GOOD: Count('school', filter=Q(coverage_availability=True)),
        ColorMapSchema.NO: Count('school', filter=Q(coverage_availability=False)),
        ColorMapSchema.UNKNOWN: Count('school', filter=Q(coverage_availability__isnull=True)),
    })
    result[ColorMapSchema.MODERATE] = 0
    return result


def aggregate_connectivity_default(qs):
    return {
        ColorMapSchema.GOOD: 0,
        ColorMapSchema.MODERATE: 0,
        ColorMapSchema.NO: 0,
        ColorMapSchema.UNKNOWN: qs.count(),
    }


def aggregate_coverage_default(qs):
    return {
        ColorMapSchema.GOOD: 0,
        ColorMapSchema.MODERATE: 0,
        ColorMapSchema.NO: 0,
        ColorMapSchema.UNKNOWN: qs.count(),
    }
