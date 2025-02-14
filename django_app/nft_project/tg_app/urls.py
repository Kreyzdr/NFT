from django.contrib import admin
from django.urls import path
from views import home  # Импортируем функцию home из вашего приложения

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Главная страница

]
