from django.contrib import admin

from proco.background.models import BackgroundTask


@admin.register(BackgroundTask)
class BackgroundTaskAdmin(admin.ModelAdmin):
    readonly_fields = ('task_id', 'status', 'created_at', 'log', 'completed_at')
    change_form_template = 'admin/background/backgroud_task_change.html'
    list_display = ('task_id', 'status', 'created_at', 'completed_at')
    search_fields = ('task_id', 'log')
