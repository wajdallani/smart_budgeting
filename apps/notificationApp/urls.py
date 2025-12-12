from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationAsReadView,
    MarkAllNotificationsAsReadView,
    TestNotificationView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications_list'),
    path('<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='notification_mark_read'),
    path('read-all/', MarkAllNotificationsAsReadView.as_view(), name='notification_mark_all_read'),
    path('test-notif/', TestNotificationView.as_view(), name='test_notif'),

]
