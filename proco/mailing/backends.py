from django.conf import settings

from templated_email.backends.vanilla_django import TemplateBackend

from proco.mailing.tasks import send_email


class AsyncTemplateBackend(TemplateBackend):
    def send(self, *args, **kwargs):
        use_celery = kwargs.pop('use_celery', settings.MAILING_USE_CELERY)

        if not use_celery:
            return super(AsyncTemplateBackend, self).send(*args, **kwargs)

        send_email.delay(self, use_celery=False, *args, **kwargs)
