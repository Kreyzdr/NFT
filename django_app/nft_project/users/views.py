# views.py
from django.shortcuts import render
from django.http import JsonResponse
from tg_app.models import User
import random

# Функция для генерации вероятностей для 6 NFT
def generate_probabilities():
    return {
        "NFT1": round(random.uniform(0, 100), 2),
        "NFT2": round(random.uniform(0, 100), 2),
        "NFT3": round(random.uniform(0, 100), 2),
        "NFT4": round(random.uniform(0, 100), 2),
        "NFT5": round(random.uniform(0, 100), 2),
        "NFT6": round(random.uniform(0, 100), 2),
    }

# Главная страница приложения
def home(request):
    # Получаем пользователя из сессии или создаем нового
    telegram_id = request.GET.get("telegram_id")  # получаем ID пользователя
    user, created = User.objects.get_or_create(telegram_id=telegram_id)

    # Если у пользователя не осталось попыток, то ограничиваем его действия
    if user.attempts_left <= 0:
        return render(request, 'app/expired.html')

    probabilities = generate_probabilities()  # Генерация вероятностей для NFT
    return render(request, 'app/home.html', {
        'user': user,
        'probabilities': probabilities
    })

# Функция для обработки нажатия кнопки "Roll"
def roll(request):
    telegram_id = request.GET.get("telegram_id")  # Получаем ID пользователя
    user = User.objects.get(telegram_id=telegram_id)

    if user.attempts_left <= 0:
        return JsonResponse({'error': 'No attempts left'}, status=400)

    # Генерация вероятностей и обновление оставшихся попыток
    probabilities = generate_probabilities()
    user.attempts_left -= 1
    user.save()

    return JsonResponse({
        'probabilities': probabilities,
        'attempts_left': user.attempts_left
    })
