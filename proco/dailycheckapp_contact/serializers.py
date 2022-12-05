from rest_framework import serializers

from proco.dailycheckapp_contact.models import ContactMessage


class DailyCheckAppContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('firstname', 'lastname', 'school_id', 'email', 'message')
