from rest_framework import serializers
from authors.apps.notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'receiver', 'message', 'link', 'is_read', 'created_at')

