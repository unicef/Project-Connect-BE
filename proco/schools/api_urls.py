from django.urls import include, path

from rest_framework.routers import SimpleRouter

from proco.schools import api

country_schools = SimpleRouter()
country_schools.register(r'countries/(?P<country_code>\w+)/schools', api.SchoolsViewSet, basename='schools')

app_name = 'schools'

urlpatterns = [
    path('', include(country_schools.urls)),
    path('schools/random/', api.RandomSchoolsListAPIView.as_view(), name='random-schools'),
]
