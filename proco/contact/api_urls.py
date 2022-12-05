from django.urls import path

from proco.contact import api

app_name = 'contact'

urlpatterns = [
    path('contact/', api.ContactAPIView.as_view(), name='contact'),
]
