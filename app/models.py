"""
Definition of models.
"""

from django.db import models
from django.contrib import admin
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Game (models.Model):
    name = models.CharField(
        max_length = 100,
        unique_for_date = "created",
        verbose_name = "Название игры"
    )

    short_name = models.CharField(
        max_length = 10,
        verbose_name = "Сокращение игры"
    )

    tag = models.CharField(
        max_length = 30,
        verbose_name = "Тег игры"
    )

    tag_colour = models.CharField(
        max_length = 7,
        verbose_name = "Цвет тега игры"
    )

    image = models.FileField(
        default='temp.jpg',
        verbose_name='Путь к картинке'
    )

    created = models.DateTimeField(
        default = datetime.now(),
        db_index = True,
        verbose_name = "Опубликована"
    )

    class Meta:
        db_table = "Games"
        ordering = ["-created"]
        verbose_name = "игра"
        verbose_name_plural = "игры"


class Blog (models.Model):
    title = models.CharField(
        max_length = 100,
        unique_for_date = "posted",
        verbose_name = "Заголовок"
    )

    image = models.FileField(
        default='temp.jpg',
        verbose_name='Путь к картинке'
    )

    description = models.TextField(
        verbose_name = "Краткое содержание"
    )

    content = models.TextField(
        verbose_name = "Полное содержание"
    )

    posted = models.DateTimeField(
        default = datetime.now(),
        db_index = True,
        verbose_name = "Опубликована"
    )

    about = models.ForeignKey(
        Game,
        default=None,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='О какой игре'
    )

    extra_tag = models.CharField(
        max_length = 30,
        default='статья',
        verbose_name = "Тег темы статьи"
    )

    extra_tag_colour = models.CharField(
        max_length = 7,
        default='#DDDDDD',
        verbose_name = "Цвет тега темы статьи"
    )

    # Методы класса:

    def __str__ (self): # метод возвращает название, используемое для представления отдельных записей в административном разделе
        return self.title

    def get_absolute_url (self): # метод возвращает строку с URL-адресом записи
        return reverse("blogpost", args=[str(self.id)])

    # Метаданные – вложенный класс, который задает дополнительные параметры модели:

    class Meta:
        db_table = "Posts" # имя таблицы для модели
        ordering = ["-posted"] # порядок сортировки данных в модели ("-" означает по убыванию)
        verbose_name = "статья блога" # имя, под которым модель будет отображаться в административном разделе (для одной статьи блога)
        verbose_name_plural = "статьи блога" # тоже для всех статей блога


class Comment (models.Model):
    text = models.TextField(
        verbose_name='Текст комментария'
    )

    date = models.DateTimeField(
        default=datetime.now(),
        db_index=True,
        verbose_name='Дата комментария'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )

    post = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        verbose_name='Статья комментария'
    )

    class Meta:
        db_table = 'Comment'
        ordering = ['-date']
        verbose_name = 'Комментарий к статье блога'
        verbose_name_plural = 'Комментарии к статьям блога'


admin.site.register(Game)
admin.site.register(Blog)
admin.site.register(Comment)
