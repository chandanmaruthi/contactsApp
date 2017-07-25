import sys
import os
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

from django.conf.urls import url
from django.conf import settings
from django.views.generic import TemplateView

import views
import viewFacebook
import viewSlack
from viewFacebook import fbClientAriseBotView
from viewSlack import slackClientWalnutBotView


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup/', views.user_signup, name="user_signup"),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^accounts/$', include('registration.backends.default.urls')),
    url(r'^accounts/$', include('registration.backends.default.urls')),
    url(r'^accounts/$', include('django.contrib.auth.urls')),
    url(r'^login/', views.user_login, name="user_login"),
    url(r'^successfullInstall/', views.successfullInstall, name="successfullInstall"),
    url(r'^webHome/', views.webHome, name="webHome"),
    url(r'^webManageModule/', views.webHome, name="webHome"),
    url(r'^logout/', views.user_logout, name="user_logout"),
    url(r'^fbABWCV/(?P<content_Id>\d+)/(?P<user_Id>\w+)/$', views.fbAriseBotContentWebView, name='fbAriseBotContentWebView'),
    url(r'^myProfile/(?P<userID>\w+)/$', views.fbAriseBotCertWebView, name='fbAriseBotCertWebView'),
    url(r'^analytics/(?P<userID>\w+)/$', views.fbAriseBotCertWebView, name='fbAriseBotCertWebView'),
    url(r'^displayPVPolicy/', views.displayPVPolicy, name="displayPVPolicy"),
    url(r'^displayTnC/', views.displayTnC, name="displayTnC"),
    url(r'^installApp/', views.installApp, name="installApp"),
    url(r'^fbABReminder/(?P<passID>\d+)/$', views.fbAriseBotReminder,name='fbAriseBotReminder'),
    url(r'^configUsers/', views.configUsers, name='configUsers'),
    url(r'^configSettings/', views.configSettings, name='configSettings'),
    url(r'^saveSettings/', views.saveSettings, name='saveSettings'),
    url(r'^configBot/', views.configBot, name='configBot'),
    url(r'^configStateMachine/', views.configStateMachine, name='configStateMachine'),
    url(r'^addStateMachineSubscription/', views.addStateMachineSubscription, name='addStateMachineSubscription'),
    url(r'^deleteStateMachineSubscription/(?P<SM_ID>\d+)/$', views.deleteStateMachineSubscription, name='deleteStateMachineSubscription'),
    url(r'^editStateMachineSubscription/(?P<SM_ID>\d+)/$', views.editStateMachineSubscription, name='editStateMachineSubscription'),
    url(r'^editTestChat/', views.editTestChat, name='editTestChat'),
    url(r'^editContentLibrary/(?P<ID>\d+)/$', views.editContentLibrary, name='editContentLibrary'),
    url(r'^deleteContentLibrary/(?P<ID>\d+)/$', views.deleteContentLibrary, name='deleteContentLibrary'),
    url(r'^configMessageLibrary/', views.configMessageLibrary, name='configMessageLibrary'),
    url(r'^editMessageLibrary/(?P<ID>\d+)/$', views.editMessageLibrary, name='editMessageLibrary'),
    url(r'^deleteMessageLibrary/(?P<ID>\d+)/$', views.deleteMessageLibrary, name='deleteMessageLibrary'),
    url(r'^addMessageLibrary/', views.addMessageLibrary, name='addMessageLibrary'),
    url(r'^configContentLibrary/', views.configContentLibrary, name='configContentLibrary'),
    url(r'^editContentLibrary/(?P<ID>\d+)/$', views.editContentLibrary, name='editContentLibrary'),
    url(r'^deleteContentLibrary/(?P<ID>\d+)/$', views.deleteContentLibrary, name='deleteContentLibrary'),
    url(r'^addContentLibrary/', views.addContentLibrary, name='addContentLibrary'),
    url(r'^saveStateMachine/(?P<SM_ID>\d+)/$', views.saveStateMachine, name='saveStateMachine'),
    url(r'^saveStateMachine/', views.saveStateMachine, name='saveStateMachine'),
    url(r'^saveMessageLibrary/(?P<ID>\d+)/$', views.saveMessageLibrary, name='saveMessageLibrary'),
    url(r'^saveMessageLibrary', views.saveMessageLibrary, name='saveMessageLibrary'),
    url(r'^saveContentLibrary/(?P<ID>\d+)/$', views.saveContentLibrary, name='saveContentLibrary'),
    url(r'^saveContentLibrary/', views.saveContentLibrary, name='saveContentLibrary'),
    url(r'^handleActions/', views.handleActions, name='handleActions'),
    url(r'^configModule/', views.configModule, name='configModule'),
    url(r'^topics/', views.configModule, name='configModule'),
    url(r'^uploadContent/(?P<ModuleID>\d+)/$', views.uploadContent, name='uploadContent'),
    url(r'^editModule/(?P<ID>\d+)/$', views.editModule, name='editModule'),
    url(r'^deleteModule/(?P<ID>\d+)/$', views.deleteModule, name='deleteModule'),
    url(r'^addModule/', views.addModule, name='addModule'),
    url(r'^saveModule/(?P<ID>\d+)/$', views.saveModule, name='saveModule'),
    url(r'^saveModule/', views.saveModule, name='saveModule'),
    url(r'^slackWebhookWalnutBot/$', viewSlack.slackClientWalnutBotView.as_view()),
    url(r'^fbWebhookAriseBot/$', viewFacebook.fbClientAriseBotView.as_view() ),
    url(r'^slackAuth/$', views.slackAuth, name="slackAuth"),

]
