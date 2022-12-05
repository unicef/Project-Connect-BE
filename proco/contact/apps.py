from django.apps import AppConfig


class ContactConfig(AppConfig):
    name = 'proco.contact'
    verbose_name = 'Contact'

    def ready(self):
        from proco.contact import receivers  # NOQA
