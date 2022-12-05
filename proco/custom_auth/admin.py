from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from proco.custom_auth.models import ApplicationUser


class ApplicationUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets
    fieldsets[2][1]['fields'] = (
        'is_active',
        'is_staff',
        'is_superuser',
        'groups',
        'user_permissions',
        'countries_available',
    )


if not ApplicationUser._meta.abstract:
    admin.site.register(ApplicationUser, ApplicationUserAdmin)
