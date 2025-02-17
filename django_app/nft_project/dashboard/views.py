from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as AuthUser


from tg_app.models import User



def admin_login_view(request):
    """
    Страница входа в панель администратора.
    Пользователь должен ввести пароль суперпользователя.
    При успешном вводе создаётся сессия и происходит редирект на /dashboard/users/.
    Ограничивается число попыток (например, в нашем случае 5 попыток).
    """

    # Инициализируем счетчик попыток в сессии
    if 'login_attempts' not in request.session:
        request.session['login_attempts'] = 0

    if request.method == "POST":
        password = request.POST.get('password', '')
        # Получаем  суперпользователя из базы
        superuser = AuthUser.objects.filter(is_superuser=True).first()
        request.session['login_attempts'] += 1

        if request.session['login_attempts'] > 5:
            messages.error(request, "Превышено количество попыток. Попробуйте позже.")
            return render(request, 'dashboard/login.html')

        if superuser and superuser.check_password(password):
            login(request, superuser)
            request.session['login_attempts'] = 0  # сброс счетчика
            return redirect(reverse('dashboard:users_list'))
        else:
            messages.error(request, "Неверный пароль.")

    return render(request, 'dashboard/login.html')



@login_required(login_url='/dashboard/login/')
def users_list_view(request):
    """
    Отображает список всех пользователей (из модели User из tg_app).
    Позволяет осуществлять поиск по telegram_id или username.
    """

    query = request.GET.get('q', '')
    if query:
        try:
            # Если query можно привести к int, фильтруем по telegram_id
            num = int(query)
            users = User.objects.filter(telegram_id=num)
        except ValueError:
            # Иначе фильтруем по username
            users = User.objects.filter(username__icontains=query)
    else:
        users = User.objects.all()

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'dashboard/users_list.html', context)



@login_required(login_url='/dashboard/login/')
def delete_user_view(request, user_id):
    """
    Удаляет пользователя с заданным id.
    Если пользователь не найден – возвращается 404.
    После удаления перенаправляет обратно на страницу списка.
    """

    user = get_object_or_404(User, pk=user_id)
    user.delete()

    messages.success(request, f"Пользователь {user.telegram_id} удалён.")
    return redirect(reverse('dashboard:users_list'))
