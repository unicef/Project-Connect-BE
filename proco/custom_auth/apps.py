from django.apps import AppConfig
from django.db.models.signals import post_migrate

from proco.custom_auth.management import create_group_data_owner


class CustomAuthConfig(AppConfig):
    name = 'proco.custom_auth'
    verbose_name = 'Auth'

    def ready(self):
        post_migrate.connect(create_group_data_owner, sender=self)
