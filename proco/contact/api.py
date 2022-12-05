from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from proco.contact.serializers import ContactSerializer


class ContactAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ContactSerializer
