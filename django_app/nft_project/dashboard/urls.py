from django.urls import path
from .views import admin_login_view, users_list_view, delete_user_view

app_name = 'dashboard'

urlpatterns = [
    path('login/', admin_login_view, name='admin_login'),
    path('users/', users_list_view, name='users_list'),
    path('users/delete/<int:user_id>/', delete_user_view, name='delete_user'),
]

