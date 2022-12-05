# Generated by Django 2.2.15 on 2020-08-12 10:06

from django.db import migrations, models
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0002_auto_20200812_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='gps_confidence',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='school',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(blank=True, null=True),
        ),
    ]