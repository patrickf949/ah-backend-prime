from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from authors.apps.notification.models import NotificationSetting, Notification
from authors.apps.notification.serializers import NotificationSerializer


class DisableInAppAndEmailNotificationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = NotificationSetting.objects.all()
    """
    disable in app notifications
    """

    def put(self, request, *args, **kwargs):
        disable_notify = NotificationSetting.objects.get(user=request.user.id)
        disable_notify.in_app_notifications = False
        disable_notify.email_notifications = False
        disable_notify.save()
        return Response({'error': 'disabled notifications app'}, status=status.HTTP_200_OK)


class NotificationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(receiver_id=request.user.id)
        serialized_data = self.serializer_class(notifications, many=True)
        return Response({
            'notifications': {
                'notificationsCount': len(notifications),
                'notifications': serialized_data.data
            }}, status=status.HTTP_200_OK)


class NotificationSingleView(generics.ListAPIView):
    """
    display single unread notifications
    """
    permission_classes = [IsAuthenticated, ]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, **kwargs):
        notifications = Notification.objects.filter(receiver_id=request.user.id, pk=self.kwargs.get('pk'))
        if not notifications:
            return Response({'error': 'notifications not available'}, status=status.HTTP_404_NOT_FOUND)
        notifications.update(is_read=True)
        serialized_data = self.serializer_class(notifications, many=True)
        return Response({'notifications': serialized_data.data}, status=status.HTTP_200_OK)


class NotificationUnreadView(generics.ListAPIView):
    """
    displays all unread notifications
    """
    permission_classes = [IsAuthenticated, ]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, **kwargs):
        notifications = Notification.objects.filter(receiver_id=request.user.id, is_read=False)
        if not notifications:
            return Response({'error': 'notifications not available'},
                            status=status.HTTP_404_NOT_FOUND)
        serialized_data = self.serializer_class(notifications, many=True)
        return Response({
            'notifications': {'notificationCounts': len(notifications),
                              'notifications': serialized_data.data}},
            status=status.HTTP_200_OK)
