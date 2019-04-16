from django.urls import path
from authors.apps.notification.views import (
    DisableInAppAndEmailNotificationView,
    NotificationView,
    NotificationSingleView,
    NotificationUnreadView
)

urlpatterns = [
    path('notifications/disable/', DisableInAppAndEmailNotificationView.as_view(), name='notification-disable'),
    path('users/notifications/', NotificationView.as_view(), name='notifications'),
    path('users/notifications/<int:pk>/unread/', NotificationSingleView.as_view(), name='notification-detail'),
    path('users/notifications/unread/', NotificationUnreadView.as_view(), name='notifications-unread')
]
