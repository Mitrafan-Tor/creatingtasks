import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import TaskList, Task


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_list_id = self.scope['url_route']['kwargs']['task_list_id']
        self.room_group_name = f'tasks_{self.task_list_id}'

        # Check if user has access to this task list
        if await self.has_access():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'task_updated':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'task_update',
                    'data': data
                }
            )

    async def task_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def has_access(self):
        user = self.scope['user']
        if isinstance(user, AnonymousUser):
            return False

        try:
            task_list = TaskList.objects.get(id=self.task_list_id)
            return user in task_list.members.all() or user == task_list.created_by
        except TaskList.DoesNotExist:
            return False


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']

        if isinstance(user, AnonymousUser):
            await self.close()
            return

        self.user_id = user.id
        self.room_group_name = f'notifications_{self.user_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))
