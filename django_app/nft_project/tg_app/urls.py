"Не знай зачем, я оставил второй такой же, но пусть будет, может потом что-то придумаю."

from django.contrib import admin
from django.urls import path

from .views import home, get_user, roll, accept_roll, cancel_roll

app_name = 'tg_app'

urlpatterns = [
    # Главная страница
    path('', home, name='home'),

    # Эндпоинты для  API
    path('api/user', get_user, name='api-user'),
    path('api/roll', roll, name='api-roll'),
    path('api/rolls/<int:roll_id>/accept', accept_roll, name='api-accept-roll'),
    path('api/rolls/<int:roll_id>/cancel', cancel_roll, name='api-cancel-roll'),
]
