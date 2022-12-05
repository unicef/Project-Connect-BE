# Generated by Django 2.2.15 on 2020-08-17 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='countrydailystatus',
            options={'ordering': ('id',), 'verbose_name': 'Country Daily Status', 'verbose_name_plural': 'Country Daily Statuses'},
        ),
        migrations.AlterModelOptions(
            name='countryweeklystatus',
            options={'ordering': ('id',), 'verbose_name': 'Country Weekly Status', 'verbose_name_plural': 'Country Weekly Statuses'},
        ),
        migrations.AlterModelOptions(
            name='realtimeconnectivity',
            options={'ordering': ('id',), 'verbose_name': 'Country Weekly Status', 'verbose_name_plural': 'Country Weekly Statuses'},
        ),
        migrations.AlterModelOptions(
            name='schooldailystatus',
            options={'ordering': ('id',), 'verbose_name': 'School Daily Status', 'verbose_name_plural': 'School Daily Statuses'},
        ),
        migrations.AlterModelOptions(
            name='schoolweeklystatus',
            options={'ordering': ('id',), 'verbose_name': 'School Weekly Status', 'verbose_name_plural': 'School Weekly Statuses'},
        ),
    ]