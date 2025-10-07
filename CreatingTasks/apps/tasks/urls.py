from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskListViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'lists', TaskListViewSet)
router.register(r'tasks', TaskViewSet)
# Пока полностью убираем comments
# router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]