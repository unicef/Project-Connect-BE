from django.urls import path

from proco.dailycheckapp_contact import api

app_name = 'dailycheckapp_contact'

urlpatterns = [
    path('dailycheckapp_contact/', api.DailyCheckAppContactAPIView.as_view(), name='dailycheckapp_contact'),
]
