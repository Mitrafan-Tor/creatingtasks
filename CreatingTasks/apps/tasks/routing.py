from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tasks/(?P<task_list_id>\w+)/$', consumers.TaskConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]