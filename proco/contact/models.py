from django.db import models

from model_utils.models import TimeStampedModel


class ContactMessage(TimeStampedModel, models.Model):
    full_name = models.CharField(max_length=256)
    organisation = models.CharField(max_length=256)
    purpose = models.CharField(max_length=256)
    message = models.TextField()

    def __str__(self):
        return 'Message from: {0} ({1})'.format(self.full_name, self.created)
