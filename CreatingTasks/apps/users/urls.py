from django.urls import path
from .views import (
    register_view, login_view, logout_view,
    current_user_view, UserListView
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('me/', current_user_view, name='current_user'),
    path('users/', UserListView.as_view(), name='user_list'),
]