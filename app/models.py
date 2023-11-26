"""
Definition of models.
"""
from django.db import models
from django.contrib import admin
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from random import randint
from datetime import datetime


### shop ###

class Game (models.Model):
    name = models.CharField(
        max_length = 100,
        unique_for_date = "created",
        verbose_name = "Название игры"
    )

    abbreviation = models.CharField(
        max_length = 10,
        verbose_name = "Сокращение игры"
    )

    description = models.TextField(
        verbose_name = "Описание игры"
    )

    theatre = models.CharField(
        max_length = 100,
        verbose_name = "Место действия"
    )

    timeline = models.CharField(
        max_length = 100,
        verbose_name = "Время действия"
    )

    timeline_start = models.IntegerField(
        verbose_name = "Год начала действия"
    )

    timeline_end = models.IntegerField(
        verbose_name = "Год окончания действия"
    )

    tag = models.CharField(
        max_length = 20,
        verbose_name = "Тег игры"
    )

    colour = models.CharField(
        max_length = 7,
        verbose_name = "Цвет тега игры"
    )

    image = models.FileField(
        default = 'temp.jpg',
        verbose_name = 'Логотип игры'
    )

    status_choices = [
        ('not-started'       , 'Не начата'),
        ('planned'           , 'Запланирована'),
        ('closed-development', 'В закрытой разработке'),
        ('open-development'  , 'В открытой разработке'), ### here payments may take place
        ('beta-testing'      , 'Тестирование'),
        ('published'         , 'Опубликована'),
        ('not-supported'     , 'Не поддерживается'),
    ]

    status = models.CharField(
        max_length=20,
        choices = status_choices,
        default = 'not-started',
        verbose_name = "Статус игры"
    )

    price = models.IntegerField(
        default = 0,
        verbose_name = "Цена за копию игры"
    )

    created = models.DateTimeField(
        default = datetime.now(),
        db_index = True,
        verbose_name = "Дата создания"
    )

    published = models.DateTimeField(
        default = datetime.now(),
        db_index = True,
        verbose_name = "Дата публикации"
    )

    class Meta:
        db_table = "Games"
        ordering = [ "-published", "-created" ]
        verbose_name = "Игра"
        verbose_name_plural = "Игры"


class DLC (models.Model):
    name = models.CharField(
        max_length = 100,
        unique_for_date = "published",
        verbose_name = "Название дополнения"
    )

    about = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        verbose_name='Для какой игры'
    )

    image = models.FileField(
        default='temp.jpg',
        verbose_name='Изображение'
    )

    content = models.TextField(
        verbose_name = "Полное содержание"
    )

    price = models.IntegerField(
        default = 0,
        verbose_name = "Цена за дополнение"
    )

    published = models.DateTimeField(
        default = datetime.now(),
        db_index = True,
        verbose_name = "Дата публикации"
    )

    class Meta:
        db_table = "DLCs"
        ordering = [ "-published" ]
        verbose_name = "Дополнение"
        verbose_name_plural = "Дополнения"


class AccessoryTag (models.Model):
    tag = models.CharField(
        max_length = 20,
        verbose_name = "Тег товара"
    )

    colour = models.CharField(
        max_length = 7,
        verbose_name = "Цвет тега товара"
    )

    class Meta:
        db_table = "AccessoryTags"
        ordering = [ "tag" ]
        verbose_name = "Тег товара"
        verbose_name_plural = "Теги товаров"


class Accessory (models.Model):
    name = models.CharField(
        max_length = 100,
        unique_for_date = "created",
        verbose_name = "Название товара"
    )

    about = models.ForeignKey(
        Game,
        default=None,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Для какой игры'
    )

    image = models.FileField(
        default='temp.jpg',
        verbose_name='Изображение'
    )

    content = models.TextField(
        verbose_name = "Полное содержание"
    )

    price = models.IntegerField(
        default = 0,
        verbose_name = "Цена за товар"
    )

    stock = models.IntegerField(
        default = -1, # -1 - unlimited
        verbose_name = "Доступно на заказ"
    )

    virtual = models.BooleanField(
        default = False,
        verbose_name = "Является виртуальным товаром"
    )

    tag = models.ForeignKey(
        AccessoryTag,
        default=None,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Тег'
    )

    created = models.DateTimeField(
        default = datetime.now(),
        db_index = True,
        verbose_name = "Дата создания"
    )

    class Meta:
        db_table = "Accessories"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = [ "-about" ]


### user ###

class User (AbstractUser):
    photo = models.ImageField(
        default = 'unknown_{rnd}.png'.format(rnd = randint(1, 12)),
        verbose_name = 'Фото профиля',
        upload_to = 'media',
    )

    first = models.CharField(
        max_length = 100,
        verbose_name = "Имя"
    )

    last = models.CharField(
        max_length = 100,
        verbose_name = "Фамилия"
    )

    purchased = models.ManyToManyField(
        Game,
        verbose_name = "Купленные игры",
    )

    purchased_DLCs = models.ManyToManyField(
        DLC,
        verbose_name = "Купленные дополнения",
    )

    is_editor = models.BooleanField(
        default = False,
        verbose_name = "Редактор"
    )
    
    class Meta:
        db_table = "Users"
        ordering = [ "username" ]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Order (models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    games = models.ManyToManyField(
        Game,
        verbose_name = "Заказанные игры",
    )

    dlcs = models.ManyToManyField(
        DLC,
        verbose_name = "Заказанные дополнения",
    )

    accessories = models.ManyToManyField(
        Accessory,
        verbose_name = "Заказанные товары",
    )

    meta = models.TextField(
        default = '',
        verbose_name = "Метаданные заказа"
    )

    status_choices = [
        ('auto-resolve' , 'Куплено'               ),

        ('wait-verified', 'Ожидает проверки'      ),
        ('verified'     , 'Проверено'             ),
        ('paid'         , 'Оплачено'              ),
        ('shipped'      , 'Отгружено'             ),
        ('delivered'    , 'Доставлено'            ),
        ('taken'        , 'Получено'              ),

        ('cancelled'    , 'Отменено пользователем'),
        ('denied'       , 'Отменено продавцом'    ),
        ('returned'     , 'Возвращено'            ),
    ]

    status = models.CharField(
        max_length=20,
        choices = status_choices,
        default = 'wait-verified',
        verbose_name = "Статус заказа"
    )

    comment = models.TextField(
        default = "",
        verbose_name = "Комментарий к статусу заказа"
    )

    address = models.TextField(
        default = "",
        verbose_name = "Адрес доставки"
    )

    created = models.DateTimeField(
        default = datetime.now(),
        db_index = True,
        verbose_name = "Дата поступления заказа"
    )

    class Meta:
        db_table = "Orders"
        ordering = [ "-created" ]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


### blog ###

class ArticleTag (models.Model):
    tag = models.CharField(
        max_length = 20,
        verbose_name = "Тег игры"
    )

    colour = models.CharField(
        max_length = 7,
        verbose_name = "Цвет тега игры"
    )

    class Meta:
        db_table = "ArticleTags"
        ordering = [ "tag" ]
        verbose_name = "Тег статьи"
        verbose_name_plural = "Теги статьей"


class Article (models.Model):
    title = models.CharField(
        max_length = 100,
        unique_for_date = "posted",
        verbose_name = "Заголовок"
    )

    image = models.FileField(
        default='temp.jpg',
        verbose_name='Изображение'
    )

    content = models.TextField(
        verbose_name = "Полное содержание"
    )

    posted = models.DateTimeField(
        default = datetime.now(),
        db_index = True,
        verbose_name = "Дата публикации"
    )

    about = models.ForeignKey(
        Game,
        default=None,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='О какой игре'
    )

    tag = models.ForeignKey(
        ArticleTag,
        default=None,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Тег'
    )

    def __str__ (self):
        return self.title

    def get_absolute_url (self):
        return reverse("blogpost", args=[str(self.id)])

    class Meta:
        db_table = "Posts"
        ordering = [ "-posted" ]
        verbose_name = "Статья блога"
        verbose_name_plural = "Статьи блога"


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
        Article,
        on_delete=models.CASCADE,
        verbose_name='Статья комментария'
    )

    class Meta:
        db_table = 'Comment'
        ordering = [ '-date' ]
        verbose_name = 'Комментарий к статье блога'
        verbose_name_plural = 'Комментарии к статьям блога'



admin.site.register(Game)
admin.site.register(DLC)
admin.site.register(AccessoryTag)
admin.site.register(Accessory)

admin.site.register(User)
admin.site.register(Order)

admin.site.register(ArticleTag)
admin.site.register(Article)
admin.site.register(Comment)
