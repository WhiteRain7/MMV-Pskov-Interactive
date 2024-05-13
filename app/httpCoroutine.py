from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from datetime import datetime


def regular (page):
    pages = {
        'home' : 'Домашняя страница',
        'about' : 'О компании',
        'videos': 'Видео',
        'news': 'Новости',
        'store': 'Магазин',
        'login': 'Вход',
        'profile': 'Профиль',
        'registration': 'Регистрация',

        'manage': 'Управление',

        'manage_games': 'Управление играми',
        'manage_dlcs': 'Управление дополнениями',
        'manage_accessories': 'Управление аксессуарами',
        'manage_orders': 'Управление заказами',
        'manage_news': 'Управление новостями',
        'manage_users': 'Управление пользователями',

        'manage_game': 'Редактирование игры',
        'manage_dlc': 'Редактирование дополнения',
        'manage_accessory': 'Редактирование товара',
        'manage_article': 'Редактирование новости',
        'manage_user': 'Редактирование пользователя',

        'error': 'Ошибка',
    }

    return {
        'year': datetime.now().year,
        'page': page,
        'page_title': pages[page]
    }


def HTTP_error (request, code, message, description = None):
    return render(
        request,
        'app/error.html',
        {
            **regular('error'),
            'code': code,
            'message': message,
            'description': description
        },
        status = code,
        content_type = 'text/html'
    )


class Security:
    @staticmethod
    def valid (func):
        def wrapper (request, *args, **kwargs):
            try:
                assert isinstance(request, HttpRequest)
                return func(request, *args, **kwargs)
            
            except Exception as e:
                return HTTP_error(request, 500, 'Внутренняя ошибка сервера', str(e))
        
        return wrapper

    @staticmethod
    def _access_control (user):
        if not user.is_authenticated: return 0
        if user.is_staff: return 3
        if user.is_editor: return 2
        return 1

    @staticmethod
    def _access_permit (user, level):
        if level == 0: return True
        if level == 1: return user.is_authenticated
        if level == 2: return user.is_authenticated and (user.is_editor or user.is_staff)
        if level == 3: return user.is_authenticated and user.is_staff

    @staticmethod
    def access_level (level, exact = False, redirecting = None):
        def decorator (func):
            def wrapper (request, *args, **kwargs):
                control = Security._access_control(request.user)

                if (exact and control == level) or (not exact and control >= level):
                    return func(request, *args, **kwargs)
                
                else:
                    if redirecting:
                        return redirect(redirecting)

                    if request.user.is_authenticated:
                        return HTTP_error(request, 403, 'Недостаточно прав')
                    else:
                        return HTTP_error(request, 401, 'Пользователь не авторизован')
                
                
            return wrapper
        
        return decorator
    
    @staticmethod
    def allowed_methods (methods):
        def decorator (func):
            def wrapper (request, *args, **kwargs):
                if request.method.upper() == 'OPTIONS':
                    return HttpResponse(
                        status = 200,
                        headers = {
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': ', '.join(methods),
                            'Allow': ', '.join(methods),
                        }
                    )

                if request.method.upper() not in [ 'GET', 'POST', 'PUT', 'PATCH', 'DELETE' ]:
                    return HTTP_error(request, 501, 'Метод не поддерживается', f'Метод {request.method} не поддерживается сервером, используйте GET, POST или OPTIONS.')
                
                elif request.method.upper() in methods:
                    return func(request, *args, **kwargs)
                
                else:
                    return HTTP_error(request, 405, 'Метод не поддерживается', f'Ресурс {request.path} не поддерживает метод {request.method}, используйте {", ".join(methods)}.')
            
            return wrapper
        
        return decorator
    
    @staticmethod
    def exists (model):
        def decorator (func):
            def wrapper (request, *args, **kwargs):
                if kwargs.get('id', -1) == -1 or model.objects.filter(id = kwargs['id']).exists():
                    return func(request, *args, **kwargs)
                else:
                    return HTTP_error(request, 404, f'{model.Meta.verbose_name or "Ресурс"} не найден')
            
            return wrapper
        
        return decorator
