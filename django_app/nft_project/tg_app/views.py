import random
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
import numpy as np

from .models import User, Roll

# Базовые вероятности для NFT
base_probabilities = {
    "NFT1": 60,
    "NFT2": 40,
    "NFT3": 35,
    "NFT4": 5,
    "NFT5": 1,
    "NFT6": 0.00001
}



def generate_roll_probabilities():
    """
    Генерирует вероятности для каждого NFT с учетом случайных коэффициентов и нормализации.
    """
    random_factors = np.random.uniform(0.5, 1.5, len(base_probabilities))

    # Пересчитываем вероятности с учетом случайных коэффициентов
    adjusted_probs = {nft: base_probabilities[nft] * factor for nft, factor in
                      zip(base_probabilities.keys(), random_factors)}

    # Нормализуем вероятности в диапазон от 0.01% до 100%
    min_prob = 0.01
    max_prob = 100

    # Находим текущий диапазон вероятностей
    min_val = min(adjusted_probs.values())
    max_val = max(adjusted_probs.values())

    # Масштабируем вероятности в нужный диапазон
    scaled_probs = {
        nft: ((prob - min_val) / (max_val - min_val)) * (max_prob - min_prob) + min_prob
        for nft, prob in adjusted_probs.items()
    }

    return scaled_probs



class TelegramPermission(BasePermission):
    """
    Разрешение для проверки telegram_id.
    """

    def has_permission(self, request, view):
        telegram_id = request.data.get("telegram_id") or request.GET.get("telegram_id")
        return telegram_id is not None




def home(request):
    """
    Отображает главную страницу с HTML-кодом.
    """
    return render(request, 'index.html')


@api_view(['GET'])
def get_user(request):
    telegram_id = request.GET.get("telegram_id")

    if not telegram_id:
        return Response({"error": "telegram_id не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)

    username = request.GET.get("username", "")

    try:
        # Пытаемся найти пользователя по telegram_id
        user = User.objects.get(telegram_id=telegram_id)

        # Если передан username и он отличается от сохраненного, обновляем его
        if username and user.username != username:
            user.username = username
            user.save()

    except User.DoesNotExist:
        # Если пользователя нет в базе данных, создаем его
        user = User.objects.create(telegram_id=telegram_id, username=username, attempts_left=3)  # устанавливаем 3 попытки

    return Response({
        "telegram_id": user.telegram_id,
        "attempts_left": user.attempts_left
    }, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([TelegramPermission])
@transaction.atomic
def roll(request):
    telegram_id = request.data.get("telegram_id") or request.GET.get("telegram_id")
    if not telegram_id:
        return Response({"error": "telegram_id не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    if user.attempts_left <= 0:
        return Response({"error": "Попытки закончились"}, status=status.HTTP_400_BAD_REQUEST)

    # Генерация вероятности для NFT
    probabilities = generate_roll_probabilities()

    # Создаем новый ролл в базе данных
    roll_instance = Roll.objects.create(
        user=user,
        roll_data=probabilities,
        status="pending"
    )

    # Уменьшаем количество попыток
    user.attempts_left -= 1
    user.save()

    return Response({
        "roll_id": roll_instance.id,
        "attempts_left": user.attempts_left,
        "probabilities": probabilities
    }, status=status.HTTP_201_CREATED)


"""Как вы помните я хотел сделать принятие и отмену в ТЗ. Но меня отговорили... Но я оставлю может вам потом пригодится"""

@api_view(['POST'])
@transaction.atomic
def accept_roll(request, roll_id):
    """
    Принимает новый ролл (переводит в статус "completed").
    """
    telegram_id = getattr(request.user, "telegram_id", None)
    if not telegram_id:
        return Response({"error": "Не удалось определить telegram_id пользователя"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(telegram_id=telegram_id)
        roll_obj = Roll.objects.get(id=roll_id, user=user)
    except (User.DoesNotExist, Roll.DoesNotExist):
        return Response({"error": "Ролл или пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    if roll_obj.status != "pending":
        return Response({"error": "Невозможно принять данный ролл"}, status=status.HTTP_400_BAD_REQUEST)

    # Деактивируем ранее принятые роллы данного пользователя
    Roll.objects.filter(user=user, status="completed").update(status="obsolete")

    roll_obj.status = "completed"
    roll_obj.save()

    return Response({
        "roll_id": roll_obj.id,
        "status": roll_obj.status,
        "final_probabilities": roll_obj.roll_data
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def cancel_roll(request, roll_id):
    """
    Отменяет новый ролл (переводит в статус "canceled").
    Если ранее был принят ролл, он остаётся активным.

    Аргументы:
      - roll_id: идентификатор ролла, который необходимо отменить.
    """
    telegram_id = getattr(request.user, "telegram_id", None)
    if not telegram_id:
        return Response({"error": "Не удалось определить telegram_id пользователя"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(telegram_id=telegram_id)
        roll_obj = Roll.objects.get(id=roll_id, user=user)
    except (User.DoesNotExist, Roll.DoesNotExist):
        return Response({"error": "Ролл или пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    if roll_obj.status != "pending":
        return Response({"error": "Невозможно отменить данный ролл"}, status=status.HTTP_400_BAD_REQUEST)

    roll_obj.status = "canceled"
    roll_obj.save()

    return Response({
        "roll_id": roll_obj.id,
        "status": roll_obj.status
    }, status=status.HTTP_200_OK)
