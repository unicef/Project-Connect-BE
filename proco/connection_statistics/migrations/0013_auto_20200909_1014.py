# Generated by Django 2.2.16 on 2020-09-09 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0012_auto_20200909_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolweeklystatus',
            name='connectivity_status',
            field=models.CharField(choices=[('no', 'No connectivity'), ('unknown', 'Data unavailable'), ('moderate', 'Moderate'), ('good', 'Good')], default='unknown', max_length=8),
        ),
    ]
