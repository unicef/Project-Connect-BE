from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe


@mark_safe
def build_changelist_link(app_name, lookup, value, as_button=False):
    if value == 0:
        return '0'

    urlconf = getattr(settings, 'CMS_URLCONF', None)
    reference = reverse(f'admin:{app_name}_changelist', urlconf)
    class_attr = 'button' if as_button else ''

    return f'<a target="_blank" class="{class_attr}" href="{reference}?{lookup}">{value}</a>'
