import sys
import os
import datetime
from django.db.models import Count
import ast

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

from environmentVariables import environmentVariables
from environmentVariables import *
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.html import escape
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
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
from curiousWorkbench.models import UserState, UserSkillStatus
from curiousWorkbench.models import StateMachine, MessageLibrary, ContentLibrary, Module, UserCertification, Progress, PlatformCredentials
from botState import BotState
import urllib
import urllib2
import clientSlack

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
from slackclient import SlackClient


class slackClientWalnutBotView(generic.View):
    mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")
    configSettingsObj = configSettings()
    #----------------Logging ------------------
    logger = logging.getLogger('views')
    hdlr = logging.FileHandler(
        configSettingsObj.logFolderPath + 'slackViews.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.info('logging log folder path viewSlack.py')
    #----------------Logging ------------------

    def get(self, request, *args, **kwargs):
        try:
            if request.GET['token'] == self.configSettingsObj.slackVerificationToken:
                return HttpResponse(self.request.GET['challenge'])
            else:
                return HttpResponse('Error, invalwewid token111')
        except KeyError, e:
            self.logger.error(str('i am here 3'))
            self.logger.error(str(e))
            return HttpResponse('Error, invalid token1234')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # print 'in dispatch'
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        try:
            strJson = self.request.body.decode('utf-8')
            #######self.logger.info(strJson)
            strJson = urllib.unquote(strJson)
            self.handleMessage(strJson)

            return HttpResponse(status=200)
        except KeyError, e:
            return HttpResponse(status=200)

    def handleMessage(self, messageString):
        try:
            strMessageType = ""
            strResponseFlag = False
            fbCustBotObj = clientSlack.clientSlack()
            strNotificationType = "REGULAR"
            strSubType = ""
            inpTxtMessage = ""
            inpPostback = ""
            inpIsEcho = False
            strImageURL = ""
            strVideoURL = ""
            strResponseMessageText = ""
            strAttachments = ""
            fbid = ""
            strBotAccessToken = ""
            strHeaders = ""
            strJson = messageString
            strTeamID =""
            ####self.logger.info(str("asdsadad----------1"))

            if strJson[:7] == "payload":
                strJson = strJson[8:]
                ###self.logger.info(strJson)

                incoming_message = json.loads(strJson)
                ####self.logger.info(str("asdsadad----------2"))
                jsonBody = incoming_message
                if "user" in jsonBody:
                    if "id" in jsonBody["user"]:
                        strUser = jsonBody["user"]["id"]
                        inpRecipient = strUser
                if "team" in jsonBody:
                    if "id" in jsonBody["team"]:
                        strTeamID = jsonBody["team"]["id"]
                if "channel" in jsonBody:
                    if "id" in jsonBody["channel"]:
                        strChannel = jsonBody["channel"]["id"]

                if "actions" in jsonBody:
                    if "value" in jsonBody["actions"][0]:
                        strPayload = jsonBody["actions"][0]["value"]
                        inpPostback = strPayload
                strMessageType = "payload"
                strMessageText = ""
                inpTxtMessage = ""

            else:
                ####self.logger.info("asdsadad----------3")
                incoming_message = json.loads(strJson)
                #####self.logger.info(str(incoming_message))
                #----------Log to Dashbot------------------
                jsonBody = incoming_message
                if "token" in jsonBody:
                    strToken = jsonBody["token"]
                ####self.logger.info("asdsadad----------3.1")
                if "team_id" in jsonBody:
                    strTeamID = jsonBody["team_id"]
                ####self.logger.info("asdsadad----------3.2")
                if "event" in jsonBody:
                    dictEvent = jsonBody["event"]
                    if "type" in dictEvent:
                        strMessageType = dictEvent["type"]
                    if "subtype" in dictEvent:
                        strSubType = dictEvent["subtype"]
                    if "user" in dictEvent:
                        strUser = dictEvent["user"]
                        inpRecipient = strUser
                    if "text" in dictEvent:
                        strMessageText = dictEvent["text"]
                        inpTxtMessage = strMessageText
                    if "channel" in dictEvent:
                        strChannel = dictEvent["channel"]

                    ####self.logger.info("asdsadad----------3.4")
                    if "file" in dictEvent:

                        attachmentURL = dictEvent["file"]["url_private"]
                        fileType = dictEvent["file"]["filetype"]
                        if fileType == "jpg" or fileType == "png" or fileType == "gif":
                            strImageURL = attachmentURL
                            strHeaders = "Authorization" + "|" + "Bearer "
                        elif fileType == "mp4":
                            strVideoURL = attachmentURL


            ####self.logger.info("4")
            ######self.logger.info(strTeamID)
            objPlatformCredentialsList = PlatformCredentials.objects.filter(SlackTeamID=strTeamID)
            if len(objPlatformCredentialsList)>0:
                strBotAccessToken = objPlatformCredentialsList[0].SlackBotAccessToken

            ####self.logger.info("asdsadad----------4.1")

            ######self.logger.info("bot tokemn" + strBotAccessToken)

            objUserList = UserState.objects.filter(UserID = strUser )
            if len(objUserList) ==0:
                newUserState = UserState(UserID = strUser,
                                 UserCurrentState = 'INIT' ,
                             	UserLastAccessedTime = datetime.datetime.now(),
                                Org_ID=strTeamID,
                                DM_ID=strChannel)
                newUserState.save()
            else:
                objUser = objUserList[0]
                #####self.logger.info("22222-"+str(strUser)+"-22222")
                #####self.logger.info("22222-"+str(objUser.Org_ID)+"-22222")
                if objUser.Org_ID is None:
                    objUser.Org_ID = strTeamID
                    objUser.DM_ID = strChannel
                    objUser.save()
                elif objUser.Org_ID == "":
                    objUser.Org_ID = strTeamID
                    objUser.DM_ID = strChannel
                    objUser.save()
            ####self.logger.info("asdsadad----------5")
            if strHeaders != "":
                strHeaders += strBotAccessToken
            #####self.logger.info("222222222222")
            ######self.logger.info(strMessageType)
            ######self.logger.info(strSubType)
            if (strMessageType == "message" and strSubType == "bot_remove"):
                ####self.logger.info("asdsadad----------6.2")
                objPlatformCredentialsList = PlatformCredentials.objects.filter(
                    SlackTeamID=strTeamID)
                for objPlatformCredentials in objPlatformCredentialsList:
                    PlatformCredentials.objects.get(
                        pk=objPlatformCredentials.ID).delete()

            elif (strMessageType == "message" and strSubType != "bot_message") or strMessageType == "payload":
                ####self.logger.info("asdsadad----------6.1")
                if strSubType == "file_share":
                    inpTxtMessage = ""

                response_msg = fbCustBotObj.processEvent(
                    inpPostback, inpRecipient, recevied_message=inpTxtMessage, VideoURL=strVideoURL, ImageURL=strImageURL, Headers=strHeaders)

                #####self.logger.info("ok 1111")
                ##self.logger.info("7")
                ##self.logger.info(response_msg)
                if response_msg is not None:

                    arrResponse = response_msg
                    for messageDictStr in arrResponse:
                        messageDict = json.loads(messageDictStr[0])
                        ####self.logger.info("8")
                        if "message" in messageDict:
                            if "text" in messageDict["message"]:
                                strResponseMessageText = messageDict["message"]["text"]
                            if "attachments" in messageDict["message"]:
                                strAttachments = json.dumps(
                                    messageDict["message"]["attachments"])
                            else:
                                strAttachments = ""
                            ####self.logger.info("9")
                            sc = SlackClient(strBotAccessToken)


                            # if messageDictStr[1] !="":
                            #     strChannel=messageDictStr[1]

                            ####self.logger.info("target users >> " + str(messageDictStr))
                            if messageDictStr[1] is not None:
                                if len(messageDictStr[1])>0:
                                    if messageDictStr[1][0] is not None:
                                        strChannel =  messageDictStr[1][0]
                            ####self.logger.info(strChannel)
                            ####self.logger.info("10")
                            if strAttachments == "":
                                ####self.logger.info("here 1")

                                ####self.logger.info(strChannel)
                                ####self.logger.info(strResponseMessageText)

                                resultStr = sc.api_call("chat.postMessage", unfurl_links="true",channel=strChannel,
                                            text=strResponseMessageText)
                            else:
                                ####self.logger.info("here 2")
                                ####self.logger.info(strChannel)
                                ####self.logger.info(strResponseMessageText)
                                resultStr =sc.api_call("chat.postMessage", unfurl_links="true", channel=strChannel,
                                            text=strResponseMessageText, attachments=strAttachments)
                            ####self.logger.info(str("12"))

            ####self.logger.info("asdsadad----------13")
        except KeyError, e:
            self.logger.error("error here")

    def sendMessage(strChannel, strMessage,strTeamID):
        objPlatformCredentialsList = PlatformCredentials.objects.filter(
            SlackTeamID=strTeamID)
        strBotAccessToken = objPlatformCredentialsList[0].SlackBotAccessToken
        sc = SlackClient(strBotAccessToken)
        sc.api_call("chat.postMessage", unfurl_links="true",
                    channel=strChannel, text=strResponseMessageText)



    def logIncommingEvent(self, incoming_message):
        strDashBotIncommingURL = "https://tracker.dashbot.io/track?platform=facebook&v=0.8.1-rest&type=incoming&apiKey=fhjN8ED9gN122XkvP3GSSao7etYrRXJPocZSs0sd"
        r = requests.post(strDashBotIncommingURL, headers={
                          "Content-Type": "application/json"}, data=incoming_message)

    def logOutGoingEvent(self, outgoing_message):
        strDashBotOutgoingURL = "https://tracker.dashbot.io/track?platform=facebook&v=0.8.1-rest&type=outgoing&apiKey=fhjN8ED9gN122XkvP3GSSao7etYrRXJPocZSs0sd"
        r = requests.post(strDashBotOutgoingURL, headers={
                          "Content-Type": "application/json"}, data=outgoing_message)
