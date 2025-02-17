from django.contrib import admin
from .models import User, Roll

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления моделью User.
    Позволяет отображать список пользователей, искать, фильтровать,
    а также удалять выбранных пользователей через экшен.
    """
    list_display = ('telegram_id', 'username', 'created_at', 'updated_at', 'is_premium', 'attempts_left')
    search_fields = ('telegram_id', 'username')  # Поля, по которым будет осуществляться поиск
    list_filter = ('is_premium', 'created_at')   # Поля, по которым можно фильтровать
    actions = ['delete_selected_users']          # Дополнительный экшен удаления

    def delete_selected_users(self, request, queryset):
        """
        Кастомный экшен для удаления выбранных пользователей.
        Вызывается из списка пользователей, когда они выделены галочками.
        """


        deleted_count = queryset.count()
        for user in queryset:
            user.delete()
        self.message_user(request, f"Успешно удалено пользователей: {deleted_count}")

    delete_selected_users.short_description = "Удалить выбранных пользователей"


@admin.register(Roll)
class RollAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления моделью Roll.
    Позволяет просматривать все роллы, искать по пользователю, фильтровать по статусу и дате.
    """

    list_display = ('id', 'user', 'status', 'created_at', 'updated_at')
    search_fields = ('user__telegram_id', 'status')  # Ищем по telegram_id пользователя и статусу
    list_filter = ('status', 'created_at')
