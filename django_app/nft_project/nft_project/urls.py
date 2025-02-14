"""
URL configuration for nft_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# Импортируем наши view-функции из приложения tg_app:
# Обратите внимание на правильный путь импорта
from tg_app.views import home, get_user, roll, accept_roll, cancel_roll

urlpatterns = [
    path('admin/', admin.site.urls),

    # Главная страница
    path('', home, name='home'),

    # Эндпоинты для вашего API
    path('api/user', get_user, name='api-user'),
    path('api/roll', roll, name='api-roll'),
    path('api/rolls/<int:roll_id>/accept', accept_roll, name='api-accept-roll'),
    path('api/rolls/<int:roll_id>/cancel', cancel_roll, name='api-cancel-roll'),
]


