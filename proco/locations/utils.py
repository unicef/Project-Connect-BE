import os
import uuid

from django.conf import settings


def get_random_name_image(instance, filename):
    extension = os.path.splitext(filename)[1]
    return f'{settings.IMAGES_PATH}/{uuid.uuid4()}{extension}'
