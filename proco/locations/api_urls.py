from django.urls import include, path

from rest_framework import routers

from proco.locations import api

router = routers.SimpleRouter()
router.register(r'countries', api.CountryViewSet, basename='countries')


app_name = 'locations'

urlpatterns = [
    path('countries-boundary/', api.CountryBoundaryListAPIView.as_view(), name='countries-boundary'),
    path('', include(router.urls)),
]
