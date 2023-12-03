"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _
from django.db import models
from .models import User, DLC, Accessory, Article, Comment, Order


class SignInForm (AuthenticationForm):
    username = forms.CharField(
        max_length = 254,
        widget = forms.TextInput({
            'class': 'form-control',
            'placeholder': 'Введите логин',
            'title': 'Введите ваш уникальный логин, который вы указывали при регистрации'
        }))

    password = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput({
            'class': 'form-control',
            'placeholder':'Введите пароль',
            'title': 'Укажите ваш пароль, который вы указывали при регистрации'
        }))
    
    class Meta (AuthenticationForm):
        model = User
        fields = ('username', 'password')


class SignUpForm (UserCreationForm):
    photo = forms.ImageField(
        label = 'Фото профиля',
        required = False,
        widget = forms.FileInput({
            'class': 'form-control',
            'accept': 'image/*',
            'oninput': 'event.target.files[0] ? event.target.classList.add("loaded") : event.target.classList.remove("loaded")',
        }))

    username = forms.CharField(
        max_length = 254,
        widget = forms.TextInput({
            'class': 'form-control',
            'placeholder': 'Введите логин',
            'title': 'Введите ваш уникальный логин, который вы указывали при регистрации'
        }))
    
    first = forms.CharField(
        max_length = 100,
        widget = forms.TextInput({
            'class': 'form-control',
            'placeholder': 'Введите ваше имя',
            'title': 'Введите ваше имя'
        })
    )

    last = forms.CharField(
        max_length = 100,
        widget = forms.TextInput({
            'class': 'form-control',
            'placeholder': 'Введите вашу фамилию',
            'title': 'Введите вашу фамилию'
        })
    )

    password1 = forms.CharField(
        label = _("Password1"),
        widget = forms.PasswordInput({
            'class': 'form-control',
            'placeholder':'Введите пароль',
            'title': 'Укажите ваш пароль, который вы указывали при регистрации'
        }))

    password2 = forms.CharField(
        label = _("Password2"),
        widget = forms.PasswordInput({
            'class': 'form-control',
            'placeholder':'Введите пароль ещё раз',
            'title': 'Укажите ваш пароль, который вы указывали при регистрации'
        }))
    
    class Meta (UserCreationForm):
        model = User
        fields = ('photo', 'username', 'first', 'last', 'password1', 'password2')


class DLCForm (forms.ModelForm):
    class Meta:
        model = DLC

        fields = {
            'about',
            'name',
            'content',
            'image',
            'price',
        }

        labels = {
            'about': 'Для какой игры',
            'name': 'Название',
            'content': 'Описание',
            'image': 'Изображение',
            'price': 'Цена',
        }


class AccessoryForm (forms.ModelForm):
    class Meta:
        model = Accessory

        fields = {
            'about',
            'name',
            'content',
            'tag',
            'image',
            'price',
            'stock',
            'virtual',
        }

        labels = {
            'about': 'Для какой игры',
            'name': 'Название',
            'content': 'Описание',
            'tag': 'Тег',
            'image': 'Изображение',
            'price': 'Цена',
            'stock': 'В наличии на складе',
            'virtual': 'Виртуальный товар',
        }


class ArticleForm (forms.ModelForm):
    class Meta:
        model = Article

        fields = {
            'about',
            'title',
            'content',
            'tag',
            'image'
        }

        labels = {
            'about': 'О какой игре',
            'title': 'Заголовок',
            'content': 'Полное содержание',
            'tag': 'Тег',
            'image': 'Изображение'
        }


class CommentForm (forms.ModelForm):
    text = forms.CharField(
        widget = forms.Textarea(
            attrs = {
                'class': 'form-control',
                'placeholder': 'Напишите свой комментарий здесь',
            }
        )
    )    

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': "Комментарий"}


class updateUserPhoto (forms.ModelForm):
    class Meta:
        model = User
        fields = ('photo',)
