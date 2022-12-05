from django.utils import timezone


def get_current_year():
    return timezone.now().isocalendar()[0]


def get_current_week():
    return timezone.now().isocalendar()[1]


def get_current_weekday():
    return timezone.now().isocalendar()[2]
