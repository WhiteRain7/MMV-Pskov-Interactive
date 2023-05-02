"""
Definition of views.
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm

from .forms import FeedbackForm
from .models import Game, Blog, Comment # использование модели комментариев
from .forms import CommentForm, BlogForm # использование формы ввода комментария

from datetime import datetime
import random

def home (request):
    """
        Renders the home page.
    """
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/index.html',
        {
            'page': 'homep',
            'page_title': 'Домашняя страница',
            'year':datetime.now().year,
            'randint': random.randint(1, 12),
            'games': Game.objects.all(),
            'blogs': Blog.objects.all()[:3]
        }
    )

def contact (request):
    """
        Renders the contact page.
    """
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/contact.html',
        {
            'page': 'links',
            'page_title': 'Контакты',
            'message': 'Наши контакты.',
            'year': datetime.now().year,
            'randint': random.randint(1, 12),
        }
    )

def about (request):
    """
        Renders the about page.
    """
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/about.html',
        {
            'page': 'about',
            'page_title': 'О компании',
            'message': 'Описание нашей компании.',
            'year': datetime.now().year,
            'randint': random.randint(1, 12),
        }
    )

def feedback (request):
    """
        Renders the about page.
    """
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            data = dict()
            data['game' ] = Game.objects.get(id=form.cleaned_data['game']).name
            data['mark' ] = form.cleaned_data['mark'        ]
            data['good' ] = form.cleaned_data['details_good']
            data['bad'  ] = form.cleaned_data['details_bad' ]
            data['email'] = (
                form.cleaned_data['contact']
                if form.cleaned_data['email_allowed'] else
                '<email not allowed>'
            )
            form = None

    else:
        data = None
        form = FeedbackForm()

    return render(
        request,
        'app/feedback.html',
        {
            'page': 'fdbck',
            'page_title': 'Оставить отзыв' if data is None else 'Отзыв отправлен',
            'year': datetime.now().year,
            'randint': random.randint(1, 12),
            'form': form,
            'data': data
        }
    )

def registration (request):
    """
        Renders the registration page.
    """

    assert isinstance(request, HttpRequest)

    if request.method == "POST": # после отправки формы
        regform = UserCreationForm(request.POST)

        if regform.is_valid(): #валидация полей формы

            reg_f = regform.save(commit=False) # не сохраняем автоматически данные формы

            reg_f.is_staff = False # запрещен вход в административный раздел
            reg_f.is_active = True # активный пользователь
            reg_f.is_superuser = False # не является суперпользователем
            reg_f.date_joined = datetime.now() # дата регистрации
            reg_f.last_login = datetime.now() # дата последней авторизации

            reg_f.save() # сохраняем изменения после добавления данных

            user = authenticate(
                username=regform.cleaned_data['username'], 
                password=regform.cleaned_data['password1']
            )
            login(request, user)

            return redirect('home') # переадресация на главную страницу после регистрации

    else:

        regform = UserCreationForm() # создание объекта формы для ввода данных нового пользователя

    return render(
        request,
        'app/registration.html',
        {
            'regform': regform, # передача формы в шаблон веб-страницы
            'year':datetime.now().year,
            'randint': random.randint(1, 12),
        }
    )

def posts (request, parametr = None):
    """
        Renders the posts page.
    """
    assert isinstance(request, HttpRequest)

    available_tags = [
        {
            'tag': game.tag,
            'colour': game.tag_colour
        } for game in Game.objects.all()
    ]

    if parametr is None:
        posts = Blog.objects.all() # запрос на выбор всех статей блога из модели
    else:
        games = Game.objects.filter(tag=parametr)
        posts = []
        for game in games:
            posts += Blog.objects.filter(about=game.id)

    return render(
        request,
        'app/posts.html',
        {
            'page': 'posts',
            'page_title': 'Статьи',
            'posts': posts,
            'year': datetime.now().year,
            'randint': random.randint(1, 12),
            'tag': parametr,
            'tags': available_tags,
        }
    )

def blogpost (request, parametr):
    """
        Renders the blogpost page.
    """
    assert isinstance(request, HttpRequest)

    post_1 = Blog.objects.get(id=parametr) # запрос на выбор конкретной статьи по параметру
    comments = Comment.objects.filter(post=parametr)

    if request.method == "POST": # после отправки данных формы на сервер методом POST
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_f = form.save(commit=False)
            comment_f.author = request.user # добавляем (так как этого поля нет в форме) в модель Комментария (Comment) в поле автор авторизованного пользователя
            comment_f.date = datetime.now() # добавляем в модель Комментария (Comment) текущую дату
            comment_f.post = Blog.objects.get(id=parametr) # добавляем в модель Комментария (Comment) статью, для которой данный комментарий
            comment_f.save() # сохраняем изменения после добавления полей

            return redirect('blogpost', parametr=post_1.id) # переадресация на ту же страницу статьи после отправки комментария
        
    else:
        form = CommentForm() # создание формы для ввода комментария

    return render(
        request,
        'app/blogpost.html',
        {
            'page': 'posts',
            'post_1': post_1, # передача конкретной статьи в шаблон веб-страницы
            'year':datetime.now().year,
            'randint': random.randint(1, 12),
            'comments': comments, # передача всех комментариев к данной статье в шаблон веб-страницы
            'form': form, # передача формы добавления комментария в шаблон веб-страницы
        }
    )

def newpost (request):
    """
        Renders the new post creation page.
    """

    assert isinstance(request, HttpRequest)

    if request.method == "POST": # после отправки формы
        form = BlogForm(request.POST, request.FILES)

        if form.is_valid(): #валидация полей формы

            post_f = form.save(commit=False) # не сохраняем автоматически данные формы

            post_f.posted = datetime.now()
            post_f.author = request.user

            post_f.save() # сохраняем изменения после добавления данных

            return redirect('posts') # переадресация на главную страницу после регистрации

    else:

        form = BlogForm() # создание объекта формы для ввода данных нового пользователя

    return render(
        request,
        'app/newpost.html',
        {
            'page': 'npost',
            'form': form, # передача формы в шаблон веб-страницы
            'page_title': 'Создание блога',
            'year': datetime.now().year,
            'randint': random.randint(1, 12),
            'game_names': Game.objects.all()
        }
    )
    
def video (request):
    """
        Renders the new post creation page.
    """

    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/video.html',
        {
            'page': 'video',
            'page_title': 'Видео',
            'year': datetime.now().year,
            'randint': random.randint(1, 12),
        }
    )
