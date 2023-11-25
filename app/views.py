"""
Definition of views.
"""
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from app import models, forms

from datetime import datetime
from math import inf

def regular (page):
    pages = {
        'home' : 'Домашняя страница',
        'about' : 'О компании',
        'videos': 'Видео',
        'news': 'Новости',
        'store': 'Магазин',
        'login': 'Вход',
        'registration': 'Регистрация',
    }

    return {
        'year': datetime.now().year,
        'page': page,
        'page_title': pages[page]
    }
    
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

def home (request):
    """
        Renders the home page.
    """
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/index.html',
        {
            **regular('home'),
            'games': models.Game.objects.all(),
            'articles': models.Article.objects.all()[:3]
        }
    )

def about (request):
    """
        Renders the about page.
    """
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/pages/presentation/about.html',
        {
            **regular('about'),
        }
    )
    
def videos (request):
    """
        Renders the video page.
    """
    assert isinstance(request, HttpRequest)

    return render(
        request,
        'app/pages/presentation/videos.html',
        {
            **regular('videos'),
        }
    )

def sign_in (request):
    """
        Renders the authorization page.
    """
    assert isinstance(request, HttpRequest)

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

def sign_up (request):
    """
        Renders the registration page.
    """
    assert isinstance(request, HttpRequest)

    if request.method == "POST":
        form = forms.SignUpForm(request.POST)

        if form.is_valid():
            saved = form.save(commit=False)

            if form.cleaned_data['photo']: saved.photo = form.cleaned_data['photo']
            saved.is_staff = False
            saved.is_active = True
            saved.is_superuser = False
            saved.date_joined = datetime.now()
            saved.last_login = datetime.now()

            saved.save()

            # user = authenticate(
            #     username = saved.username,
            #     password = saved.password
            # )
            # login(request, user)

            return redirect('home')

    return render(
        request,
        'app/pages/auth/sign-up.html',
        {
            **regular('registration'),
            'form': forms.SignUpForm(),
        }
    )

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
        game.status = status_choices[game.status]

        game.DLCs = models.DLC.objects.filter(about = game.id)

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

    return render(
        request,
        'app/pages/store/store.html',
        {
            **regular('store'),
            'games': games,
            'accessories': accessories,
        }
    )
