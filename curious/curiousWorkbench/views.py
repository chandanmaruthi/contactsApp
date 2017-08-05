import sys
import os
import datetime
from django.db.models import Count
import ast
import base64


dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
import csv
from django.db import transaction
from django.contrib.auth.models import AnonymousUser
#sys.path.append(dir_path + "/customViews")
from django.views.decorators.csrf import requires_csrf_token
import magic
from random import randint
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.html import escape
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.context_processors import csrf
#from django.template import RequestContext, loader
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import get_object_or_404, render, render_to_response
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
#from networkBuilder import Network
from django.contrib.auth import authenticate, login, logout
from models import UserState, UserSkillStatus
#from models import StateMachine, MessageLibrary, ContentLibrary, Module, UserCertification, Progress, PlatformCredentials, Challenge, SignUp,UserActions
import urllib
import urllib2
from django.core.files.storage import FileSystemStorage
from itertools import *
from django.db import connection
from django.utils.safestring import SafeUnicode

#import redis
import StringIO
import random
import os
import time
import sys
import json
import requests
import subprocess
from django.http import Http404, HttpResponse
import json
import requests
import random
import re
from pprint import pprint

from configSettings import configSettings
from django.views import generic
import logging

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import mixpanel
from mixpanel import Mixpanel
import plotly.plotly as py
import plotly.graph_objs as go
#import curiousWorkbench.clientFacebook


mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")


configSettingsObj = configSettings()
#----------------Logging ------------------
logger = logging.getLogger('views')
hdlr = logging.FileHandler(configSettingsObj.logFolderPath + 'views.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
logger.info('logging log folder path views.py')
rootURL = configSettingsObj.webUrl
# logger.info(configSettingsObj.logFolderPath)
#----------------Logging ------------------


def query_to_dicts(query_string, *query_args):
    cursor = connection.cursor()
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        yield row_dict
    return





@csrf_exempt
def user_login(request):
    state = "Please log in below..."
    username = ''
    password = ''
    if request.POST:
        if 'LoginFormSubmit':
            username = request.POST["username"]
            password = request.POST["password"]

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    state = "You're successfully logged in!"
                else:
                    state = "Your account is not active, please contact the site admin."

                template = get_template('curiousWorkbench/index.html')
                contextDict =  {
                    'rootURL' : rootURL,
                    'state': state,
                }
                return HttpResponse(template.render(contextDict))
            else:
                state = "Your username and/or password were incorrect."
                template = get_template('curiousWorkbench/login.html')
                contextDict =  {
                    'rootURL' : rootURL,
                    'state': state,
                }
                return HttpResponse(template.render(contextDict))

    #state = "error occured."
    template = get_template('curiousWorkbench/login.html')
    contextDict =  {
        'rootURL' : rootURL,
        'state': state,
        'UserName': request.user.username,
    }

    return HttpResponse(template.render(contextDict))

@csrf_exempt
def user_signup(request):
    SignUpState=""
    userEmail=''
    if request.POST:
        if request.POST:
            state = "NA"
            userEmail = request.POST["userEmail"]
            try:
                validate_email(userEmail)
            except ValidationError as e:
                SignUpState =  "oops! invalid email id"
            else:

                userSignUpObj  = SignUp.objects.filter(UserEmail=userEmail.strip())
                if len(userSignUpObj)>0:
                    SignUpState = "You have already signed up, please wait"
                else:

                    userSignUpObj = SignUp()
                    userSignUpObj.UserEmail= userEmail
                    userSignUpObj.save()

                    SignUpState = "You have been added to the early beta, we will let you know soon"


    #state = "error occured."
    template = get_template('curiousWorkbench/login.html')
    contextDict =  {
        'rootURL' : rootURL,
        'SignUpState': SignUpState,
        'state':""

    }

    # context.update(csrf(request))

    return HttpResponse(template.render(contextDict))





@csrf_exempt
@login_required
def webHome(request):
    state = "Please log in below..."
    username = ''
    password = ''
    logger.info("hello1")
    if request.POST:
        logger.info("hello")
        logger.info(str(request.FILES.items()))
        for a in request.FILES:
            logger.info(str(a))
        if 'FileUpload' in request.FILES:
            myfile = request.FILES['FileUpload']
            fs = FileSystemStorage()
            filePath = configSettingsObj.appFolderPath() + "/UserContent/FileUploads/" + myfile.name
            filename = fs.save(filePath, myfile)
            uploaded_file_url = fs.url(filename)

    #state = "error occured."
    template = get_template('curiousWorkbench/webManageModule.html')
    contextDict =  {
        'rootURL' : rootURL,
        'state': state,
        'UserName': request.user.username,
    }

    # context.update(csrf(request))

    return HttpResponse(template.render(contextDict))

@csrf_exempt
def webManageModule(request):
    state = "Please log in below..."
    username = ''
    password = ''
    logger.info("hello1")
    if request.POST:
        logger.info("hello")
        logger.info(str(request.FILES.items()))
        for a in request.FILES:
            logger.info(str(a))
        if 'FileUpload' in request.FILES:
            myfile = request.FILES['FileUpload']
            fs = FileSystemStorage()
            filePath = configSettingsObj.appFolderPath() + "/UserContent/FileUploads/" + myfile.name
            filename = fs.save(filePath, myfile)
            uploaded_file_url = fs.url(filename)

    #state = "error occured."
    template = get_template('curiousWorkbench/webManageModule.html')
    contextDict =  {
        'rootURL' : rootURL,
        'state': state,
        'UserName': request.user.username,
    }

    # context.update(csrf(request))

    return HttpResponse(template.render(contextDict))



def user_logout(request):
    logout(request)
    request.session.flush()
    request.user = AnonymousUser
    template = get_template('curiousWorkbench/login.html')
    contextDict =  {
        'rootURL' : rootURL,
        'state': "You Have been logged out, Please login again if you wish to continue ",
    }
    return HttpResponse(template.render(contextDict))


@login_required
def index(request):
    template = get_template('curiousWorkbench/index.html')
    contextDict =  {
        'rootURL' : rootURL,
        'latest_question_list': 1,
        'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
@csrf_exempt
def handleActions(request):
    if 'refreshBotBehaviour' in request.POST:
        objBotState = BotState()
        objBotState.refreshBot()
        return HttpResponseRedirect(reverse('curiousWorkbench:configBot', ))
