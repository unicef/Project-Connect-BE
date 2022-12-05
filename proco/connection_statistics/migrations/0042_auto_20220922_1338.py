# Generated by Django 2.2.19 on 2022-09-22 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connection_statistics', '0041_auto_20201201_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolweeklystatus',
            name='num_classroom',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='schoolweeklystatus',
            name='num_computers',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='schoolweeklystatus',
            name='num_latrines',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='schoolweeklystatus',
            name='num_students',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='schoolweeklystatus',
            name='num_teachers',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
    ]