import sys
import os
import datetime
from django.db.models import Count
import ast

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
import csv
from django.db import transaction
from viewSlack import slackClientWalnutBotView
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
import pygal
from pygal.style import DefaultStyle
from pygal.style import Style
from models import UserState, UserSkillStatus
from models import StateMachine, MessageLibrary, ContentLibrary, Module, UserCertification, Progress, PlatformCredentials, Challenge, SignUp,UserActions
from botState import BotState
import urllib
import urllib2
from django.core.files.storage import FileSystemStorage
from itertools import *
from django.db import connection

import redis
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


def fbAriseBotContentWebView(request, content_Id, user_Id):
    try:
        logger.info("1")
        mp.track(user_Id, "ViewContent", {
                 'strNextEvent': "", 'strToState': "", 'strCallFunction': "", "Content_ID": content_Id})

        strContentID = content_Id
        r_server = redis.Redis(host=configSettingsObj.inMemDbHost,
                               port=configSettingsObj.inMemDbPort, db=configSettingsObj.inMemDataDbName)
        logger.info("2")
        if strContentID != "":
            strContent = r_server.hget("KEY_CONTENT_" + strContentID, "Msg")
        else:
            strContent = r_server.hget("0", "Msg")
        strHTML = "Oop, did not find content"
        logger.info("3")
        if strHTML != "":
            dictContent = json.loads(strContent)
            try:
                selProgress = Progress.objects.get(
                    userID=user_Id, SKILL_CODE=dictContent["Skill"])
                selProgress.Credits += 1
            except Progress.DoesNotExist:
                selProgress = Progress(
                    userID=user_Id, SKILL_CODE=dictContent["Skill"])
                selProgress.Credits = 1
            selProgress.save()
            logger.info("4")
            if dictContent["Type"] == "WebPage":
                strHTML = "<iframe style='overflow: hidden; height: 100%; width: 100%; position: absolute;' src='" + \
                    dictContent["LinkURL"] + "'></iframe>"
            if dictContent["Type"] == "YouTube":
                strHTML = "<iframe style='overflow: hidden; height: 100%; width: 100%; position: absolute;' height='315' src='https://www.youtube.com/embed/" + \
                    dictContent["Embed_ID"] + "'></iframe>"
            if dictContent["Type"] == "UGC":
                strHTML = "<iframe style='overflow: hidden; height: 100%; width: 100%; position: absolute;' height='315' src='" + \
                    self.configSettingsObj.absFileLocation + "/videos/" + \
                    dictContent["LinkURL"] + "'></iframe>"
        logger.info("5")
        template = get_template('curiousWorkbench/displayContentWebView.html')
        strTitle = dictContent["Title"]
        contextDict =  {
            'rootURL' : rootURL,
            'strHTML': strHTML,
            'strTitle': strTitle,
            'timeStamp': timezone.now(),
        }
        return HttpResponse(template.render(contextDict))
    except Exception, e:
        self.logger.error('fbAriseBotContentWebView' + str(e))


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
def successfullInstall(request):
    state = "Please log in below..."
    username = ''
    password = ''
    if request.POST:
        state = "here 1"
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
    template = get_template('curiousWorkbench/successfullInstall.html')
    contextDict =  {
        'rootURL' : rootURL,
        'state': state,
        'UserName': request.user.username,
    }

    # context.update(csrf(request))

    return HttpResponse(template.render(contextDict))


# @csrf_exempt
# def user_signup(request):
#     state = "Please log in below..."
#     username = ''
#     password = ''
#     if request.POST:
#         state = "here 1"
#         username = request.POST["username"]
#         password = request.POST["password"]
#
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 state = "You're successfully logged in!"
#             else:
#                 state = "Your account is not active, please contact the site admin."
#
#             template = get_template('curiousWorkbench/index.html')
#             contextDict =  {
#                 'state': state,
#             }
#             return HttpResponse(template.render(contextDict))
#         else:
#             state = "Your username and/or password were incorrect."
#             template = get_template('curiousWorkbench/login.html')
#             contextDict =  {
#                 'state': state,
#                 'UserName': request.user.username,
#             }
#             return HttpResponse(template.render(contextDict))
#
#     #state = "error occured."
#     template = get_template('curiousWorkbench/signup.html')
#     contextDict =  {
#         'state': state,
#         'UserName': request.user.username,
#     }
#     )
#     # context.update(csrf(request))
#
#     return HttpResponse(template.render(contextDict))


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
            filePath = self.configSettingsObj.appFolderPath() + "/UserContent/FileUploads/" + myfile.name
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
            filePath = self.configSettingsObj.appFolderPath() + "/UserContent/FileUploads/" + myfile.name
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


def facebookAuth(request):
   # print 'a i am here'
    dataFileList = 'before'
    template = get_template('curiousWorkbench/facebookAuth.html')
    if request.method == 'POST':
        dataFileList = 'after'
        nAccessTokenValue = request.POST['nAccessToken']
        first_nameValue = request.POST['first_name']
        last_nameValue = request.POST['last_name']
        age_range_minValue = request.POST['age_range_min']
        genderValue = request.POST['gender']
        locationValue = request.POST['location']
        localeValue = request.POST['locale']
        timezoneValue = request.POST['timezone']
        birthdayValue = request.POST['birthday']
        hometownValue = request.POST['hometown']

        newUserIdentity = UserIdentity(nAccessToken=nAccessTokenValue,
                                       first_name=first_nameValue,
                                       last_name=last_nameValue,
                                       age_range_min=age_range_minValue,
                                       gender=genderValue,
                                       locale=localeValue,
                                       location=localeValue,
                                       timezone=timezoneValue,
                                       birthday=birthdayValue,
                                       hometown=hometownValue)
        newUserIdentity.save()

        return render_to_response(
            'curiousWorkbench/facebookAuth.html',
            {'dataFileList': dataFileList, 'form': 'l', 'showSuccess': 'block'},
            context_instance=RequestContext(request))
    # Render list page with the documents and the form
    else:
        return render_to_response(
            'curiousWorkbench/facebookAuth.html',
            {'dataFileList': dataFileList, 'form': 'l', 'showSuccess': 'none'},
            context_instance=RequestContext(request))


def displayPVPolicy(request):

    template = get_template('curiousWorkbench/displayPVPolicy.html')
    strTitle = "My Certificates"
    contextDict =  {
        'timeStamp': timezone.now(),
    }
    return HttpResponse(template.render(contextDict))


def displayTnC(request):

    template = get_template('curiousWorkbench/displayTnC.html')
    strTitle = "Terms and Conditions"
    contextDict =  {
        'timeStamp': timezone.now(),
    }
    return HttpResponse(template.render(contextDict))
# displayTnC


def fbAriseBotCertWebView(request, userID):
    mp.track(userID, "ViewContent", {
             'strNextEvent': "", 'strToState': "", 'strCallFunction': "", "User_ID": userID})

    strUserID = userID
    objUserCertificationList = UserCertification.objects.filter(userID=userID).order_by('-date')

    objModuleCreatedList = Module.objects.filter(UserID = strUserID)
    objModuleCreatedList = UserActions.objects.filter(User_ID=userID,Action="START_MODULE")
    objModuleSharedList = UserActions.objects.filter(User_ID=userID,Action="SHARE_MODULE")


    #strHTML = "<table><tr><td>Title</td><td>Author</td><td> Profile</td><td>Skill</td><td>Date Completed</td><td>Share</td></tr>"
    intModulesCreated = Module.objects.filter(UserID=userID).count()
    intModulesConsumed = UserCertification.objects.filter(userID=userID).count()
    for objUserCertification in objUserCertificationList:
        strLinkedInShareURL = "https://www.linkedin.com/shareArticle?mini=true&"
        dictLinkedInURLParams = {}
        dictLinkedInURLParams["url"] = webURLRoot
        dictLinkedInURLParams["title"] = objUserCertification.Title
        dictLinkedInURLParams["summary"] = "I just acquired this short skill."
        dictLinkedInURLParams["source="] = "Walnut Ai - Learn skills bot"
        strLinkedInURLParams = urllib.urlencode(dictLinkedInURLParams)
        strLinkedInShareURL = strLinkedInShareURL + strLinkedInURLParams

    #---------GenerateGraph1
    strRandomKey = str(randint(0,9000))
    strSql_1= "select DATE(CreatedDate) AS 'createdDateVal', count(id) as 'units' from curiousWorkbench_usercertification where userID ='" + userID + "' group by createdDateVal;"
    results_1 = list(query_to_dicts(strSql_1))

    chartFileName_1 = "profile_chart_1_" + "-" + str(userID) + strRandomKey + ".png"
    chartPath_1 = configSettingsObj.absFileLocation + "/images/plots/" + chartFileName_1
    custom_style= Style(legend_font_size=20, value_font_size=20,title_font_size=40, colors=('#29b992','#f77b71'))
    bar_chart = pygal.Bar(title=u'Concepts I learnt', print_values=True,print_values_position='top',  print_labels=False,show_y_labels=False, legend_at_bottom=True,include_x_axis=False,include_y_axis=False,show_y_guides=False,margin=50,style=custom_style,)
    for result_1 in results_1:
        bar_chart.add(str(result_1["createdDateVal"]),[result_1["units"]], rounded_bars=2 * 10)

    bar_chart.render_to_png(filename=chartPath_1)
    chartURL_1 = configSettingsObj.webUrl + "/static/curiousWorkbench/images/plots/" + chartFileName_1
    chartURL_2=""
    chartURL_3=""
    #---------GenerateGraph2
    strRandomKey = str(randint(0,9000))
    strSql_2= "select DATE(CreatedDate) AS 'createdDateVal', count(id) as 'units' from curiousWorkbench_module where userID = '"+ userID +"' group by createdDateVal;"
    results_2 = list(query_to_dicts(strSql_2))

    chartFileName_2 = "profile_chart_2_" + "-" + str(userID) + strRandomKey + ".png"
    chartPath_2 = configSettingsObj.absFileLocation + "/images/plots/" + chartFileName_2
    custom_style= Style(legend_font_size=20, value_font_size=20,title_font_size=40, colors=('#29b992','#f77b71'))
    bar_chart = pygal.Bar(title=u'Modules I Created', print_values=True,print_values_position='top',  print_labels=False,show_y_labels=False, legend_at_bottom=True,include_x_axis=False,include_y_axis=False,show_y_guides=False,margin=50,style=custom_style,)
    for result_2 in results_2:
        bar_chart.add(str(result_2["createdDateVal"]),[result_2["units"]], rounded_bars=2 * 10)

    bar_chart.render_to_png(filename=chartPath_2)
    chartURL_2 = configSettingsObj.webUrl + "/static/curiousWorkbench/images/plots/" + chartFileName_2
    #---------GenerateGraph3
    strRandomKey = str(randint(0,9000))
    strSql_3= "select DATE(CreatedDate) AS 'createdDateVal', count(id) as 'units' from curiousWorkbench_usercertification where userID ='" + userID + "' group by createdDateVal;"
    results_3 = list(query_to_dicts(strSql_3))

    chartFileName_3 = "profile_chart_1_" + "-" + str(userID) + strRandomKey + ".png"
    chartPath_3 = configSettingsObj.absFileLocation + "/images/plots/" + chartFileName_3
    custom_style= Style(legend_font_size=20, value_font_size=20,title_font_size=40, colors=('#29b992','#f77b71'))
    bar_chart = pygal.Bar(title=u'Modules I Shared', print_values=True,print_values_position='top',  print_labels=False,show_y_labels=False, legend_at_bottom=True,include_x_axis=False,include_y_axis=False,show_y_guides=False,margin=50,style=custom_style,)
    for result_3 in results_3:
        bar_chart.add(str(result_3["createdDateVal"]),[result_3["units"]], rounded_bars=2 * 10)

    bar_chart.render_to_png(filename=chartPath_3)
    chartURL_3 = configSettingsObj.webUrl + "/static/curiousWorkbench/images/plots/" + chartFileName_3

    #---------------------------------------
    strRandomKey = str(randint(0,9000))
    strSql_4= "select ModuleID,CurrentPosition,LastUpdatedDate,(select Units from curiousWorkbench_module a where a.ID=b.ModuleID) as 'Units' from curiousWorkbench_usermoduleprogress b where b.UserID='D3X5U1BBJ';"
    results_4 = list(query_to_dicts(strSql_4))

    chartFileName_4 = "profile_chart_1_" + "-" + str(userID) + strRandomKey + ".png"
    chartPath_4 = configSettingsObj.absFileLocation + "/images/plots/" + chartFileName_4
    custom_style= Style(legend_font_size=20, value_font_size=20,title_font_size=40, colors=('#29b992','#f77b71'))
    bar_chart = pygal.Bar(title=u'Modules I Shared', print_values=True,print_values_position='top',  print_labels=False,show_y_labels=False, legend_at_bottom=True,include_x_axis=False,include_y_axis=False,show_y_guides=False,margin=50,style=custom_style,)
    for result_4 in results_4:
        bar_chart.add(str(result_3["createdDateVal"]),[result_3["units"]], rounded_bars=2 * 10)

    bar_chart.render_to_png(filename=chartPath_4)
    chartURL_4 = configSettingsObj.webUrl + "/static/curiousWorkbench/images/plots/" + chartFileName_4

    #---------------------------------------
    template = get_template('curiousWorkbench/displayCertWebView.html')
    strTitle = "My Certificates"
    contextDict =  {
        # 'strHTML': strHTML,
        'strTitle': strTitle,
        'strUserName': "Chandan Maruthi",
        'strTeamName': "Chandans Team",
        'timeStamp': timezone.now(),
        'objUserCertificationList': objUserCertificationList,
        'intModuleCreated': intModulesCreated,
        'intModulesConsumed': intModulesConsumed,
        'intContentReached' :  20,
        'objModuleCreatedList': objModuleCreatedList,
        'objModuleSharedList': objModuleSharedList,
        'chartURL_1':chartURL_1,
        'chartURL_2':chartURL_2,
        'chartURL_3':chartURL_3,
    }
    return HttpResponse(template.render(contextDict))


def fbAriseBotReminder(request, passID):
    intCounter = 0
    #logger.info('entered reminder function')
    dateTimeObj = datetime.datetime.now()
    currentUTCHour = dateTimeObj.hour
    if passID == "4321":
        post_message_url = configSettingsObj.facebookPostMessageURL % configSettingsObj.fbPageAccessTokenArise
        fbCustBotObj = clientFacebook()
        userStateObjs = UserState.objects.filter(Notify_Subscription="TRUE")
        logger.info('in Reminder function at' + str(dateTimeObj))
        LocalNotifyTime = 9
        for userStateObj in userStateObjs:
            notifyUserNowFlag = False
            userID = userStateObj.UserID
            if userStateObj.Notify_Time == 'MOR':
                LocalNotifyTime = 10
            elif userStateObj.Notify_Time == 'AFT':
                LocalNotifyTime = 12
            elif userStateObj.Notify_Time == 'EVE':
                LocalNotifyTime = 20

            if currentUTCHour + int(userStateObj.UserTimeZone) < 0:
                currentLocalHour = 24 + currentUTCHour + \
                    int(userStateObj.UserTimeZone)
            elif currentUTCHour + int(userStateObj.UserTimeZone) > 24:
                currentLocalHour = currentUTCHour + \
                    int(userStateObj.UserTimeZone) - 24
            else:
                currentLocalHour = currentUTCHour + \
                    int(userStateObj.UserTimeZone)

            logger.info(currentUTCHour)
            logger.info(currentLocalHour)
            logger.info(LocalNotifyTime)
            if currentLocalHour == LocalNotifyTime:
                notifyUserNowFlag = True

            if notifyUserNowFlag == True:
                mp.track(userStateObj.UserID, "Reminder", {
                         'strNextEvent': "", 'strToState': "", 'strCallFunction': ""})
                # if userID == "1383980648297827":
                #logger.info('matching user id')
                payload = "SHOW_RECO_NOTIFY"
                response_msg = fbCustBotObj.processEvent(
                    payload, userID, recevied_message='', VideoURL='')
                # logger.info(post_message_url)
                for response_msg_item in response_msg:
                    # logger.info(response_msg_item)
                    if response_msg_item != '':
                        logger.info(str(response_msg_item))
                        status = requests.post(post_message_url, headers={
                                               "Content-Type": "application/json"}, data=response_msg_item)
                        intCounter += 1
                        # logger.info(status)
    template = get_template('curiousWorkbench/fbABReminder.html')
    contextDict =  {
        'strHTML': "Sent " + str(intCounter) + " reminders",
        'strTitle': "Reminders",
        'timeStamp': timezone.now(),
    }
    return HttpResponse(template.render(contextDict))


#@method_decorator(csrf_exempt)
def fbWebhook(request):
   # print 'in webhook message'
    try:
        # print HttpResponse(escape(repr(request)))
        if request.GET['hub.verify_token'] == configSettingsObj.fbVerifyToken:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token 232')
    except KeyError, e:
        # Redisplay the question voting form.
        self.logger.error(str(e))
        return HttpResponse('Error, invalid token232')


def getconv(request, moduleID):
   # print 'i am here duuuudeee', moduleID
    if request.is_ajax():
       # print 'start of getconv'
        contentList = Content.objects.filter(module__id__contains=moduleID)
        moduleList = Module.objects.order_by('-Title')
        contentItems = []
        for contentRow in contentList:
            contentSet = {}
            contentSet['text'] = contentRow.Content
            contentSet['id'] = contentRow.id
            contentItems.append(contentSet)
        #todo_items = ['Mow Lawn', 'Buy Groceries',]
        data = json.dumps(contentItems)
       # print 'end of getconv'
        return HttpResponse(data, content_type='application/json')

    else:
        raise Http404
#!----------------------------UI ----------------------------------------


@login_required
def configUsers(request):
    UserStateList = UserState.objects.order_by('UserName')
    template = get_template('curiousWorkbench/configUsers.html')
    UsersByRoleList = UserState.objects.values(
        'UserRole').annotate(dcount=Count('UserRole'))
    UsersNotificationList = UserState.objects.values(
        'Notify_Subscription').annotate(dcount=Count('Notify_Subscription'))
    UsersByGenderList = UserState.objects.values(
        'UserGender').annotate(dcount=Count('UserGender'))
    UsersByNotifyTimeList = UserState.objects.values(
        'Notify_Time').annotate(dcount=Count('Notify_Time'))

    # Replace the username, and API key with your credentials.
    py.sign_in('chandanmaruthi', 'LYh6mM6JtyArCnfA76Tx')
    #-------------------------------------------------------
    xAxisRoleSummary = []
    yAxisRoleSummary = []
    intMax = 20
    intCount = 0
    for UsersByRole in UsersByRoleList:
        if intCount <= intMax:
            xAxisRoleSummary.append(UsersByRole["UserRole"][:20])
            yAxisRoleSummary.append(UsersByRole["dcount"])
            intCount += 1
    traceRole = go.Pie(labels=xAxisRoleSummary, values=yAxisRoleSummary)
    data = [traceRole]
    layout = go.Layout(title='Users By Role', width=800, height=640)
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename=configSettingsObj.appFolderPath +
                     'static/curiousWorkbench/images/plots/UsersByRole.png')
    imgURLRole = configSettingsObj.webUrl + \
        "/static/curiousWorkbench/images/plots/UsersByRole.png"

    #-------------------------------------------------------
    xAxisGenderSummary = []
    yAxisGenderSummary = []
    for UsersByGender in UsersByGenderList:
        xAxisGenderSummary.append(UsersByGender["UserGender"])
        yAxisGenderSummary.append(UsersByGender["dcount"])
    traceGender = go.Pie(labels=xAxisGenderSummary, values=yAxisGenderSummary)
    data = [traceGender]
    layout = go.Layout(title='Users By Gender', width=800, height=640)
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename=configSettingsObj.appFolderPath +
                     'static/curiousWorkbench/images/plots/UsersByGender.png')
    imgURLGender = configSettingsObj.webUrl + \
        "/static/curiousWorkbench/images/plots/UsersByGender.png"

    #-------------------------------------------------------
    xAxisNotifySummary = []
    yAxisNotifySummary = []
    for UsersNotification in UsersNotificationList:
        xAxisNotifySummary.append(UsersNotification["Notify_Subscription"])
        yAxisNotifySummary.append(UsersNotification["dcount"])
    traceNotify = go.Pie(labels=xAxisNotifySummary, values=yAxisNotifySummary)
    data = [traceNotify]
    layout = go.Layout(
        title='Users By Notification subscription', width=800, height=640)
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename=configSettingsObj.appFolderPath +
                     'static/curiousWorkbench/images/plots/UsersBySubscription.png')
    imgURLSubscription = configSettingsObj.webUrl + \
        "/static/curiousWorkbench/images/plots/UsersBySubscription.png"

    #-------------------------------------------------------
    xAxisNotifyTimeSummary = []
    yAxisNotifyTimeSummary = []
    for UsersByNotifyTime in UsersByNotifyTimeList:
        xAxisNotifyTimeSummary.append(UsersByNotifyTime["Notify_Time"])
        yAxisNotifyTimeSummary.append(UsersByNotifyTime["dcount"])
    traceNotifyTime = go.Pie(
        labels=xAxisNotifyTimeSummary, values=yAxisNotifyTimeSummary)
    data = [traceNotifyTime]
    layout = go.Layout(
        title='Users by Notification Time of Day', width=800, height=640)
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename=configSettingsObj.appFolderPath +
                     'static/curiousWorkbench/images/plots/UsersByNotifyTime.png')
    imgURLNotifyTime = configSettingsObj.webUrl + \
        "/static/curiousWorkbench/images/plots/UsersByNotifyTime.png"

    #-------------------------------------------------------

    contextDict =  {
        'UserStateList': UserStateList,
        'UsersByRoleList': UsersByRoleList,
        'imgURLRole': imgURLRole,
        'imgURLGender': imgURLGender,
        'imgURLSubscription': imgURLSubscription,
        'imgURLNotifyTime': imgURLNotifyTime,
        'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
def configSettings(request):
    fileAppSetting= open(configSettingsObj.appFolderPath+'appSettings.json','rb')
    strAppSettings = fileAppSetting.read()

    #StateMachineList = StateMachine.objects.order_by('SM_ID')
    template = get_template('curiousWorkbench/configSettings.html')
    contextDict =  {
        'strAppSettings': strAppSettings,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))


@login_required
@csrf_exempt
def configStateMachine(request):
    if 'searchEvent' in request.POST:
        strSearchText = request.POST['searchText']
        StateMachineList = StateMachine.objects.filter(Q(Event_Code__icontains=strSearchText)| Q(ExpectedState__icontains=strSearchText)).order_by('Event_Code')
    elif 'clearSearch' in request.POST:
        StateMachineList = StateMachine.objects.order_by('Event_Code')
    else:
        StateMachineList = StateMachine.objects.order_by('Event_Code')

    template = get_template('curiousWorkbench/configStateMachine.html')
    contextDict =  {
        'StateMachineList': StateMachineList,
        'strTree': getEventTree(StateMachineList)
    }
    return HttpResponse(template.render(contextDict))

@login_required
def configBot(request):
    StateMachineList = StateMachine.objects.order_by('Event_Code')
    template = get_template('curiousWorkbench/configBot.html')
    contextDict =  {
        'StateMachineList': StateMachineList,
        'strTree': getEventTree(StateMachineList),
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

def getEventTree(StateMachineList):
    StateMachineList = list(StateMachineList)
    q=""
    for selStateMachine in StateMachineList:
        strHTML= getEventElement(selStateMachine)
        q+= strHTML
        # if selStateMachine.NextEvent !="":
        #     for a in StateMachineList:
        #         if a.Event_Code == selStateMachine.NextEvent:
        #             StateMachineList.remove(a)
    strEventTree = q

    # <li>
    # <input type="checkbox" checked="checked" id="c1" />
    # <label class="tree_label" for="c1"><a href=configSettingsObj.webUrl + "editStateMachineSubscription/{{ stateMachineSubscription.SM_ID }}" target="stateMachine">{{ stateMachineSubscription.Event_Code }}</label>

    return strEventTree
def getEventElement(selStateMachine):
    strQ = ""
    strCh = ""
    strExpectedState =""
    #for selStateMachine in listStateMachine:
        #if len(selStateMachine) >0 :
    strQ += "<ul>"
    strQ += "<li>"
    # if selStateMachine.NextEvent !="":
    #     if selStateMachine.ExpectedState !="":
    #         strExpectedState = " [" + selStateMachine.ExpectedState + "] "
    #     strQ +='<input type="checkbox"  id="' + str(selStateMachine.SM_ID) + '" />'
    #     strQ +='<label class="tree_label" for="'+ str(selStateMachine.SM_ID) + '"><a nohref onclick="javascript:parent.document.getElementById(\'stateMachine\').src=\'' + configSettingsObj.webUrl + "editStateMachineSubscription/" + str(selStateMachine.SM_ID) + '\';">' + selStateMachine.Event_Code + strExpectedState + '</a></label>'
    # else:
    strExpectedState=""
    if selStateMachine.ExpectedState !="":
        strExpectedState = " [ " + str(selStateMachine.ExpectedState) + " ]"
    strQ +='<span class="tree_label" for="'+ str(selStateMachine.SM_ID) + '"><a nohref onclick="javascript:parent.document.getElementById(\'stateMachine\').src=\'' + configSettingsObj.webUrl + "/editStateMachineSubscription/" + str(selStateMachine.SM_ID) + '/\';">' + selStateMachine.Event_Code + strExpectedState + '</a></span>'
    # if selStateMachine.NextEvent !="":
    #     strCh =  getEventElement(selStateMachine.NextEvent, StateMachineList)
    #     strQ += strCh
    strQ += "</li>"
    strQ += "</ul>"

    strElement = strQ
    return strElement

# def getEventElement(strEventCode,StateMachineList):
#     strQ = ""
#     strCh = ""
#     strExpectedState =""
#     listStateMachine = StateMachine.objects.filter(Event_Code=strEventCode)
#     for selStateMachine in listStateMachine:
#         #if len(selStateMachine) >0 :
#         strQ += "<ul>"
#         strQ += "<li>"
#         if selStateMachine.NextEvent !="":
#             if selStateMachine.ExpectedState !="":
#                 strExpectedState = " [" + selStateMachine.ExpectedState + "] "
#             strQ +='<input type="checkbox"  id="' + str(selStateMachine.SM_ID) + '" />'
#             strQ +='<label class="tree_label" for="'+ str(selStateMachine.SM_ID) + '"><a nohref onclick="javascript:parent.document.getElementById(\'stateMachine\').src=\'' + configSettingsObj.webUrl + "editStateMachineSubscription/" + str(selStateMachine.SM_ID) + '\';">' + selStateMachine.Event_Code + strExpectedState + '</a></label>'
#         else:
#             strQ +='<span class="tree_label" for="'+ str(selStateMachine.SM_ID) + '"><a nohref onclick="javascript:parent.document.getElementById(\'stateMachine\').src=\'' + configSettingsObj.webUrl + "editStateMachineSubscription/" + str(selStateMachine.SM_ID) + '\';">' + selStateMachine.Event_Code + '</a></span>'
#         if selStateMachine.NextEvent !="":
#             strCh =  getEventElement(selStateMachine.NextEvent, StateMachineList)
#             strQ += strCh
#         strQ += "</li>"
#         strQ += "</ul>"
#
#     strElement = strQ
#     return strElement

@login_required
def configMessageLibrary(request):
    MessageLibraryList = MessageLibrary.objects.order_by('ID')
    template = get_template('curiousWorkbench/configMessageLibrary.html')
    contextDict =  {
        'MessageLibraryList': MessageLibraryList,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))


@login_required
def configContentLibrary(request):
    ContentLibraryList = ContentLibrary.objects.filter(Message_Type='UGC')[
        :100]
    template = get_template('curiousWorkbench/configContentLibrary.html')
    contextDict =  {
        'ContentLibraryList': ContentLibraryList,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
def configModule(request):
    ModuleList = Module.objects.order_by('ID')
    template = get_template('curiousWorkbench/configModule.html')
    contextDict =  {
        'ModuleList': ModuleList,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
@requires_csrf_token
@transaction.atomic
def uploadContent(request,ModuleID):
    if request.user.is_authenticated():
        username = request.user.username
    ModuleList = Module.objects.filter(ID=ModuleID)
    uploaded_file_url=""
    template = get_template('curiousWorkbench/uploadContent.html')
    c = {}
    c.update(csrf(request))
    strData=""
    sid = 0
    strErrorMessage = ""
    intSucces = 1
    contextDict =  {
        'ModuleList': ModuleList,
        'UserName': request.user.username,
    }
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filePath = configSettingsObj.appFolderPath + "UserContent/FileUploads/"
        filename = fs.save(filePath + myfile.name, myfile)

        uploaded_file_url = fs.url(filePath)
        fileObj = open(filePath + myfile.name, 'rb')
        mime = magic.Magic(mime=True)
        logger.info(mime.from_file(filePath + myfile.name))
        strData=""

        strData +="<table>"
        intSample =0

        arrAllowedHeaders=['Module_ID','Order_Number','Concept','Question_Text','Option_A','Option_B','Option_C','Option_D','Option_E','Correct_Answer','Tags']
        if mime.from_file(filePath + myfile.name) == "text/plain":
            readerList= csv.DictReader(fileObj)

            fileHeaders = readerList.fieldnames
            for strHeader in arrAllowedHeaders:
                if strHeader not in fileHeaders:
                    intSucces = 0
                    strErrorMessage += "Column Not Provided: " +  strHeader

            if intSucces ==1 :
                for reader in readerList:
                    logger.info(str(reader))

                    contentObj = ContentLibrary()
                    contentObj.Type = "Text"
                    contentObj.Text = reader["Concept"]
                    contentObj.Message_Type = "UGC"
                    contentObj.Module_ID = reader["Module_ID"]
                    contentObj.Tags = reader["Tags"]
                    contentObj.save()

                    challengeObj=Challenge()
                    challengeObj.Content_ID = contentObj.ID
                    challengeObj.Module_ID = reader["Module_ID"]
                    challengeObj.Question_Text = reader["Question_Text"]
                    challengeObj.Correct_Answer = reader["Correct_Answer"]
                    challengeObj.Option_A = reader["Option_A"]
                    challengeObj.Option_B = reader["Option_B"]
                    challengeObj.Option_C = reader["Option_C"]
                    challengeObj.Option_D = reader["Option_D"]
                    challengeObj.Option_E = reader["Option_E"]
                    challengeObj.save()

                    sid =  transaction.savepoint()
                    strErrorMessage = "File successfully uploaded"

                    intSample +=1
                    if intSample <20:
                        strData += "<tr><td>" + str(reader["Module_ID"][:20]) + "</td><td>" + str(reader["Order_Number"][:20]) + "</td><td>" + str(reader["Concept"][:20]) + "</td><td>" + str(reader["Question_Text"][:20]) + "</td><td>" + str(reader["Option_A"][:20]) + "</td><td>" + str(reader["Option_B"][:20]) + "</td><td>" + str(reader["Option_C"][:20]) + "</td><td>" + str(reader["Option_D"][:20]) + "</td><td></tr>"

            else:
                strErrorMessage = "There was an error uploading the file see below, " + strErrorMessage

        strData +="</table>"

        if intSample >0:
            transaction.savepoint_commit(sid)




        contextDict =  {
            'ModuleList': ModuleList,
            'uploaded_file_url': uploaded_file_url,
                    'UserName': request.user.username,
                    'dataTable': strData,
                    'ModuleID' :ModuleID,
                    'SuccessMessage' : strErrorMessage,
                    'UserName': username,}
    return HttpResponse(template.render(contextDict))



@login_required
def addStateMachineSubscription(request):
    template = get_template(
        'curiousWorkbench/addStateMachineSubscription.html')
    contextDict =  {'timeStamp': timezone.now(),
            'UserName': request.user.username,}
    return HttpResponse(template.render(contextDict))


@login_required
def deleteStateMachineSubscription(request, SM_ID):
    selStateMachine = StateMachine.objects.get(pk=SM_ID)
    selStateMachine.delete()

    StateMachineList = StateMachine.objects.order_by('-Event_Code')
    template = get_template('curiousWorkbench/tateMachine.html')
    contextDict =  {
        'StateMachineList': StateMachineList,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))


@login_required
def editStateMachineSubscription(request, SM_ID):
    selStateMachine = get_object_or_404(StateMachine, pk=SM_ID)
    #selAction = MessageLibrary.objects.filter(EventID=selStateMachine.SM_ID)
    template = get_template(
        'curiousWorkbench/editStateMachineSubscription.html')
    contextDict =  {
        'rootURL' : rootURL,
        'selStateMachine': selStateMachine,
        'selEventID':selStateMachine.SM_ID,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
def editTestChat(request):
    selStateMachine = get_object_or_404(StateMachine, pk=1)
    selAction = MessageLibrary.objects.filter(Action=selStateMachine.Action)
    template = get_template(
        'curiousWorkbench/editTestChat.html')
    contextDict =  {
        'selStateMachine': selStateMachine,
        'selActionID':selAction[0].ID,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))


@login_required
def addMessageLibrary(request):
    template = get_template('curiousWorkbench/addMessageLibrary.html')
    contextDict =  {'timeStamp': timezone.now(),        'UserName': request.user.username,}
    return HttpResponse(template.render(contextDict))


@login_required
def editMessageLibrary(request, ID):

    #selAction = get_object_or_404(MessageLibrary, EventID=ID)

    try:
        selMessageLibrary = MessageLibrary.objects.get(EventID=ID)
    except MessageLibrary.DoesNotExist:
        selMessageLibrary = None

    template = get_template('curiousWorkbench/editMessageLibrary.html')
    contextDict =  {
        'selMessageLibrary': selMessageLibrary,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
def deleteMessageLibrary(request, ID):
    selMessage = MessageLibrary.objects.filter(pk=ID).delete()

    MessageLibraryList = MessageLibrary.objects.order_by('-Action')
    template = get_template('curiousWorkbench/configMessageLibrary.html')
    contextDict =  {
        'MessageLibraryList': MessageLibraryList,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
def editContentLibrary(request, ID):
    selContent = get_object_or_404(ContentLibrary, pk=ID)
    template = get_template('curiousWorkbench/editContentLibrary.html')
    contextDict =  {
        'selContent': selContent,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
def editModule(request, ID):
    selModule = get_object_or_404(Module, pk=ID)
    template = get_template('curiousWorkbench/editModule.html')
    contextDict =  {
        'selModule': selModule,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
def deleteContentLibrary(request, ID):
    selContent = ContentLibrary.objects.get(pk=ID)
    selContent.delete()

    ContentLibraryList = ContentLibraryList.objects.order_by('-ID')
    template = get_template('curiousWorkbench/configContentLibrary.html')
    contextDict =  {
        'ContentLibraryList': ContentLibraryList,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))

@login_required
def deleteModule(request, ID):
    selContent = ContentLibrary.objects.get(pk=ID)
    selContent.delete()

    ContentLibraryList = ContentLibraryList.objects.order_by('-ID')
    template = get_template('curiousWorkbench/configModule.html')
    contextDict =  {
        'ContentLibraryList': ContentLibraryList,
                'UserName': request.user.username,
    }
    return HttpResponse(template.render(contextDict))


@login_required
def addContentLibrary(request):
    template = get_template('curiousWorkbench/addContentLibrary.html')
    contextDict =  {'timeStamp': timezone.now(),        'UserName': request.user.username,}
    return HttpResponse(template.render(contextDict))


@login_required
def addModule(request):
    template = get_template('curiousWorkbench/addModule.html')
    contextDict =  {'timeStamp': timezone.now(),        'UserName': request.user.username,}
    return HttpResponse(template.render(contextDict))


@login_required
@csrf_exempt
def saveStateMachine(request, SM_ID=""):
    # logger.info(str(request.POST))
    if 'saveStateMachine' in request.POST:
        selectedStateMachine = get_object_or_404(StateMachine, pk=SM_ID)
        selectedStateMachine.Event_Code = request.POST['Event_Code']
        selectedStateMachine.ExpectedState = request.POST['ExpectedState']
        selectedStateMachine.State = request.POST['State']
        #selectedStateMachine.Expiry = request.POST['Expiry']
        selectedStateMachine.Action = request.POST['Action']
        selectedStateMachine.NextEvent = request.POST['NextEvent']
        selectedStateMachine.CallFunction = request.POST['CallFunction']
        #selectedStateMachine.ParentSystem = request.POST['ParentSystem']
        selectedStateMachine.save()

        try:
            selMessageLibrary =  MessageLibrary.objects.get(EventID=SM_ID)
        except MessageLibrary.DoesNotExist:
            newMessageLibrary = MessageLibrary()
            newMessageLibrary.Type = "Text"
            newMessageLibrary.Text = "Sample"
            newMessageLibrary.EventID = SM_ID
            newMessageLibrary.save()

        return HttpResponseRedirect(reverse('curiousWorkbench:editStateMachineSubscription', args=(selectedStateMachine.SM_ID,)))
    elif 'addStateMachine' in request.POST:
        selectedStateMachine = StateMachine()
        #selectedStateMachine.SM_ID = request.POST['SM_ID']
        selectedStateMachine.Event_Code = request.POST['Event_Code']
        selectedStateMachine.ExpectedState = request.POST['ExpectedState']
        selectedStateMachine.State = request.POST['State']
        #selectedStateMachine.Expiry = request.POST['Expiry']
        selectedStateMachine.Action = request.POST['Action']
        selectedStateMachine.NextEvent = request.POST['NextEvent']
        selectedStateMachine.CallFunction = request.POST['CallFunction']
        #selectedStateMachine.ParentSystem = request.POST['ParentSystem']
        selectedStateMachine.save()

        try:
            selMessageLibrary =  MessageLibrary.objects.get(EventID=selectedStateMachine.SM_ID)
        except MessageLibrary.DoesNotExist:
            newMessageLibrary = MessageLibrary()
            newMessageLibrary.MessageType = "Text"
            newMessageLibrary.MessageText = "Sample"
            newMessageLibrary.EventID = selectedStateMachine.SM_ID
            newMessageLibrary.save()


        return HttpResponseRedirect(reverse('curiousWorkbench:editStateMachineSubscription', args=(selectedStateMachine.SM_ID,)))
    elif 'deleteStateMachine' in request.POST:
        selectedStateMachine = StateMachine.objects.get(pk=SM_ID)
        selectedStateMachine.delete()

        selMessageLibrary = MessageLibrary.objects.get(EventID=SM_ID)
        selMessageLibrary.delete()

        return HttpResponseRedirect(reverse('curiousWorkbench:configStateMachine'))


@login_required
@csrf_exempt
def saveMessageLibrary(request, ID=""):
    if 'saveMessage' in request.POST:

        selectedMessage = get_object_or_404(MessageLibrary, EventID=ID)
        #selectedMessage.Action = request.POST['Action']
        #selectedMessage.MsgOrder = request.POST['MsgOrder']
        selectedMessage.MessageType = request.POST['MessageType']
        selectedMessage.MessageText = request.POST['MessageText']
        selectedMessage.MessageImage = request.POST['MessageImage']
        selectedMessage.MessageVideo = request.POST['MessageVideo']
        selectedMessage.MessageButtons = request.POST['MessageButtons']
        selectedMessage.MessageQuickReplies = request.POST['MessageQuickReplies']
        selectedMessage.save()



        return HttpResponseRedirect(reverse('curiousWorkbench:editMessageLibrary', args=(ID,)))
    elif 'addMessage' in request.POST:
        selectedMessage = MessageLibrary()
        #selectedMessage.ID = request.POST['ID']
        #selectedMessage.Action = request.POST['Action']
        #selectedMessage.MsgOrder = request.POST['MsgOrder']
        selectedMessage.MessageType = request.POST['MessageType']
        selectedMessage.MessageText = request.POST['MessageText']
        selectedMessage.MessageImage = request.POST['MessageImage']
        selectedMessage.MessageVideo = request.POST['MessageVideo']
        selectedMessage.MessageButtons = request.POST['MessageButtons']
        selectedMessage.MessageQuickReplies = request.POST['MessageQuickReplies']
        selectedMessage.save()
        return HttpResponseRedirect(reverse('curiousWorkbench:editMessageLibrary', args=(ID,)))
    elif 'deleteMessage' in request.POST:
        logger.info("in delete message")
        logger.info(str(ID))
        MessageLibrary.objects.filter(EventID=ID).delete()
        return HttpResponseRedirect(reverse('curiousWorkbench:configMessageLibrary', ))


@login_required
@csrf_exempt
def saveContentLibrary(request, ID=""):
    if 'saveContent' in request.POST:
        selectedContentLibrary = get_object_or_404(ContentLibrary, pk=ID)
        selectedContentLibrary.Module_ID = request.POST['Module_ID']
        selectedContentLibrary.Rating = int(request.POST['Rating'])
        selectedContentLibrary.Content_Order = request.POST['Content_Order']
        selectedContentLibrary.Message_Type = request.POST['Message_Type']
        selectedContentLibrary.Text = request.POST['Text'].encode(
            'ascii', 'replace')
        selectedContentLibrary.Title = request.POST['Title']
        selectedContentLibrary.Subtitle = request.POST['Subtitle']
        selectedContentLibrary.ImageURL = request.POST['ImageURL']
        selectedContentLibrary.LinkURL = request.POST['LinkURL']
        selectedContentLibrary.Embed_ID = request.POST['Embed_ID']
        selectedContentLibrary.Type = request.POST['Type']
        selectedContentLibrary.Skill = request.POST['Skill']
        selectedContentLibrary.Questions = request.POST['Questions'].encode(
            'ascii', 'replace')
        selectedContentLibrary.AnswerOptions = request.POST['AnswerOptions'].encode(
            'ascii', 'replace')
        selectedContentLibrary.RightAnswer = request.POST['RightAnswer'].encode(
            'ascii', 'replace')
        selectedContentLibrary.Right_Ans_Response = request.POST['Right_Ans_Response'].encode(
            'ascii', 'replace')
        selectedContentLibrary.Wrong_Ans_Response = request.POST['Wrong_Ans_Response'].encode(
            'ascii', 'replace')
        selectedContentLibrary.save()
        return HttpResponseRedirect(reverse('curiousWorkbench:editContentLibrary', args=(selectedContentLibrary.ID,)))
    elif 'addContent' in request.POST:
        selectedContentLibrary = ContentLibrary()
        selectedContentLibrary.ID = request.POST['ID']
        selectedContentLibrary.Module_ID = request.POST['Module_ID']
        selectedContentLibrary.Content_Order = request.POST['Content_Order']
        selectedContentLibrary.Message_Type = request.POST['Message_Type']
        selectedContentLibrary.Text = request.POST['Text'].encode(
            'ascii', 'replace')
        selectedContentLibrary.Title = request.POST['Title'].encode(
            'ascii', 'replace')
        selectedContentLibrary.Subtitle = request.POST['Subtitle'].encode(
            'ascii', 'replace')
        selectedContentLibrary.ImageURL = request.POST['ImageURL']
        selectedContentLibrary.LinkURL = request.POST['LinkURL']
        selectedContentLibrary.Embed_ID = request.POST['Embed_ID']
        selectedContentLibrary.Type = request.POST['Type']
        selectedContentLibrary.Skill = request.POST['Skill']
        selectedContentLibrary.Questions = request.POST['Questions']
        selectedContentLibrary.AnswerOptions = request.POST['AnswerOptions'].encode(
            'ascii', 'replace')
        selectedContentLibrary.RightAnswer = request.POST['RightAnswer'].encode(
            'ascii', 'replace')
        selectedContentLibrary.Right_Ans_Response = request.POST['Right_Ans_Response'].encode(
            'ascii', 'replace')
        selectedContentLibrary.Wrong_Ans_Response = request.POST['Wrong_Ans_Response'].encode(
            'ascii', 'replace')

        selectedContentLibrary.save()
        return HttpResponseRedirect(reverse('curiousWorkbench:editContentLibrary', args=(selectedContentLibrary.ID,)))

    elif 'deleteContent' in request.POST:
        selectedContentLibrary = ContentLibrary.objects.get(pk=ID)
        selectedContentLibrary.delete()
        return HttpResponseRedirect(reverse('curiousWorkbench:configContentLibrary', ))


@login_required
@csrf_exempt
def saveModule(request, ID=""):
    if 'saveModule' in request.POST:
        selectedModule = get_object_or_404(Module, pk=ID)
        # selectedModule.ID = request.POST['ID']
        selectedModule.Title = request.POST['Title']
        selectedModule.Description = request.POST['Description']
        # selectedModule.AuthorURL = request.POST['AuthorURL']
        selectedModule.Goal = request.POST['Goal']
        selectedModule.Author = request.POST['Author']
        selectedModule.Units = request.POST['Units']
        selectedModule.save()
        return HttpResponseRedirect(reverse('curiousWorkbench:editModule', args=(selectedModule.ID,)))
    elif 'addModule' in request.POST:
        selectedModule = Module()
        # selectedModule.ID = request.POST['ID']
        selectedModule.Title = request.POST['Title']
        selectedModule.Description = request.POST['Description']
        # selectedModule.AuthorURL = request.POST['AuthorURL']
        selectedModule.Goal = request.POST['Goal']
        selectedModule.Author = request.POST['Author']
        selectedModule.Units = request.POST['Units']
        selectedModule.save()
        return HttpResponseRedirect(reverse('curiousWorkbench:editModule', args=(selectedModule.ID,)))

    elif 'deleteModule' in request.POST:
        selectedModule = Module.objects.get(pk=ID)
        selectedModule.delete()
        return HttpResponseRedirect(reverse('curiousWorkbench:configModule', ))



@login_required
@csrf_exempt
def saveSettings(request):
    if 'txtSettings' in request.POST:
        fileAppSetting= open(configSettingsObj.appFolderPath+'appSettings.json','wb')
        strAppSettings = request.POST['txtSettings']
        fileAppSetting.write(strAppSettings)
        #selectedModule.save()
        return HttpResponseRedirect(reverse('curiousWorkbench:configSettings'))


@login_required
@csrf_exempt
def handleActions(request):
    if 'refreshBotBehaviour' in request.POST:
        objBotState = BotState()
        objBotState.refreshBot()
        return HttpResponseRedirect(reverse('curiousWorkbench:configBot', ))


def slackAuth(request):
    try:
        ####self.logger.info(str('i am here 1'))
        # print configSettingsObj.fbVerifyToken ,
        # request.GET['self.configSettingsObjify_token']
        strMessage=""
        if request.GET['code'] != '':
            strTempCode = request.GET['code']
            payload = {}
            payload["client_id"] = configSettingsObj.slackWalnutClientID
            payload["client_secret"] = configSettingsObj.slackClientSecret
            payload["code"] = strTempCode
            payload["redirect_uri"] = configSettingsObj.webUrl + "/slackAuth"
            r = requests.get(
                "https://slack.com/api/oauth.access", params=payload)

            strJson = r.text.decode('utf-8')
            strJson = urllib.unquote(strJson)

            logger.info("code is" + strTempCode)
            logger.info(strJson)
            dictInstallCred = json.loads(strJson)

            logger.info(str(dictInstallCred["ok"]))
            if dictInstallCred["ok"]:
                strAccessToken = dictInstallCred["access_token"]
                strScope = dictInstallCred["scope"]
                strTeamName = dictInstallCred["team_name"]
                strTeamID = dictInstallCred["team_id"]
                strAuthUserID =  dictInstallCred["user_id"]
                strAuthTeamName = dictInstallCred["team_name"]
                #strChallengeID = dictInstallCred["channel_id"]
                strBotUserID = dictInstallCred["bot"]["bot_user_id"]
                strBotAccessToken = dictInstallCred["bot"]["bot_access_token"]

                #with transaction.atomic():
                objPlatformCredentials = PlatformCredentials()
                objPlatformCredentials.SlackAccessToken = strAccessToken
                objPlatformCredentials.SlackScope = strScope
                objPlatformCredentials.SlackTeamName = strTeamName
                objPlatformCredentials.SlackTeamID = strTeamID
                objPlatformCredentials.SlackBotUserID = strBotUserID
                objPlatformCredentials.SlackBotAccessToken = strBotAccessToken
                objPlatformCredentials.CreatedUser = strAuthUserID
                objPlatformCredentials.CreatedDate = datetime.datetime.now()
                objPlatformCredentials.LastUpdatedDateUser = strAuthUserID
                objPlatformCredentials.LastUpdatedUserDate = datetime.datetime.now()
                objPlatformCredentials.save()
                strMessage = 'Success'
                ####self.logger.info(str('i am here 2'))

                strGetDMIDURL ="https://slack.com/api/im.list?token="+ strBotAccessToken  +"&pretty=1"

                responseDMIDs = requests.get(strGetDMIDURL)

                strDMIDsContent= responseDMIDs.content

                dictDMIDs = json.loads(strDMIDsContent)

                dmIDs = dictDMIDs["ims"]

                dmAuthUserID = ""
                for im in dmIDs:
                    if im["user"] == strAuthUserID:
                        dmAuthUserID = im["id"]


                if dmAuthUserID !="":
                    objSlackClient = slackClientWalnutBotView()

                    dictMessage = {}
                    dictMessage["token"]= strBotAccessToken
                    dictMessage["team_id"]= strTeamID

                    dictEvent={}
                    dictEvent["type"]="message"
                    dictEvent["user"]=[strAuthUserID]
                    dictEvent["text"] = "hello"
                    dictEvent["channel"] =dmAuthUserID
                    dictEvent["authed_users"]= strAuthUserID

                    dictMessage["event"] = dictEvent

                    #{"token":"IKDsdx8sgJ7hCEB0ubIQ42Kq","team_id":"T0ATCR7RR",
                    #"event":{"type":"message","user":"U0ATCR7S7","text":"hello","channel":"D3X5U1BBJ"},"type":"event_callback","authed_users":["U3XQL857V"]}

                    strJsonMessage = json.dumps(dictMessage)
                    r= requests.post(configSettingsObj.webUrl +"/slackWebhookWalnutBot/", data=strJsonMessage)
                    logger.info(str(r))
            else:
                logger.info(str('slackAuth no code found'))
                strMessage = 'Error, invalwewid token111'




        template = get_template('curiousWorkbench/successfullInstall.html')
        contextDict =  {'timeStamp': timezone.now(), 'UserName': request.user.username,
        'InstallMessage': strMessage}
        return HttpResponse(template.render(contextDict))

    except KeyError, e:
        # Redisplay the question voting form.
        logger.error(str(e))
        return HttpResponse('Error, invalid token1234')
