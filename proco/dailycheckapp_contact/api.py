from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from proco.dailycheckapp_contact.serializers import DailyCheckAppContactSerializer


class DailyCheckAppContactAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = DailyCheckAppContactSerializer
