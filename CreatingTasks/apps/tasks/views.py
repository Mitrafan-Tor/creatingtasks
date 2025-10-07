from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import TaskList, Task
from .serializers import TaskListSerializer, TaskSerializer
from .models import Comment
#from .serializers import CommentSerializer

class TaskListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer
    queryset = TaskList.objects.all()

    def get_queryset(self):
        return TaskList.objects.all()


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        return Task.objects.all()


# class CommentViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = CommentSerializer
#
#     def get_queryset(self):
#         return Comment.objects.filter(
#             task__task_list__members=self.request.user
#         ).select_related('author', 'task')
#
#     def perform_create(self, serializer):
#         comment = serializer.save(author=self.request.user)