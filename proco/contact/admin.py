from django.contrib import admin

from proco.contact.models import ContactMessage


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'purpose', 'organisation', 'created', 'message')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(ContactMessage, ContactMessageAdmin)
