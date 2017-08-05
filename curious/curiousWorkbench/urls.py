import sys
import os
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
import ajax
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

from django.conf.urls import url
from django.conf import settings
from django.views.generic import TemplateView

import views
import ajax
from views import *
from ajax import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^ajax/add/$',add_todo, name='add_todo'),
    url(r'^ajax/more/$',more_todo, name='more_todo'),
    url(r'^ajax/search/$',searchContacts, name='searchContacts'),
    url(r'^ajax/details/$',details, name='details'),
    url(r'^login/', user_login, name="user_login"),
    url(r'^handleActions/', views.handleActions, name='handleActions'),

]
