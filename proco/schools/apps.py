from django.apps import AppConfig


class SchoolsConfig(AppConfig):
    name = 'proco.schools'
    verbose_name = 'Schools'

    def ready(self):
        from proco.schools import signals  # NOQA
