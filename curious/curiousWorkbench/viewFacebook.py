import sys
import os
import datetime
from django.db.models import Count
import ast

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.html import escape
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from clientFacebook import clientFacebook
#from django.core.context_processors import csrf
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
#from models import UserState, UserSkillStatus
#from models import StateMachine, MessageLibrary, ContentLibrary, Module, UserCertification,Progress
from botState import BotState
import urllib
import urllib2


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
import json, requests, random, re
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



class fbClientAriseBotView(generic.View):
    mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")
    configSettingsObj = configSettings()

    #----------------Logging ------------------
    logger = logging.getLogger('views')
    hdlr = logging.FileHandler(configSettingsObj.logFolderPath + 'viewFacebook.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.info('logging log folder path viewFacebook.py')
    #logger.info(self.configSettingsObj.logFolderPath)
    #----------------Logging ------------------

    def get(self, request, *args, **kwargs):
        #print 'in get'
        try:
            #print self.configSettingsObj.fbVerifyToken , request.GET['hub.verify_token']
            if request.GET['hub.verify_token'] == self.self.configSettingsObj.fbVerifyToken:
                return HttpResponse(self.request.GET['hub.challenge'])
            else:
                return HttpResponse('Error, invalwewid token111')
        except KeyError,e:
            # Redisplay the question voting form.
            self.logger.error(str('i am here 3'))
            self.logger.error(str(e))
            return HttpResponse('Error, invalid token1234')

            #print str(e)


    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        #print 'in dispatch'
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        try:
            strResponseFlag = False
            fbCustBotObj = clientFacebook()
            strNotificationType ="REGULAR"
            strJson = self.request.body.decode('utf-8')
            #strJson = ast.literal_eval(strJson)
            incoming_message = json.loads(strJson)
            fbid =""

            #----------Log to Dashbot------------------
            self.logIncommingEvent(json.dumps(incoming_message))
            post_message_url = self.configSettingsObj.facebookPostMessageURL%self.configSettingsObj.fbPageAccessTokenArise
            for entry in incoming_message['entry']:
                inpTxtMessage = ""
                inpPostback = ""
                inpIsEcho = False
                strVideoURL = ""
                strReferralSource = ""
                strReferralRef = ""
                strReferralType = ""
                strImageURL = ""
                for message in entry['messaging']:
                    # ------------- Start Extact input from JSON ----------------------
                    if 'message' in message:
                        if 'is_echo' in message['message']:
                            isIsEcho = True
                        if 'text' in message['message']:
                            inpTxtMessage = message['message']['text']
                        if 'quick_reply' in message['message']:
                            inpPostback = message['message']['quick_reply']['payload']
                        if 'attachments' in message['message']:
                            for attachment in message['message']['attachments']:
                                if 'type' in attachment:
                                    if attachment['type'] == 'video':
                                        if 'payload' in attachment:
                                            strVideoURL= attachment['payload']['url']
                                    if attachment['type'] == 'image':
                                        if 'payload' in attachment:
                                            strImageURL= attachment['payload']['url']


                    if "referral" in message:
                        if "source" in message["referral"]:
                            strReferralSource = message["referral"]["source"]
                        if "ref" in message["referral"]:
                            strReferralRef = message["referral"]["ref"]
                        if "type" in message["referral"]:
                            strReferralType = message["referral"]["type"]

                        inpPostback = "RUN_CHALLENGE-CHALLENGE_ID|"+strReferralRef

                    if 'postback' in message:
                        inpPostback = message['postback']['payload']

                    inpRecipient = message['sender']['id']
                    fbid =  inpRecipient
                    # --------------- End Extract Input from Json ------------------
                    inpTxtMessage =  inpTxtMessage.replace("'","\'")
                    response_msg= fbCustBotObj.processEvent(inpPostback, inpRecipient, recevied_message=inpTxtMessage,VideoURL=strVideoURL,ImageURL=strImageURL)
                    strVideoURL=""


                    #if recvdNotificationType!="":
                    #    strNotificationType = recvdNotificationType
                    #if response_msg is not None:
                    # Check to make sure the received call is a message call
                    # This might be delivery, optin, postback for other events

                    if 'message' in message:
                        strResponseFlag = True
                        if 'is_echo' not in message['message'] and ('text' in message['message'] or 'attachments' in message['message']):
                            #response_msg = fbCustBotObj.processEvent('', message['sender']['id'], recevied_message=message['message']['text'])
                            if response_msg is not None:
                                for response_msg_item in response_msg:
                                    if str(response_msg_item) != '' :
                                        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg_item)
                                        self.logOutGoingEvent(response_msg_item)
                                    else:
                                        msg =  json.dumps({"recipient":{"id":fbid}, "message":{"text":"error"},"notification_type":strNotificationType})
                                        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=msg)
                                        self.logOutGoingEvent(msg)
                    elif ('postback' in message) or ('referral' in message):
                        strResponseFlag = True
                        #print 'kokokoko', message['postback']['payload']
                        #print ' Process Event - a postback was raised' , message['postback']['payload']
                        #response_msg = fbCustBotObj.processEvent(message['postback']['payload'], message['sender']['id'], recevied_message='')
                        for response_msg_item in response_msg:
                            if str(response_msg_item) != '' :
                                status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg_item)
                                self.logOutGoingEvent(response_msg_item)

                    else:
                        msg =  json.dumps({"recipient":{"id":fbid}, "message":{"text":"error"},"notification_type":strNotificationType})
                        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=msg)
                        self.logOutGoingEvent(msg)

                #strDashBotOutgoingURL= "https://tracker.dashbot.io/track?platform=facebook&v=0.8.1-rest&type=outgoing&apiKey=fhjN8ED9gN122XkvP3GSSao7etYrRXJPocZSs0sd"
                #r = requests.post(strDashBotOutgoingURL,headers={"Content-Type": "application/json"},data=msg)

                return HttpResponse()
        except KeyError,e:
            if fbid !="":
                msg =  json.dumps({"recipient":{"id":fbid}, "message":{"text":"error"}})
                status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=msg)

    def logIncommingEvent(self,incoming_message):
        strDashBotIncommingURL= "https://tracker.dashbot.io/track?platform=facebook&v=0.8.1-rest&type=incoming&apiKey=fhjN8ED9gN122XkvP3GSSao7etYrRXJPocZSs0sd"
        r = requests.post(strDashBotIncommingURL, headers={"Content-Type": "application/json"},data=incoming_message)

    def logOutGoingEvent(self,outgoing_message):
        strDashBotOutgoingURL= "https://tracker.dashbot.io/track?platform=facebook&v=0.8.1-rest&type=outgoing&apiKey=fhjN8ED9gN122XkvP3GSSao7etYrRXJPocZSs0sd"
        r = requests.post(strDashBotOutgoingURL, headers={"Content-Type": "application/json"},data=outgoing_message)
