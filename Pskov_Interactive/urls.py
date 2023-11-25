"""
Definition of urls for Pskov_Interactive.
"""

from datetime import datetime
from django.urls import path
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
    path('auth/sign-out/', LogoutView.as_view(next_page='/auth/sign-in'), name = 'sign-out'),
    path('admin/', admin.site.urls),
    path('news/', views.news, name='news'),
    path('news/<str:tag>/', views.news, name='news'),
    path('news/article/<int:id>', views.article, name='article'),
    path('news/comment/<int:id>', views.comment, name='comment'),
    path('store/', views.store, name='store'),
    path('accounts/profile/', views.redirect_home, name='redirect_home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
