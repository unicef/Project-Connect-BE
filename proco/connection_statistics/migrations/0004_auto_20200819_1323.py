# Generated by Django 2.2.15 on 2020-08-19 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0003_merge_20200817_1023'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='realtimeconnectivity',
            options={'ordering': ('id',), 'verbose_name': 'Real Time Connectivity', 'verbose_name_plural': 'Real Time Connectivities'},
        ),
    ]