from django.db import models

# Модель для пользователей
class User(models.Model):
    # Уникальный идентификатор пользователя из Telegram
    telegram_id = models.BigIntegerField(unique=True)

    # Никнейм пользователя (может быть пустым)
    username = models.CharField(max_length=100, blank=True, null=True)

    # Время регистрации пользователя
    created_at = models.DateTimeField(auto_now_add=True)

    # Время последнего обновления данных пользователя
    updated_at = models.DateTimeField(auto_now=True)

    # Является ли пользователь премиум (по умолчанию False)
    is_premium = models.BooleanField(default=False)

    # Количество оставшихся попыток
    attempts_left = models.IntegerField(default=3)

    def __str__(self):
        # Строковое представление пользователя (для админки и других целей)
        return f"User {self.telegram_id} - {self.username}"

# Модель для роллов (попыток получения NFT)
class Roll(models.Model):
    # Ссылка на пользователя, который сделал попытку
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Данные о вероятностях для каждой NFT (JSON формат)
    roll_data = models.JSONField()

    # Результат ролла (может быть пустым, если нет результатов)
    result_data = models.JSONField(null=True)

    # Статус ролла (например, "pending", "completed", "canceled")
    status = models.CharField(max_length=20)

    # Время создания ролла
    created_at = models.DateTimeField(auto_now_add=True)

    # Время последнего обновления ролла
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Строковое представление ролла (для админки и других целей)
        return f"Roll for {self.user} - Status: {self.status}"