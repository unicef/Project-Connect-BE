# Generated by Django 2.2.16 on 2020-09-17 11:16

import django.core.validators
from django.db import migrations, models

import calendar
from datetime import datetime, timedelta

def get_start_and_end_date_from_calendar_week(year, calendar_week):       
    monday = datetime.strptime(f'{year}-{calendar_week}-1', "%Y-%W-%w").date()
    return monday, monday + timedelta(days=6.9)


def fill_schools_with_data_percentage_field(apps, schema_editor):
    CountryWeeklyStatus = apps.get_model("connection_statistics", "CountryWeeklyStatus")
    School = apps.get_model("schools", "School")

    for country_weekly in CountryWeeklyStatus.objects.all():
        week_start, week_end = get_start_and_end_date_from_calendar_week(country_weekly.year, country_weekly.week)

        schools_number = School.objects.filter(created__lte=week_end, country=country_weekly.country).count()

        if schools_number:
            schools_with_data_number = School.objects.filter(
                weekly_status__created__lte=week_end, country=country_weekly.country
            ).count()

            country_weekly.schools_with_data_percentage = 100.0 * schools_with_data_number / schools_number
            country_weekly.save()


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0017_merge_20200915_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='countryweeklystatus',
            name='schools_with_data_percentage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.RunPython(fill_schools_with_data_percentage_field, migrations.RunPython.noop),
    ]
