from django.apps import AppConfig


class DailyCheckAppContactConfig(AppConfig):
    name = 'proco.dailycheckapp_contact'
    verbose_name = 'Daily Check App Contact'

    def ready(self):
        from proco.dailycheckapp_contact import receivers  # NOQA
