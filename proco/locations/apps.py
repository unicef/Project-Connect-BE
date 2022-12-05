from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = 'proco.locations'
    verbose_name = 'Locations'

    def ready(self):
        from proco.locations import signals  # NOQA
