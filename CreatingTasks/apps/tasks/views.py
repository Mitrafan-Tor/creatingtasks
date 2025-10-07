from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TaskList, Task, Comment
from .serializers import TaskListSerializer, TaskSerializer, CommentSerializer, CommentCreateSerializer

class TaskListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer
    queryset = TaskList.objects.all()  # Добавьте эту строку

    def get_queryset(self):
        return TaskList.objects.filter(
            members=self.request.user
        ).prefetch_related('tasks', 'members')

    def perform_create(self, serializer):
        task_list = serializer.save(created_by=self.request.user)
        task_list.members.add(self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()  # Добавьте эту строку

    def get_queryset(self):
        return Task.objects.filter(
            task_list__members=self.request.user
        ).select_related('task_list', 'created_by', 'assigned_to')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.mark_as_completed()
        return Response({'status': 'task completed'})

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()  # Добавьте эту строку

    def get_queryset(self):
        return Comment.objects.filter(
            task__task_list__members=self.request.user
        ).select_related('author', 'task')

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)