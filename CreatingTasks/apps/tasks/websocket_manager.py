import json
import logging
from typing import Dict, Set
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Класс для управления WebSocket соединениями в CreatingTasks"""

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def send_task_update(self, task_list_id: int, data: Dict):
        """Отправка обновления задачи всем подключенным клиентам"""
        try:
            async_to_sync(self.channel_layer.group_send)(
                f'tasks_{task_list_id}',
                {
                    'type': 'task_update',
                    'data': data
                }
            )
            logger.info(f"Task update sent to group tasks_{task_list_id}")
        except Exception as e:
            logger.error(f"Error sending task update: {e}")

    def send_notification(self, user_id: int, notification_data: Dict):
        """Отправка уведомления конкретному пользователю"""
        try:
            async_to_sync(self.channel_layer.group_send)(
                f'notifications_{user_id}',
                {
                    'type': 'send_notification',
                    'data': notification_data
                }
            )
            logger.info(f"Notification sent to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    def broadcast_task_creation(self, task_list_id: int, task_data: Dict):
        """Широковещательная рассылка о создании новой задачи"""
        self.send_task_update(task_list_id, {
            'type': 'task_created',
            'task': task_data
        })

    def broadcast_task_update(self, task_list_id: int, task_data: Dict):
        """Широковещательная рассылка об обновлении задачи"""
        self.send_task_update(task_list_id, {
            'type': 'task_updated',
            'task': task_data
        })

    def broadcast_task_deletion(self, task_list_id: int, task_id: int):
        """Широковещательная рассылка об удалении задачи"""
        self.send_task_update(task_list_id, {
            'type': 'task_deleted',
            'task_id': task_id
        })


# Глобальный экземпляр менеджера WebSocket
websocket_manager = WebSocketManager()