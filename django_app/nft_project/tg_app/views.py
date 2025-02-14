import random
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated  # Предполагается, что у вас настроена аутентификация по Telegram
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import User, Roll

def home(request):
    """
    Отображает главную страницу с HTML-кодом.
    """
    return render(request, 'index.html')


@api_view(['GET'])
def get_user(request):
    """
    Получение данных пользователя по telegram_id.

    Параметры запроса:
      - telegram_id: идентификатор пользователя в Telegram.
    """
    telegram_id = request.GET.get("telegram_id")
    if not telegram_id:
        return Response({"error": "telegram_id не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "telegram_id": user.telegram_id,
        "attempts_left": user.attempts_left
    })


@api_view(['POST'])
@transaction.atomic
def roll(request):
    """
    Генерация нового ролла:
      - Проверяет наличие попыток у пользователя.
      - Генерирует вероятности для 6 NFT.
      - Создаёт запись в базе данных с новым роллом (status = "pending").
      - Уменьшает количество попыток.

    Параметры запроса:
      - telegram_id: идентификатор пользователя в Telegram (передаётся через тело запроса или GET-параметры).
    """
    telegram_id = request.data.get("telegram_id") or request.GET.get("telegram_id")
    if not telegram_id:
        return Response({"error": "telegram_id не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    if user.attempts_left <= 0:
        return Response({"error": "Попытки закончились"}, status=status.HTTP_400_BAD_REQUEST)

    nft_names = ["NFT1", "NFT2", "NFT3", "NFT4", "NFT5", "NFT6"]
    probabilities = {name: round(random.uniform(0, 100), 2) for name in nft_names}

    # Создаём новый ролл в базе данных
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def accept_roll(request, roll_id):
    """
    Принимает новый ролл (переводит в статус "completed").
    Если ранее был принят другой ролл, он становится неактуальным.

    Аргументы:
      - roll_id: идентификатор ролла, который необходимо принять.
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
