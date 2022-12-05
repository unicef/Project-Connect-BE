from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from model_utils import Choices


class BackgroundTask(models.Model):
    STATUSES = Choices(
        ('running', _('Running')),
        ('completed', _('Completed')),
    )
    PROCESS_STATUSES = [STATUSES.running]

    task_id = models.CharField(max_length=50, primary_key=True)
    status = models.CharField(default=STATUSES.running, choices=STATUSES, max_length=10)
    log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name = _('Background Task')

    def __str__(self):
        return f'{self.task_id} {self.status}'

    def info(self, text: str):
        if self.log:
            self.log += '\n'

        self.log += '{0}: {1}'.format(timezone.now().strftime('%Y-%m-%d %H:%M:%S'), text)
        self.save()
