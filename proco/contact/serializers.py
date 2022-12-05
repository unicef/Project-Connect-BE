from rest_framework import serializers

from proco.contact.models import ContactMessage


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('full_name', 'organisation', 'purpose', 'message')
