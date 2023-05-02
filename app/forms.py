"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.db import models
from .models import Game, Blog, Comment

class BootstrapAuthenticationForm(AuthenticationForm):
    """
        Authentication form which uses boostrap CSS.
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput({
            'class': 'form-control',
            'placeholder': 'Введите логин',
            'title': 'Введите ваш уникальный логин, который вы указывали при регистрации'
        }))

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput({
            'class': 'form-control',
            'placeholder':'Введите пароль',
            'title': 'Укажите ваш пароль, который вы указывали при регистрации'
        }))


class FeedbackForm (forms.Form):
    '''
        Feedback form
    '''
    game = forms.ChoiceField(
        choices=[(game.id, game.name) for game in Game.objects.all()],
        required=True,
        initial=None,
        help_text='Укажите игру, к которой хотите написать отзыв'
    )

    mark = forms.IntegerField(
        min_value=1,
        max_value=10,
        required=True,
        initial=None,
        widget=forms.NumberInput({
            'class': 'form-control',
            'title': 'Укажите оценку от 1 (полностью не нравится) до 10 (полностью нравится)',
            'min': '1',
            'max': '10',
            'step': '1',
        })
    )

    details_good = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.Textarea({
            'class': 'form-control',
            'placeholder': 'Что вам нравится в продукте?',
            'title': 'Напишите дополнительную информацию о том, что вам нравится',
            'maxlength': '2000',
        })
    )

    details_bad = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.Textarea({
            'class': 'form-control',
            'placeholder': 'Что вам не нравится в продукте?',
            'title': 'Напишите дополнительную информацию о том, что вам не нравится',
            'maxlength': '2000',
        })
    )

    email_allowed = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput({
            'class': 'form-control',
            'title': 'Хотите ли вы, чтобы мы могли связаться с вами по поводу уточнения деталей отзыва? (также укажите почту)',
            'onchange': 'switch_contact_display()',
        })
    )

    contact = forms.EmailField(
        required=False,
        widget=forms.EmailInput({
            'class': 'form-control',
            'title': 'Укажите почту, на которую мы можем написать при необходимости уточнить детали по вашему отзыву (также поставьте галочку)',
        })
    )

class BlogForm (forms.ModelForm):
    '''about = forms.ChoiceField(
        choices=[('', 'Не относится')] + [(game.id, game.name) for game in Game.objects.all()],
        required=True,
        initial=None,
        help_text='Укажите игру, к которой хотите написать новость'
    )'''

    class Meta:
        model = Blog
        fields = {
            'title',
            'description',
            'content',
            'about',
            'extra_tag',
            'extra_tag_colour',
            'image'
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Краткое содержание',
            'content': 'Полное содержание',
            'about': 'Относится к',
            'extra_tag': 'Дополнительный тег',
            'extra_tag_colour': 'Цвет тега',
            'image': 'Картинка'
        }

class CommentForm (forms.ModelForm):
    class Meta:
        model = Comment # используемая модель
        fields = ('text',) # требуется заполнить только поле text
        labels = {'text': "Комментарий"} # метка к полю формы text
