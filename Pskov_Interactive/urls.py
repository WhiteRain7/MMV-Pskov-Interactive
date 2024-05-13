"""
Definition of urls for Pskov_Interactive.
"""

from datetime import datetime
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from app import forms, views

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    path('', views.home, name = 'home'),
    path('about/', views.about, name = 'about'),
    path('videos/', views.videos, name='videos'),
    path('auth/sign-in/',
         LoginView.as_view(
             template_name = 'app/pages/auth/sign-in.html',
             authentication_form = forms.SignInForm,
             extra_context = { 'year' : datetime.now().year, 'page': 'login', 'page_title': 'Вход' },
         ),
         name='sign-in'),
    path('auth/sign-up/', views.sign_up, name = 'sign-up'),
    path('auth/sign-out/', LogoutView.as_view(next_page='/auth/sign-in/'), name = 'sign-out'),
    path('profile/<int:id>/', views.profile, name='profile'),
    path('profile/', views.profile, name='profile'),
    path('news/', views.news, name='news'),
    path('news/<str:tag>/', views.news, name='news'),
    path('news/article/<int:id>', views.article, name='article'),
    path('news/comment/<int:id>', views.comment, name='comment'),
    path('store/', views.store, name='store'),
    path('accounts/profile/', views.redirect_home, name='redirect_home'),

    path('edit/profile/', views.edit_profile, name='edit_profile'),
    path('place/order/', views.order, name='order'),
    path('update/order/<int:id>', views.update_order_status, name='update_order'),

    path('manage/', views.manage, name='manage'),
    path('manage/games/', views.manage_games, name='manage_games'),
    path('manage/game/<int:id>', views.manage_game, name='manage_game'),
    path('manage/dlcs/', views.manage_dlcs, name='manage_dlcs'),
    path('manage/dlc/<int:id>', views.manage_dlc, name='manage_dlc'),
    path('manage/accessories/', views.manage_accessories, name='manage_accessories'),
    path('manage/accessory/<int:id>', views.manage_accessory, name='manage_accessory'),
    path('manage/news/', views.manage_news, name='manage_news'),
    path('manage/article/<int:id>', views.manage_article, name='manage_article'),
    path('manage/users/', views.manage_users, name='manage_users'),
    path('manage/user/<int:id>', views.manage_user, name='manage_user'),
    path('manage/orders/', views.manage_orders, name='manage_orders'),

    path('admin/', admin.site.urls, name='admin')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

urlpatterns += [ re_path('.*', views.missing_page, name='missing_page') ]
