# Generated by Django 2.2.15 on 2020-11-17 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0018_auto_20201112_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='name',
            field=models.CharField(default='Name unknown', max_length=255),
        ),
    ]
