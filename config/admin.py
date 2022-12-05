from django.conf.urls import url
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from proco.utils.cache import cache_manager
from proco.utils.tasks import update_all_cached_values


class CustomAdminSite(admin.AdminSite):
    site_header = _('Project Connect')
    site_title = _('Project Connect')
    index_title = _('Welcome to Project Connect')
    index_templates = 'admin/index.html'

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(r'^invalidate-cache/$', self.admin_view(self.invalidate_cache), name='admin_invalidate_cache'),
        ]
        return urls

    def invalidate_cache(self, request):
        cache_manager.invalidate()
        update_all_cached_values.delay()

        messages.success(request, 'Cache invalidation started. Maps will be updated in a few minutes.')
        return redirect('admin:index')
