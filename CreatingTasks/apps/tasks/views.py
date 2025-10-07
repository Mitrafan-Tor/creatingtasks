from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import TaskList, Task, Comment
from .serializers import (
    TaskListSerializer, TaskSerializer, TaskCreateSerializer,
    TaskUpdateSerializer, CommentSerializer
)
from .permissions import IsTaskListMember


class TaskListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_queryset(self):
        return TaskList.objects.filter(
            Q(created_by=self.request.user) | Q(members=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        task_list = serializer.save(created_by=self.request.user)
        task_list.members.add(self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTaskListMember]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(task_list__created_by=user) | Q(task_list__members=user)
        ).distinct().select_related('assigned_to', 'created_by', 'task_list')

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        # Send notification if assigned_to is set
        if task.assigned_to and task.assigned_to != self.request.user:
            self._send_task_assigned_notification(task)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.mark_as_completed()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        tasks = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    def _send_task_assigned_notification(self, task):
        from apps.notifications.tasks import send_task_assigned_notification
        send_task_assigned_notification.delay(task.id)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            task__task_list__members=self.request.user
        ).select_related('author', 'task')

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        # Send notification to task members
        self._send_comment_notification(comment)

    def _send_comment_notification(self, comment):
        from apps.notifications.tasks import send_comment_notification
        send_comment_notification.delay(comment.id)