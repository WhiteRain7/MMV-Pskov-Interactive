"""
Definition of views.
"""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

import sqlite3 as sql

from app import models, forms
from .httpCoroutine import Security, regular, HTTP_error

from datetime import datetime
from math import inf
import json
   
TIMELINE = [
    { 'year': None, 'hex': '#c72727', 'width': '10%'   , 'name': 'BC'          , 'human': 'До н.э.' },
    { 'year': 0   , 'hex': '#beb317', 'width': '18.13%', 'name': 'ancient'     , 'human': 'Античность' },
    { 'year': 476 , 'hex': '#da571b', 'width': '37.22%', 'name': 'middle-ages' , 'human': 'Средневековье' },
    { 'year': 1453, 'hex': '#1e8ccc', 'width': '13.67%', 'name': 'early-modern', 'human': 'Новое время' },
    { 'year': 1812, 'hex': '#13a786', 'width': '6.4%'  , 'name': 'modern'      , 'human': 'Эпоха революций' },
    { 'year': 1980, 'hex': '#9a20ca', 'width': '4.58%' , 'name': 'space-age'   , 'human': 'Эра освоения космоса' },
    { 'year': 2100, 'hex': '#cc27a3', 'width': '10%'   , 'name': 'future'      , 'human': 'Будущее' },
]

def guess_era (year):
    for i in range(len(TIMELINE)-1, 0, -1):
        if year > TIMELINE[i]['year']:
            return TIMELINE[i]
    return TIMELINE[0]

def calculate_position (year):
    if year < TIMELINE[1]['year']: return 5
    elif TIMELINE[-1]['year'] < year: return 95
    else: return 10 + 80 * (year / (TIMELINE[-1]['year'] - TIMELINE[1]['year']))

def calculate_top_position (year):
    era = guess_era(year)
    index = TIMELINE.index(era)
    next_era = TIMELINE[index + 1] if index < len(TIMELINE) - 1 else {}
    
    if index == 0: return 5
    elif index == len(TIMELINE) - 1: return 95
    else: return 100 * (index / len(TIMELINE)) + (100 / len(TIMELINE)) * ((year - era['year']) / (next_era['year'] - era['year']))

def get_timeline (syear, eyear):
    if syear > eyear: syear, eyear = eyear, syear

    timeline = []

    timeline.append({
        'year' : TIMELINE[0]['year' ],
        'hex'  : TIMELINE[0]['hex'  ],
        'width': TIMELINE[0]['width'],
        'name' : TIMELINE[0]['name' ],
        'human': TIMELINE[0]['human'],
        'included': syear <= TIMELINE[1]['year'],
    })

    for i in range(1, len(TIMELINE)):
        era = TIMELINE[i]
        next_era = TIMELINE[i + 1] if i < len(TIMELINE) - 1 else {}

        timeline.append({
            'year' : era['year' ],
            'hex'  : era['hex'  ],
            'width': era['width'],
            'name' : era['name' ],
            'human': era['human'],
            'included': (
                era.get('year', inf) <= eyear
                and
                syear <= next_era.get('year', inf)
            ),
        })

    return timeline


def redirect_home (request): return redirect('home')

def missing_page (request):
    return HTTP_error(request, 404, 'Страница не найдена')

@Security.valid
@Security.allowed_methods([ 'GET' ])
@Security.access_level(0)
def home (request):
    """
        Renders the home page.
    """

    return render(
        request,
        'app/index.html',
        {
            **regular('home'),
            'games': models.Game.objects.all(),
            'articles': models.Article.objects.all()[:3]
        }
    )

@Security.valid
@Security.allowed_methods([ 'GET' ])
@Security.access_level(0)
def about (request):
    """
        Renders the about page.
    """
    
    return render(
        request,
        'app/pages/presentation/about.html',
        {
            **regular('about'),
        }
    )

@Security.valid
@Security.allowed_methods([ 'GET' ])
@Security.access_level(0)
def videos (request):
    """
        Renders the video page.
    """

    return render(
        request,
        'app/pages/presentation/videos.html',
        {
            **regular('videos'),
        }
    )

@Security.valid
@Security.allowed_methods([ 'GET', 'POST' ])
@Security.access_level(0, exact = True, redirecting = 'home')
def sign_in (request):
    """
        Renders the authorization page.
    """

    if request.method == "POST":
        form = forms.SignInForm(request.POST)

        if form.is_valid():
            saved = form.save(commit=False)

            saved.last_login = datetime.now()

            saved.save()

            user = authenticate(
                username = saved.cleaned_data['username'], 
                password = saved.cleaned_data['password']
            )
            login(request, user)

            return redirect('home')

    return render(
        request,
        'app/pages/auth/sign-in.html',
        {
            **regular('login'),
            'form': forms.SignInForm()
        }
    )

@Security.valid
@Security.allowed_methods([ 'GET', 'POST' ])
@Security.access_level(0, exact = True, redirecting = 'home')
def sign_up (request):
    """
        Renders the registration page.
    """

    if request.method == "POST":
        form = forms.SignUpForm(request.POST)

        if form.is_valid():
            saved = form.save(commit=False)

            try: saved.photo = request['photo']
            except: pass
            saved.is_staff = False
            saved.is_active = True
            saved.is_superuser = False
            saved.date_joined = datetime.now()
            saved.last_login = datetime.now()

            saved.save()

            user = authenticate(
                username = saved.username,
                password = form.data['password1']
            )
            login(request, user)

            return redirect('home')

    return render(
        request,
        'app/pages/auth/sign-up.html',
        {
            **regular('registration'),
            'form': forms.SignUpForm(),
        }
    )

@Security.valid
@Security.exists(models.User)
@Security.allowed_methods([ 'GET' ])
@Security.access_level(1)
def profile (request, id = None):
    """
        Renders the profile page.
    """

    statuses = {
        'auto-resolve' : {
            'title': 'Куплено',
            'colour': 'green',
            'icon': 'check',
            'short_descr': 'Указанные товары куплены без дополнительного подтверждения.',
        },

        'wait-verified': {
            'title': 'Ожидает проверки',
            'colour': 'orange',
            'icon': 'clock',
            'short_descr': 'Заказ ожидает подтверждения от продавца.',
        },

        'verified' : {
            'title': 'Проверено',
            'colour': 'darkcyan',
            'icon': 'check',
            'short_descr': 'Заказ подтвержден продавцом и ожидает оплаты.',
        },

        'paid' : {
            'title': 'Оплачено',
            'colour': 'turtle',
            'icon': 'check',
            'short_descr': 'Заказ оплачен и ожидает отгрузки.',
        },

        'shipped' : {
            'title': 'Отгружено',
            'colour': 'indigo',
            'icon': 'check',
            'short_descr': 'Заказ отгружен и ожидает доставки по адресу получателя.',
        },

        'delivered' : {
            'title': 'Доставлено',
            'colour': 'darkgreen',
            'icon': 'check',
            'short_descr': 'Заказ доставлен до адреса и ожидает получения.',
        },

        'taken' : {
            'title': 'Получено',
            'colour': 'green',
            'icon': 'check',
            'short_descr': 'Заказ успешно получен и оплачен.',
        },

        'cancelled' : {
            'title': 'Отменено пользователем',
            'colour': 'darkred',
            'icon': 'cancel',
            'short_descr': 'Заказ отменен пользователем.',
        },

        'denied' : {
            'title': 'Отменено продавцом',
            'colour': 'orangered',
            'icon': 'cancel',
            'short_descr': 'Заказ отменен продавцом.',
        },

        'returned' : {
            'title': 'Возвращено',
            'colour': 'red',
            'icon': 'cancel',
            'short_descr': 'Заказ возвращен продавцу.',
        }
    }

    profile = models.User.objects.get(id = id) if id else request.user
    orders = (
        models.Order.objects.filter(user = profile)
        if profile.id == request.user.id or request.user.is_staff or request.user.is_editor else
        None
    )
    parsed_orders = None

    if orders:
        parsed_orders = []

        for order in orders:
            parsed_order = {
                'id': order.id,
                'created': order.created,
                'raw-status': order.status,
                'status': statuses[order.status],
                'address': order.address,
                'comment': order.comment,
                'meta': json.loads(order.meta),
                'products': []
            }

            for game in order.games.all(): parsed_order['products'].append({
                'type': 'game',
                'name': game.name,
                'image': game.image,
                'quantity': parsed_order['meta']['g' + str(game.id)]['q'],
                'price': parsed_order['meta']['g' + str(game.id)]['p'],
                'total': parsed_order['meta']['g' + str(game.id)]['q'] * parsed_order['meta']['g' + str(game.id)]['p'],
            })
                
            for dlc in order.dlcs.all(): parsed_order['products'].append({
                'type': 'dlc',
                'name': dlc.name,
                'image': dlc.image,
                'quantity': parsed_order['meta']['d' + str(dlc.id)]['q'],
                'price': parsed_order['meta']['d' + str(dlc.id)]['p'],
                'total': parsed_order['meta']['d' + str(dlc.id)]['q'] * parsed_order['meta']['d' + str(dlc.id)]['p'],
            })
                
            for acc in order.accessories.all(): parsed_order['products'].append({
                'type': 'accessory',
                'name': acc.name,
                'image': acc.image,
                'quantity': parsed_order['meta']['a' + str(acc.id)]['q'],
                'price': parsed_order['meta']['a' + str(acc.id)]['p'],
                'total': parsed_order['meta']['a' + str(acc.id)]['q'] * parsed_order['meta']['a' + str(acc.id)]['p'],
            })
                
            parsed_order['sum'] = sum(product['total'] for product in parsed_order['products'])

            parsed_orders.append(parsed_order)

    games = models.Game.objects.all()

    for game in games:
        game.is_visible = (game.status != 'not-started' and game.status != 'planned')
        game.DLCs = models.DLC.objects.filter(about = game.id)

    return render(
        request,
        'app/pages/profile/profile.html',
        {
            **regular('profile'),
            'profile': profile,
            'orders': parsed_orders,
            'itself': parsed_orders is not None,
            'statuses': statuses,
            'games': games
        }
    )

@Security.valid
@Security.exists(models.User)
@Security.allowed_methods([ 'POST', 'PUT', 'PATCH' ])
@Security.access_level(1)
def edit_profile (request):
    """
        Edits profile with given data
    """

    if (
        not request.headers.get('referrer').endswith('/profile') or
        not request.user.is_staff
    ):
        return HttpResponse(status = 403)

    user = models.User.objects.get(id = request.user.id)

    form = forms.updateUserPhoto(request)

    if form.is_valid():
        user.photo = request.FILES['photo']
        user.save()

    return HttpResponse(status = 200)

@Security.valid
@Security.allowed_methods([ 'GET' ])
@Security.access_level(0)
def news (request, tag = None):
    """
        Renders the posts page.
    """
    assert isinstance(request, HttpRequest)

    game_tags = [
        {
            'tag': game.tag,
            'colour': game.colour
        } for game in models.Game.objects.all()
    ]

    extra_tags = [
        {
            'tag': article_tag.tag,
            'colour': article_tag.colour
        } for article_tag in models.ArticleTag.objects.all()
    ]

    if tag is None:
        articles = models.Article.objects.all()

    else:
        articles = []

        for game in models.Game.objects.filter(tag = tag):
            articles += models.Article.objects.filter(about = game.id)

        if not articles:
            article_tag = models.ArticleTag.objects.get(tag = tag)
            articles.extend(models.Article.objects.filter(tag = article_tag))


    return render(
        request,
        'app/pages/news/articles.html',
        {
            **regular('news'),
            'articles': articles,
            'filter_tag': tag,
            'game_tags': game_tags,
            'extra_tags': extra_tags,
        }
    )

@Security.valid
@Security.exists(models.Article)
@Security.allowed_methods([ 'GET' ])
@Security.access_level(0)
def article (request, id):
    """
        Renders the blogpost page.
    """
    assert isinstance(request, HttpRequest)

    article = models.Article.objects.get(id = id)
    comments = models.Comment.objects.filter(post = id)
    form = forms.CommentForm()

    return render(
        request,
        'app/pages/news/article.html',
        {
            **regular('news'),
            'article': article,
            'comments': comments,
            'form': form,
        }
    )

@Security.valid
@Security.allowed_methods([ 'POST' ])
@Security.access_level(1)
def comment (request, id):
    """
        Processes the comment form.
    """
    assert isinstance(request, HttpRequest)

    if request.method == "POST":
        form = forms.CommentForm(request.POST)

        if form.is_valid():
            saved = form.save(commit=False)

            saved.date = datetime.now()
            saved.post = models.Article.objects.get(id = id)
            saved.author = request.user

            saved.save()

    return redirect('article', id)

@Security.valid
@Security.allowed_methods([ 'GET' ])
@Security.access_level(0)
def store (request):
    """
        Renders the store page.
    """
    assert isinstance(request, HttpRequest)

    games = models.Game.objects.all()

    status_choices = {
        'not-started': 'Не начата',
        'planned': 'Запланирована',
        'closed-development': 'В закрытой разработке',
        'open-development': 'В открытой разработке',
        'beta-testing': 'Тестирование',
        'published': '',
        'not-supported': 'Не поддерживается',
    }

    for game in games:
        game.is_visible = (game.status != 'not-started' and game.status != 'planned')
        game.is_purchasable = game.is_visible and game.status != 'closed-development'
        try: game.is_purchased = game in request.user.purchased.all()
        except: game.is_purchased = False
        game.status = status_choices[game.status]

        game.DLCs = models.DLC.objects.filter(about = game.id)
        for DLC in game.DLCs:
            try: DLC.is_purchased = DLC in request.user.purchased_DLCs.all()
            except: DLC.is_purchased = False

        game.timeline_data = {
            'timeline': get_timeline(game.timeline_start, game.timeline_end),
            'start': {
                'year': game.timeline_start,
                'pos': str(calculate_position(game.timeline_start)) + '%',
                'top': str(calculate_top_position(game.timeline_start)) + '%',
                'era': guess_era(game.timeline_start),
            },
            'end': {
                'year': game.timeline_end,
                'pos': str(calculate_position(game.timeline_end)) + '%',
                'top': str(calculate_top_position(game.timeline_end)) + '%',
                'era': guess_era(game.timeline_end),
            }
        }

    accessories = models.Accessory.objects.all()

    products = {}

    for game in games:
        products['g' + str(game.id)] = {
            'type': 'game',
            'name': game.name,
            'image': game.image.url,
            'price': game.price,
        }
        
        for DLC in game.DLCs: products['d' + str(DLC.id)] = {
            'type': 'dlc',
            'name': DLC.name,
            'image': DLC.image.url,
            'price': DLC.price,
        }
        
    for acc in accessories: products['a' + str(acc.id)] = {
        'type': 'accessory',
            'name': acc.name,
            'image': acc.image.url,
            'price': acc.price,
            'limit': acc.stock
    }

    return render(
        request,
        'app/pages/store/store.html',
        {
            **regular('store'),
            'games': games,
            'accessories': accessories,
            'products': products,
        }
    )

@Security.valid
@Security.allowed_methods([ 'POST' ])
@Security.access_level(1)
def order (request):
    """
        Places the order.
    """

    assert isinstance(request, HttpRequest)

    if request.method != "POST": return None

    body = json.loads(request.read())

    games = []
    dlcs = []
    accessories = []

    meta = {}

    for id_ in body['cart']:
        if id_[0] == 'g': games.append(models.Game.objects.get(id = id_[1:]))
        if id_[0] == 'd': dlcs.append(models.DLC.objects.get(id = id_[1:]))
        if id_[0] == 'a': accessories.append(models.Accessory.objects.get(id = id_[1:]))

        meta[id_] = {
            'q': int(body['cart'][id_]),
            'p': games[-1].price if id_[0] == 'g' else dlcs[-1].price if id_[0] == 'd' else accessories[-1].price,
        }

    order = models.Order.objects.create(
        user = request.user,
        meta = json.dumps(meta),
        status = 'auto-resolve' if len(accessories) == 0 else 'wait-verified',
        address = body['address'],
    )

    order.games.set(games)
    order.dlcs.set(dlcs)
    #order.accessories.set(accessories)

    # please forgive me for all the sins I've made here, I just have to do it
    connection = sql.connect('db.sqlite3')
    connection.executemany('INSERT INTO Orders_accessories (order_id, accessory_id) VALUES (?, ?)', [(order.id, accessory.id) for accessory in accessories])
    connection.commit()
    connection.close()

    user = models.User.objects.get(id = request.user.id)
    for game in games: user.purchased.add(game)
    for DLC in dlcs: user.purchased_DLCs.add(DLC)
    user.save(force_update=True)

    return HttpResponse(status = 200)

@Security.valid
@Security.exists(models.Order)
@Security.allowed_methods([ 'POST' ])
@Security.access_level(2)
def update_order_status (request, id):
    """
        Updates order status.
    """

    assert isinstance(request, HttpRequest)

    if request.method != "POST": return HttpResponse(status = 405)
    if not (request.user.is_staff or request.user.is_editor): return HttpResponse(status = 403)

    body = json.loads(request.read())

    order = models.Order.objects.get(id = id)
    order.status = body['status']
    order.comment = body['comment']
    order.save(force_update=True)

    return HttpResponse(status = 200)

@Security.valid
@Security.allowed_methods([ 'GET' ])
@Security.access_level(2)
def manage (request):
    """
        Renders the manage page.
    """

    assert isinstance(request, HttpRequest)

    statuses = {
        'auto-resolve' : {
            'title': 'Куплено',
            'colour': 'green',
            'icon': 'check',
            'short_descr': 'Указанные товары куплены без дополнительного подтверждения.',
        },

        'wait-verified': {
            'title': 'Ожидает проверки',
            'colour': 'orange',
            'icon': 'clock',
            'short_descr': 'Заказ ожидает подтверждения от продавца.',
        },

        'verified' : {
            'title': 'Проверено',
            'colour': 'darkcyan',
            'icon': 'check',
            'short_descr': 'Заказ подтвержден продавцом и ожидает оплаты.',
        },

        'paid' : {
            'title': 'Оплачено',
            'colour': 'turtle',
            'icon': 'check',
            'short_descr': 'Заказ оплачен и ожидает отгрузки.',
        },

        'shipped' : {
            'title': 'Отгружено',
            'colour': 'indigo',
            'icon': 'check',
            'short_descr': 'Заказ отгружен и ожидает доставки по адресу получателя.',
        },

        'delivered' : {
            'title': 'Доставлено',
            'colour': 'darkgreen',
            'icon': 'check',
            'short_descr': 'Заказ доставлен до адреса и ожидает получения.',
        },

        'taken' : {
            'title': 'Получено',
            'colour': 'green',
            'icon': 'check',
            'short_descr': 'Заказ успешно получен и оплачен.',
        },

        'cancelled' : {
            'title': 'Отменено пользователем',
            'colour': 'darkred',
            'icon': 'cancel',
            'short_descr': 'Заказ отменен пользователем.',
        },

        'denied' : {
            'title': 'Отменено продавцом',
            'colour': 'orangered',
            'icon': 'cancel',
            'short_descr': 'Заказ отменен продавцом.',
        },

        'returned' : {
            'title': 'Возвращено',
            'colour': 'red',
            'icon': 'cancel',
            'short_descr': 'Заказ возвращен продавцу.',
        }
    }

    orders = models.Order.objects.all()
    parsed_orders = None

    if orders:
        parsed_orders = []

        for order in orders:
            parsed_order = {
                'id': order.id,
                'created': order.created,
                'user': order.user,
                'raw_status': order.status,
                'status': statuses[order.status],
                'address': order.address,
                'comment': order.comment,
                'meta': json.loads(order.meta),
                'products': []
            }

            for game in order.games.all(): parsed_order['products'].append({
                'type': 'game',
                'name': game.name,
                'image': game.image,
                'quantity': parsed_order['meta']['g' + str(game.id)]['q'],
                'price': parsed_order['meta']['g' + str(game.id)]['p'],
                'total': parsed_order['meta']['g' + str(game.id)]['q'] * parsed_order['meta']['g' + str(game.id)]['p'],
            })
                
            for dlc in order.dlcs.all(): parsed_order['products'].append({
                'type': 'dlc',
                'name': dlc.name,
                'image': dlc.image,
                'quantity': parsed_order['meta']['d' + str(dlc.id)]['q'],
                'price': parsed_order['meta']['d' + str(dlc.id)]['p'],
                'total': parsed_order['meta']['d' + str(dlc.id)]['q'] * parsed_order['meta']['d' + str(dlc.id)]['p'],
            })
                
            for acc in order.accessories.all(): parsed_order['products'].append({
                'type': 'accessory',
                'name': acc.name,
                'image': acc.image,
                'quantity': parsed_order['meta']['a' + str(acc.id)]['q'],
                'price': parsed_order['meta']['a' + str(acc.id)]['p'],
                'total': parsed_order['meta']['a' + str(acc.id)]['q'] * parsed_order['meta']['a' + str(acc.id)]['p'],
            })
                
            parsed_order['sum'] = sum(product['total'] for product in parsed_order['products'])

            parsed_orders.append(parsed_order)

    games = models.Game.objects.all()

    for game in games:
        game.is_visible = (game.status != 'not-started' and game.status != 'planned')
        game.DLCs = models.DLC.objects.filter(about = game.id)

    return render(
        request,
        'app/pages/manage/manage.html',
        {
            **regular('manage'),
            'min_orders': [{ 'id': o['id'], 'comment': o['comment'] } for o in parsed_orders],
            'orders': parsed_orders,
            'statuses': statuses,
            'games': games
        }
    )
