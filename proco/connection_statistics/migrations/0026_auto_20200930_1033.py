# Generated by Django 2.2.16 on 2020-09-30 10:33
import itertools
from datetime import datetime

from django.db import migrations, models


def fix_statistics_date(apps, schema_editor):
    SchoolWeeklyStatus = apps.get_model('connection_statistics', 'SchoolWeeklyStatus')
    CountryWeeklyStatus = apps.get_model('connection_statistics', 'CountryWeeklyStatus')
    for status in itertools.chain(SchoolWeeklyStatus.objects.all(), CountryWeeklyStatus.objects.all()):
        status.date = datetime.strptime(f'{status.year}-W{status.week}-1', '%Y-W%W-%w')
        status.save()


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0025_auto_20200930_0808'),
    ]

    operations = [
        migrations.RunPython(fix_statistics_date, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='countryweeklystatus',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='schoolweeklystatus',
            name='date',
            field=models.DateField(),
        ),
    ]
