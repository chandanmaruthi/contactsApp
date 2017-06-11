# -*- coding: utf-8 -*-
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
from environmentVariables import environmentVariables
from environmentVariables import *

import time
import json
import random
import sys
import redis
from random import randint
import cgi
from dateutil import parser
from datetime import datetime
import MySQLdb
import unicodedata
import json
import requests
import random
import re
import MySQLdb
import logging
from configSettings import *
from elasticsearch import Elasticsearch
from dateutil import parser

from models import UserState, UserSkillStatus
from models import StateMachine, MessageLibrary, ContentLibrary, UserModuleProgress, Module, UserCertification, RoleDemandInfo, Progress
from django.shortcuts import get_list_or_404, get_object_or_404
import urllib
import botLogic
from botLogic import botLogic
import os.path
import apiai
from django.forms.models import model_to_dict
import mixpanel
from mixpanel import Mixpanel
mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")


class clientSlack():

    configSettingsObj = configSettings()
    #----------------Logging ------------------
    logger = logging.getLogger('fbClientEventBot')
    #-------------------------------------------------------------------------
    hdlr = logging.FileHandler(
        configSettingsObj.logFolderPath + 'clientSlack.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    botLogicObj = botLogic("Slack")
    logger.info('logging log folder path clientSlack.py')
    # logger.info(configSettingsObj.logFolderPath)
    #-------------------------------------------
    listOfRemoveStrings = ['<span>', '</span>', '<br>', '</br>', '<br/>']
    r_server = redis.Redis(host=configSettingsObj.inMemDbHost,
                           db=configSettingsObj.inMemDataDbName)
    r_stateServer = redis.Redis(
        host=configSettingsObj.inMemDbHost, db=configSettingsObj.inMemStateDbName)

    def __init__(self):
        try:
            inputMsg = 'no value'
            lastTopicNumber = 15
            # ########self.logger.info('init')
            db = MySQLdb.connect(host=self.configSettingsObj.dbHost,    # your host, usually localhost
                                 user=self.configSettingsObj.dbUser,         # your username
                                 passwd=self.configSettingsObj.dbPassword,  # your password
                                 db=self.configSettingsObj.dbName)        # name of the data base
        except Exception, e:
            self.logger.error('fbClient init here' + str(e))

    def NLProcessMessage(self, inputMessage):
        try:
            strAction = ""
            if inputMessage.strip() != "":

                ai = apiai.ApiAI('988345dc9f26462cb74c930198bf0616')
                apiAIRequest = ai.text_request()
                apiAIRequest.lang = 'en'
                ###############self.logger.info( "starting NLP : " + inputMessage)
                apiAIRequest.query = inputMessage
                apiAIResponse = apiAIRequest.getresponse()
                strApiAIIntent = apiAIResponse.read()
                responseDict = json.loads(strApiAIIntent)
                ##########self.logger.info( "NLP Feed : " + str(responseDict))

                strAction = ''
                if 'result' in responseDict:
                    if 'metadata' in responseDict['result']:
                        if 'intentName' in responseDict['result']['metadata']:
                            strAction = responseDict['result']['metadata']['intentName']
            NLPDict = {}
            NLPDict['INTENT'] = strAction
            NLPDict['ENTITY_MOVIE'] = ''

            return NLPDict
        except Exception, e:

            self.logger.error('handle nlp process' + str(e))

    def processEvent(self, event, fbid, recevied_message='', VideoURL='', ImageURL='', Headers=''):
        try:
            ##self.logger.info("in  processEvent 1")
            # #######self.logger.info(str(recevied_message))
            strNotificationType = "REGULAR"
            strToState = ''
            strCurrentState = self.botLogicObj.getUserState(fbid)
            strMessage = ''
            dictParams = {}
            ##self.logger.info("in  processEvent 2")

            if event == '' and strCurrentState == "CLEAR" and recevied_message != "":
                ###self.logger.info("case 2.1")
                strEvent = self.NLProcessMessage(recevied_message)["INTENT"]
                if strEvent != "":
                    event = strEvent
                else:
                    event = 'UNABLE_TO_UNDERSTAND'
                ###self.logger.info("2.2")
            elif event == '' and strCurrentState != "CLEAR" and recevied_message != "":
                ###self.logger.info("case 3.1")
                event = 'MSG'
                #########self.logger.info("here 02")
            elif VideoURL != "":
                ########self.logger.info("case 3")
                #########self.logger.info("here 03")
                event = 'VIDEO_UPLOAD'
                #self.logger.info("video posted" + str(VideoURL))
            elif ImageURL != "":
                ##########self.logger.info("case 3")
                ##########self.logger.info("here 03")
                event = 'IMAGE_UPLOAD'
                #self.logger.info("image posted" + str(ImageURL))
            #self.logger.info("in  processEvent 4" + event)

            dictEventInfo = event.split("-")
            eventCode = dictEventInfo[0]

            for dictItem in dictEventInfo:
                arrParamInfo = dictItem.split("|")
                if len(arrParamInfo) == 2:
                    dictParams[arrParamInfo[0]] = arrParamInfo[1]

            dictParams['VideoURL'] = VideoURL
            dictParams['ImageURL'] = ImageURL
            if Headers != "":
                dictParams['Headers'] = Headers

            strDictParams = json.dumps(dictParams)
            stateMachineSubscriptions = self.r_server.hgetall(
                "KEY_EVENT_" + str(eventCode))
            stateMachineSubscriptions = self.r_server.hgetall(
                "KEY_EVENT_" + str(eventCode))
            # #######self.logger.info(str(stateMachineSubscriptions))
            ##self.logger.info("5")
            for subscription in stateMachineSubscriptions:
                strAction = ""
                strNextEvent = ""
                strToState = ""
                strCallFunction = ""
                strEventID = ""

                strVal = stateMachineSubscriptions[subscription]
                dictStateMachine = json.loads(strVal)
                strExpectedState = dictStateMachine['ExpectedState']
                ##self.logger.info("in  processEvent 5")
                process = False
                if strExpectedState == strCurrentState:
                    process = True
                elif strExpectedState == '':
                    process = True
                if process == True:
                    #strAction = dictStateMachine['Action']
                    strNextEvent = dictStateMachine['NextEvent']
                    strToState = dictStateMachine['State']
                    strCallFunction = dictStateMachine['CallFunction']
                    strEventID = dictStateMachine['SM_ID']
                    # #######self.logger.info(strCallFunction)
                    #strAction1 = strAction
                    strNextEvent1 = strNextEvent
                    strToState1 = strToState
                    strCallFunction1 = strCallFunction
                    if strAction == "":
                        strAction1 = "Msg"
                        if strNextEvent == "":
                            strNextEvent1 = "empty"
                        if strToState == "":
                            strToState1 = "empty"
                        if strCallFunction == "":
                            strCallFunction1 = "empty"
                    mp.track(fbid, strAction1, {
                             'strNextEvent': strNextEvent, 'strToState': strToState, 'strCallFunction': strCallFunction})
                    ##self.logger.info("step 7")
                    recevied_message = recevied_message.replace('"', "")
                    recevied_message = recevied_message.replace("'", "")
                    # #######self.logger.info(strAction)
                    # #######self.logger.info(fbid)
                    # #######self.logger.info(recevied_message)
                    # #######self.logger.info(strDictParams)
                    if strCallFunction != '':
                        strCallFunctionSyntax = "self.botLogicObj." + strCallFunction + \
                            "('" + fbid + "','" + recevied_message + \
                            "','" + strDictParams + "')"
                        ###self.logger.info("call funtion" + strCallFunctionSyntax)
                        eval(strCallFunctionSyntax)
                        #########self.logger.info("step 6.1.1-")

                    ##self.logger.info("step 8")
                    strMessage = self.buildMessage(
                        strEventID, fbid, recevied_message, strDictParams)
                    ##self.logger.info("step 8.2")

                    self.botLogicObj.setUserCurrentState(fbid, strToState)
                    ##self.logger.info("9")
                    if strNextEvent1 != '':
                        strMessageNew = self.processEvent(
                            strNextEvent1, fbid, '', '')
                        #########self.logger.info("printing internal processEvent" + str(strMessageNew))
                        if strMessage is None:
                            strMessage = []
                        for message in strMessageNew:
                            strMessage.append(message)
                            # #######self.logger.info(str(strMessage))
                            #########self.logger.info("step 6.3")
                        strMessageNew = ""

            ##self.logger.info("10")
            return strMessage
        except Exception, e:
            self.logger.error("processEvent" + str(e))
            strMessage = self.buildMessage("msg_oops", fbid, "", "")
            return strMessage

    def getProgressBar(self, intRange):
        if intRange < 10:
            intBars = 1
        elif intRange >= 10:
            intBars = int(intRange / 10)
        strBars = ""
        for intA in range(0, intBars):
            strBars += ""
        return strBars

    def getAttachment(self):
        try:
            # print 'pppppppppp'
            dictAttachment = {}
            dictAttachment['type'] = 'template'
            dictAttachment['payload'] = self.getPayload(
                'button', 'Hey There! Lets get started', self.getButtons())
            # print dictAttachment
            return dictAttachment
        except KeyError, e:
            self.logger.error("getAttachment " + str(e))
            # Redisplay the question voting form.
            # print 'getAttachment an error here'
            # print str(e)

    def getPayload(self, templateType, text, buttons):
        # print 'pppppppppp2'
        dictPayload = {}
        dictPayload['template_type'] = templateType
        dictPayload['text'] = text
        dictPayload['buttons'] = self.getButtons()
        return dictPayload

    def getButtons(self):
        dictbuttons = []
        # print 'pppppppppp3'
        dictbuttons.append(self.getButton(
            'postback', 'Ask a question', surl='', spayload='ASK_A_QUESTION'))
        dictbuttons.append(self.getButton(
            'postback', 'Hours and Location', surl='', spayload='HOURS_AND_LOCATION'))
        dictbuttons.append(self.getButton(
            'postback', 'Place an Order', surl='', spayload='ORDER'))
        return dictbuttons

    def buildMessage(self, eventID, fbid, recevied_message, strDictParams):
        try:
            ##self.logger.info("0")
            ##self.logger.info("1")
            strNotificationType = "REGULAR"
            responseMessages = []
            response_msg_item = ''
            strMessageTypeFromContent =""
            rawMessages = self.r_server.hgetall("KEY_ACTION_" + str(eventID))
            dictMessageParams = {}
            ##self.logger.info("2")
            for message in rawMessages:
                if message is not None:
                    strmessagesDetailsVal = rawMessages[message]
                    strSubTitleInfo = ""
                    strDictButtons = ""

                    if strmessagesDetailsVal != '':
                        dictMessageDetails = json.loads(strmessagesDetailsVal)
                        strMessage = ""
                        strMessageType = ""
                        strButtonInfo = ""
                        strImageInfo = ""
                        strMessageImage = ""
                        strMessageVideo = ""
                        strQuickReplies = ""

                        strMessage = dictMessageDetails['MessageText']
                        strMessageType = dictMessageDetails['MessageType']
                        strButtonInfo = dictMessageDetails['MessageButtons']
                        strImageInfo = dictMessageDetails['MessageImage']
                        strMessageImage = dictMessageDetails['MessageImage']
                        strMessageVideo = dictMessageDetails['MessageVideo']
                        strQuickReplies = dictMessageDetails['MessageQuickReplies']
                        strAttachmentText =""

                        arrMessageList = strMessage.split("||")
                        strMessage = random.choice(arrMessageList)


                        arrReplaceableKeys = []
                        arrReplaceableKeys = re.findall(r"\{{([A-Za-z0-9_]+)\}}",strMessage)
                        if arrReplaceableKeys is not None:
                            for strReplaceableKey in arrReplaceableKeys:
                                strReplaceableValue = self.botLogicObj.getFromUserStateFromDict(fbid,strReplaceableKey)
                                strMessage = strMessage.replace("{{" + strReplaceableKey + "}}", strReplaceableValue)


                        ##self.logger.info("3")
                        #strListContent = dictMessageDetails["ListContent"]
                        intStart = strMessage.find('[[')
                        intEnd = strMessage.find(']]')
                        strLink = ""
                        strMessageTypeFromContent = ""
                        if intStart > -1:
                            strSubAction = strMessage[intStart + 2:intEnd]
                            strSubActionFunctionSyntax = "self.botLogicObj." + strSubAction + \
                                "('" + fbid + "','" + recevied_message + \
                                "','" + strDictParams + "')"
                            ###self.logger.info("printing subfunction" + strSubActionFunctionSyntax)
                            arrRetMessageDicts = eval(strSubActionFunctionSyntax)

                            #########self.logger.info("here 1")
                            ########self.logger.info(str(arrRetMessageDicts))
                            for dictMessageParams in arrRetMessageDicts:
                                ##self.logger.info(dictMessageParams)
                                ##self.logger.info("4.0.0")

                                if dictMessageParams !={}:
                                    if 'strAttachmentText' in dictMessageParams:
                                        strAttachmentText = dictMessageParams['strAttachmentText']
                                    else:
                                        strAttachmentText = ""

                                    if "arrTargetUsers" in dictMessageParams:
                                        arrTargetUsers = dictMessageParams["arrTargetUsers"]
                                    else:
                                        arrTargetUsers = None

                                    if "NotificationType" in dictMessageParams:
                                        strNotificationType = dictMessageParams["NotificationType"]
                                    if "MessageType" in dictMessageParams:
                                        strMessageTypeFromContent = dictMessageParams["MessageType"]

                                    ##self.logger.info("4")
                                    if strMessageTypeFromContent != "":
                                        strMessageType = strMessageTypeFromContent
                                        #########self.logger.info("here 2")
                                    if strMessageType == 'Text':
                                        response_msg_item = self.buildSimpleMessage(
                                            fbid, dictMessageParams["Message"], dictMessageParams["ImageURL"], dictMessageParams["VideoURL"], dictMessageParams["QuickReplies"], strNotificationType, strAttachmentText)
                                    elif strMessageType == 'Buttons':
                                        # #######self.logger.info(dictMessageParams["Link"])
                                        response_msg_item = self.buildButtonMessage(fbid, dictMessageParams["Message"], dictMessageParams["DictButtons"], dictMessageParams["ImageURL"], dictMessageParams["SubTitleInfo"], dictMessageParams[
                                                                                    "ImageURL"], dictMessageParams["VideoURL"], dictMessageParams["Link"], dictMessageParams["DictButtons"], dictMessageParams["QuickReplies"], strNotificationType)
                                        # #######self.logger.info("test200")
                                        #########self.logger.info("here 300000")
                                    elif strMessageType == 'Image':
                                        response_msg_item = self.buildImageMessage(
                                            fbid, dictMessageParams["Message"], dictMessageParams["ImageURL"], dictMessageParams["VideoURL"], dictMessageParams["QuickReplies"], strNotificationType)
                                    elif strMessageType == 'List':
                                        #########self.logger.info("calling list message")
                                        response_msg_item = self.buildListMessage(
                                            fbid, dictMessageParams["QuickReplies"], strNotificationType, dictMessageParams["ListContent"], dictMessageParams["ListButtons"])

                                    ##self.logger.info("here 5")

                                    if response_msg_item != '':
                                        ##self.logger.info("here 5.1")
                                        ##self.logger.info(response_msg_item)
                                        responseMessages.append([response_msg_item,arrTargetUsers])
                                        response_msg_item =  None
                                        ##self.logger.info("here 5.2")

                        else:

                            if strMessageType == 'Text':
                                response_msg_item = self.buildSimpleMessage(
                                    fbid, strMessage, strMessageImage, strMessageVideo, strQuickReplies, strNotificationType,strAttachmentText)
                            elif strMessageType == 'Buttons':
                                # #######self.logger.info("test1")
                                if "QuickReplies" in dictMessageParams:
                                    strQuickReplies1 = dictMessageParams["QuickReplies"]
                                response_msg_item = self.buildButtonMessage(
                                    fbid, strMessage, strButtonInfo, strMessageImage, strSubTitleInfo, strMessageImage, strMessageVideo, "", "", strQuickReplies1, strNotificationType)
                                # #######self.logger.info("test290")
                            elif strMessageType == 'Image':
                                response_msg_item = self.buildImageMessage(
                                    fbid, strMessage, strMessageImage, strMessageVideo, strQuickReplies, strNotificationType)
                                strMessageImage = ""
                            elif strMessageType == 'List':
                                #########self.logger.info("calling list message")
                                response_msg_item = self.buildListMessage(
                                    fbid, dictMessageParams["QuickReplies"], strNotificationType, dictMessageParams["ListContent"], dictMessageParams["ListButtons"])

                            if "arrTargetUsers" in dictMessageParams:
                                arrTargetUsers = dictMessageParams["arrTargetUsers"]
                            else:
                                arrTargetUsers = None

                            if response_msg_item != '':
                                responseMessages.append([response_msg_item,arrTargetUsers])
                ##self.logger.info("-------->>6")
                #######self.logger.info(str(responseMessages))
            return responseMessages
        except Exception, e:
            self.logger.error("buildMessage" + str(e))

    def buildSimpleMessage(self, fbid, responseMessage, imageURL="", videoURL="", strQuickReplies="", strNotificationType="REGULAR", strAttachmentText=""):
        try:
            response_msg_item = ''
            quickReplies = []
            if responseMessage == "":
                responseMessage = "blank message"
            dictMessage = {}
            dictMessage["recipient"] = {"id": fbid}
            dictMessage["message"] = {}
            dictMessage["message"]["text"] = responseMessage
            dictMessage["notification_type"] = strNotificationType
            ###self.logger.info("221")
            ###self.logger.info(strQuickReplies)
            if strQuickReplies != "":
                arrQuickReplies = strQuickReplies.split(",")
                #####self.logger.info("000.11")
                for quickReply in arrQuickReplies:
                    if quickReply !="":
                        #####self.logger.info("000.12")
                        quickReplyDetails = quickReply.split(":")
                        contentType = quickReplyDetails[0]
                        title = quickReplyDetails[1][:18]
                        payload = quickReplyDetails[2]
                        #####self.logger.info("000.13")
                        imageURL = ""
                        if len(quickReplyDetails) > 3:
                            imageURL = quickReplyDetails[3]
                            imageURL = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/" + imageURL
                        if title != "":
                            quickReplies.append(
                                {"name": title, "text": title, "type": "button", "value": payload})
                #responseMessage = '.'
                dictMessage["message"]["attachments"] = [
                    {"text": "", "fallback": responseMessage, "callback_id": "001", "actions": quickReplies}]
            #####self.logger.info("000.2")
            if strAttachmentText != "":
                if "attachments" in dictMessage["message"]:
                    dictMessage["message"]["attachments"][0]["text"] =strAttachmentText
                    dictMessage["message"]["attachments"][0]["color"] = "#414af4"
                else:
                    arrAttacments =[]
                    arrAttacments.append({"text":strAttachmentText,"color" : "#414af4" })
                    dictMessage["message"]["attachments"] =  arrAttacments
            #####self.logger.info("000.3")
            if responseMessage != '' or len(quickReplies) != 0:
                response_msg_item = json.dumps(dictMessage)

            return response_msg_item
        except Exception, e:
            self.logger.error('buildSimpleMessage' + str(e))

    def buildImageMessage(self, fbid, responseMessage, imageURL="", videoURL="", strQuickReplies="", strNotificationType="REGULAR"):
        try:
            ########self.logger.info("here 1")
            response_msg_item = ''
            quickReplies = []
            dictMessage = {}
            dictAttachment = {}
            dictPayload = {}
            # dictAttachment["type"]="image"
            # dictPayload["url"]=imageURL
            dictMessage["message"] = {}
            dictMessage["message"]["text"] = responseMessage
            # dictAttachment["payload"]=dictPayload
            #dictMessage["attachment"] =dictAttachment

            dictMessage["recipient"] = {"id": fbid}
            #dictMessage["message"] = {"attachment" : dictAttachment}
            dictMessage["notification_type"] = strNotificationType

            dictAttachment = {}
            dictAttachment["fallback"] = ""
            dictAttachment["title"] = ""
            dictAttachment["title_link"] = ""
            dictAttachment["text"] = ""
            dictAttachment["image_url"] = imageURL
            #dictAttachment["color"] = "#764FA5"

            ########self.logger.info("here 2")
            # #######self.logger.info(json.dumps(dictMessage))

            if strQuickReplies != "":
                arrActions = []
                arrQuickReplies = strQuickReplies.split(",")
                for quickReply in arrQuickReplies:
                    quickReplyDetails = quickReply.split(":")
                    contentType = quickReplyDetails[0]
                    title = quickReplyDetails[1][:18]
                    payload = quickReplyDetails[2]
                    dictButton = {"name": title, "text": title,
                                  "type": "button", "value": payload}
                    arrActions.append(dictButton)

                dictAttachment["callback_id"] = "001"
                dictAttachment["actions"] = arrActions

            dictAttachments = []
            dictAttachments.append(dictAttachment)
            dictMessage["message"]["attachments"] = dictAttachments

            #if responseMessage != '' or len(quickReplies) != 0:
            response_msg_item = json.dumps(dictMessage)
            #######self.logger.info(response_msg_item)
            return response_msg_item
        except Exception, e:
            self.logger.error('buildImageMessage' + str(e))

    def getButton(self, stype, stitle, surl='', spayload=''):
        # print 'pppppppppp4'
        #########self.logger.info("3.5-----" + stype +"---" + stitle +"---" + surl +"---" +spayload )
        dictButton = {}
        if stype == 'web_url':
            dictButton['type'] = 'web_url'
            dictButton['name'] = stitle
            dictButton['text'] = stitle
            dictButton['value'] = surl
            #dictButton['url'] = surl
            #dictButton['webview_height_ratio']= "tall"
        if stype == 'postback':
            dictButton['type'] = 'button'
            dictButton['name'] = stitle
            dictButton['text'] = stitle
            dictButton['value'] = spayload
        # elif stype == 'element_share':
        #     dictButton['type'] = stype

        return dictButton

    def buildButtonMessage(self, fbid, responseMessage, buttonInfo, imageURL, subTitleInfo, strMessageImage, strMessageVideo, linkURL, strDictButtons, strQuickReplies, strNotificationType):
        try:
            #########self.logger.info("1---" + str(buttonInfo))
            #########self.logger.info("2---" + str(strDictButtons))
            response_msg_item = ''
            imageURLSaved = imageURL
            if responseMessage != '':
                #---- Create Buttons
                strButtonInfo = buttonInfo
                arrButtons = strButtonInfo.split(',')

                dictbuttons = []
                if strDictButtons == "":

                    for button in arrButtons:

                        arrButtonInfo = button.split(':')
                        strButtonTitle = arrButtonInfo[0]
                        strButtonPostback = arrButtonInfo[1]
                        strButtonType = ""
                        if len(arrButtonInfo) == 3:
                            flagButtonType = arrButtonInfo[2]
                            if flagButtonType == "P":
                                strButtonType = "postback"
                            elif flagButtonType == "U":
                                strButtonType = "web_url"
                            elif flagButtonType == "S":
                                strButtonType = "element_share"
                        # if strButtonType == "web_url":
                        # #######self.logger.info("-------------ss---------")
                        # if strButtonType == "web_url"
                        dictbuttons.append(self.getButton(
                            strButtonType, strButtonTitle, surl=linkURL, spayload=strButtonPostback))

                else:
                    dictbuttons = json.loads(strDictButtons)

                #########self.logger.info("3------" + str(dictbuttons))
                urlText = ""
                for button in dictbuttons:
                    #########self.logger.info("3-1------" + str(button))

                    #button = json.loads(button)
                    # if "type" in button:
                    if button["type"] == "web_url":
                        if "url" in button:
                            urlText += button["url"]
                            #########self.logger.info("URL---" + str(urlText))
                            # dictbuttons.remove(button)
                    elif button["type"] == "url":
                        urlText += button["url"]
                        # dictbuttons.remove(button)
                        ##########self.logger.info("URL---" + str(urlText))
                    elif button["type"] == "postback":
                        #########self.logger.info("3-1-1------" + str(button))

                        newButton = {}
                        if "title" in button:
                            newButton["name"] = button["title"]
                            newButton["text"] = button["title"]
                            #del dictbuttons[button]["title"]
                        if "payload" in button:
                            newButton["value"] = button["payload"]
                            #del dictbuttons[button]["payload"]
                        newButton["type"] = "button"
                        dictbuttons.remove(button)
                        dictbuttons.append(newButton)

                #########self.logger.info("4-1------" + str(dictbuttons))

                for button in dictbuttons:
                    if button["type"] != "button":
                        dictbuttons.remove(button)

                # dictButton['type'] = stype
                # dictButton['title'] = stitle
                # dictButton['payload'] = spayload

                # dictButton['type'] = 'button'
                # dictButton['name'] = stitle
                # dictButton['text'] = stitle
                # dictButton['value'] = spayload

                dictAttachments = []
                dictAttachment = {}
                dictAttachment["text"] = subTitleInfo
                dictAttachment["fallback"] = responseMessage
                dictAttachment["callback_id"] = "001"
                dictAttachment["author_link"] = urlText
                dictAttachment["title"] = responseMessage
                dictAttachment["title_link"] = urlText
                if imageURLSaved != "":
                    dictAttachment["image_url"] = imageURLSaved

                quickReplies = []
                if strQuickReplies != "":
                    arrQuickReplies = strQuickReplies.split(",")
                    for quickReply in arrQuickReplies:
                        quickReplyDetails = quickReply.split(":")
                        contentType = quickReplyDetails[0]
                        title = quickReplyDetails[1][:18]
                        payload = quickReplyDetails[2]
                        imageURL = ""
                        if len(quickReplyDetails) > 3:
                            imageURL = quickReplyDetails[3]
                            imageURL = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/" + imageURL
                        if imageURL == "":
                            dictbuttons.append(
                                {"type": "button", "name": title, "text": title, "value": payload})
                        else:
                            dictbuttons.append(
                                {"type": "button", "name": title, "text": title, "value": payload})
                dictAttachment["actions"] = dictbuttons
                dictAttachments.append(dictAttachment)
                responseMessage = "."
                if len(quickReplies) == 0:
                    response_msg_item = json.dumps({"recipient": {"id": fbid}, "message": {
                                                   "text": responseMessage, "attachments": dictAttachments}, "notification_type": strNotificationType})
                else:
                    response_msg_item = json.dumps({"recipient": {"id": fbid}, "message": {
                                                   "text": responseMessage, "attachments": dictAttachments, "quick_replies": quickReplies}, "notification_type": strNotificationType})

            return response_msg_item
        except Exception, e:
            self.logger.error('buildButtonMessage' + str(e))

    def buildListMessage(self, fbid, strQuickReplies, strNotificationType, strListContent, strListButtons):
        try:
            response_msg_item = ''
            responseMessage = "_"
            arrListContent=[]
            arrListButtons=[]
            strMessage = ""

            if strListButtons is not None:
                if strListButtons !="":
                    arrListButtons = json.loads(strListButtons.decode('utf-8'))

            try:
                if strListContent is not None:
                    if arrListContent !="":
                        arrListContent = json.loads(strListContent.decode('utf-8'))
            except:
                pass

            if responseMessage != '':
                dictElements = []
                dictAttachments = []
                intCount =0
                for listContent in arrListContent:
                    if intCount ==0:
                        strMessage = "*" + listContent["Title"] + "* \n" + listContent["SubTitle"]
                    else:

                        dictbuttons = []
                        arrButtons = []
                        if "Buttons" in listContent:
                            arrButtons = listContent["Buttons"]
                            for dictButton in arrButtons:
                                dictbuttons.append(self.getButton(
                                    dictButton["ButtonType"], dictButton["ButtonTitle"], surl=dictButton["ButtonLinkURL"], spayload=dictButton["ButtonPostback"]))

                        attachment = {}
                        attachment["title"] = listContent["Title"]
                        attachment["text"] = listContent["SubTitle"]
                        attachment["fallback"] = listContent["Title"]
                        attachment["color"] = "#414af4"
                        attachment["callback_id"] = "001"
                        attachment["actions"] = dictbuttons

                        dictAttachments.append(attachment)
                    intCount +=1

                #####self.logger.info("okokok")
                #####self.logger.info(arrListButtons)
                #for listButton in arrListButtons:
                attachment = {}
                # attachment["title"] = "1"
                attachment["text"] = ""
                # attachment["fallback"] = "1"
                attachment["callback_id"] = "001"
                dictbuttons = []
                for dictButton in arrListButtons:
                    dictbuttons.append(self.getButton(
                        dictButton["ButtonType"], dictButton["ButtonTitle"], surl=dictButton["ButtonLinkURL"], spayload=dictButton["ButtonPostback"]))
                attachment["actions"] = dictbuttons



                dictAttachments.append(attachment)


                quickReplies = []



                #####self.logger.info("done-----")
                if strQuickReplies != "":
                    arrQuickReplies = strQuickReplies.split(",")
                    for quickReply in arrQuickReplies:
                        quickReplyDetails = quickReply.split(":")
                        contentType = quickReplyDetails[0]
                        title = quickReplyDetails[1][:18]
                        payload = quickReplyDetails[2]
                        imageURL = ""
                        if len(quickReplyDetails) > 3:
                            imageURL = quickReplyDetails[3]
                            imageURL = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/" + imageURL
                        if imageURL == "":
                            quickReplies.append(
                                {"content_type": contentType, "title": title, "payload": payload})
                        else:
                            quickReplies.append(
                                {"content_type": contentType, "title": title, "payload": payload, "image_url": imageURL})

                responseMessage = strMessage
                if len(quickReplies) == 0:
                    response_msg_item = json.dumps({"recipient": {"id": fbid}, "message": {
                                                   "text": responseMessage, "attachments": dictAttachments}, "notification_type": strNotificationType})
                else:
                    response_msg_item = json.dumps({"recipient": {"id": fbid}, "message": {
                                                   "text": responseMessage, "attachments": dictAttachments, "quick_replies": quickReplies}, "notification_type": strNotificationType})


            return response_msg_item
        except Exception, e:
            self.logger.error('buildListMessage' + str(e))
