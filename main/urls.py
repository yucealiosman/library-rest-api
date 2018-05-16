# -*- coding: utf-8 -*-
from django.conf.urls import url
from main.views import Book, Author
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^library$', views.library, name='library'),
    url(r'^book/$', Book.as_view(), name='book'),
    url(r'^author/$', Author.as_view(), name='author'),
    url(r'^book/(?P<book_id>[\w-]+)$', Book.as_view(), name='book'),
    url(r'^author/(?P<author_id>[\w-]+)$', Author.as_view(), name='author_id'),

]

