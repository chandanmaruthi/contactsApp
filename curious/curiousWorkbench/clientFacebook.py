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
import json, requests, random, re
import MySQLdb
import logging
from configSettings import *
from elasticsearch import Elasticsearch
from dateutil import parser

from models import UserState, UserSkillStatus
from models import StateMachine, MessageLibrary, ContentLibrary, UserModuleProgress, Module, UserCertification,RoleDemandInfo,Progress
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
import re
class clientFacebook():

    configSettingsObj = configSettings()
    #----------------Logging ------------------
    logger = logging.getLogger('fbClientEventBot')
    #--------------------------------------------------------------------------------------------------------
    hdlr = logging.FileHandler( configSettingsObj.logFolderPath + 'clientFacebook.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    botLogicObj = botLogic(platform="Facebook")
    #logger.info('logging log folder path')
    #logger.info(configSettingsObj.logFolderPath)
    #-------------------------------------------
    listOfRemoveStrings = ['<span>' , '</span>', '<br>', '</br>', '<br/>']
    r_server =  redis.Redis(host=configSettingsObj.inMemDbHost,db=configSettingsObj.inMemDataDbName)
    r_stateServer =  redis.Redis(host=configSettingsObj.inMemDbHost,db=configSettingsObj.inMemStateDbName)



    def __init__(self):
        try:
            inputMsg='no value'
            lastTopicNumber = 15
            #######self.logger.info('init')
            db = MySQLdb.connect(host=self.configSettingsObj.dbHost,    # your host, usually localhost
                                 user=self.configSettingsObj.dbUser,         # your username
                                 passwd=self.configSettingsObj.dbPassword,  # your password
                                 db=self.configSettingsObj.dbName)        # name of the data base
        except Exception,e:
            self.logger.error('fbClient init here' + str(e))


    def NLProcessMessage(self, inputMessage):
        try:
            strAction = ""
            if inputMessage.strip() !="":

                ai=apiai.ApiAI('988345dc9f26462cb74c930198bf0616')
                apiAIRequest =  ai.text_request()
                apiAIRequest.lang= 'en'
                #######self.logger.info( "starting NLP : " + inputMessage)
                apiAIRequest.query = inputMessage
                apiAIResponse = apiAIRequest.getresponse()
                strApiAIIntent =  apiAIResponse.read()
                responseDict =json.loads(strApiAIIntent)
                ##self.logger.info( "NLP Feed : " + str(responseDict))

                strAction = ''
                if 'result' in responseDict:
                    if 'metadata' in responseDict['result']:
                        if 'intentName' in responseDict['result']['metadata']:
                            strAction= responseDict['result']['metadata']['intentName']
            NLPDict ={}
            NLPDict['INTENT'] = strAction
            NLPDict['ENTITY_MOVIE'] = ''

            return NLPDict
        except Exception,e:

            self.logger.error('handle nlp process' + str(e))


    def processEvent(self, event, fbid, recevied_message='', VideoURL='',ImageURL=''):
        try:
            ##self.logger.info("in  processEvent 1.1")
            ######self.logger.info(str(recevied_message))
            strNotificationType = "SILENT"
            strToState = ''
            strCurrentState = self.botLogicObj.getUserState(fbid)
            strMessage = ''
            #######self.logger.info("in  processEvent 2")

            if event == '' and strCurrentState=="CLEAR" and recevied_message !="":
                ##self.logger.info("case 1")
                strEvent = self.NLProcessMessage(recevied_message)["INTENT"]
                if strEvent !="":
                    event = strEvent
                else:
                    event = 'UNABLE_TO_UNDERSTAND'
                ##self.logger.info("here 01")
            elif event =='' and strCurrentState !="CLEAR" and recevied_message!="" :
                ##self.logger.info("case 2")
                event = 'MSG'
                ##self.logger.info("here 02")
            elif VideoURL!="" :
                ##self.logger.info("case 3")
                ##self.logger.info("here 03")
                event = 'VIDEO_UPLOAD'
                ##self.logger.info("video posted" + str(VideoURL))
            elif ImageURL!="" :
                ##self.logger.info("case 3")
                ##self.logger.info("here 03")
                event = 'IMAGE_UPLOAD'
                ##self.logger.info("video posted" + str(VideoURL))

            ##self.logger.info("in  processEvent 3" + event)

            dictEventInfo = event.split("-")
            eventCode = dictEventInfo[0]
            dictParams ={}
            for dictItem in dictEventInfo:
                arrParamInfo = dictItem.split("|")
                if len(arrParamInfo) == 2:
                    dictParams[arrParamInfo[0]] = arrParamInfo[1]


            dictParams['VideoURL'] = VideoURL
            dictParams['ImageURL'] = ImageURL

            strDictParams = json.dumps(dictParams)
            stateMachineSubscriptions = self.r_server.hgetall("KEY_EVENT_" + str(eventCode))
            #stateMachineSubscriptions = self.r_server.hgetall("KEY_EVENT_" + str(eventCode))
            ##self.logger.info(str(stateMachineSubscriptions))
            for subscription in stateMachineSubscriptions:
                strAction = ""
                strNextEvent = ""
                strToState = ""
                strCallFunction = ""
                strEventID = ""

                strVal = stateMachineSubscriptions[subscription]
                dictStateMachine = json.loads(strVal)
                strExpectedState = dictStateMachine['ExpectedState']
                process = False
                if strExpectedState == strCurrentState:
                    process = True
                elif strExpectedState =='':
                    process = True
                if process == True:
                    #strAction =  dictStateMachine['Action']
                    strNextEvent = dictStateMachine['NextEvent']
                    strToState = dictStateMachine['State']
                    strCallFunction = dictStateMachine['CallFunction']
                    strEventID = dictStateMachine['SM_ID']
                    ##self.logger.info(strCallFunction)
                    #strAction1=strAction
                    strNextEvent1 =strNextEvent
                    strToState1 =strToState
                    strCallFunction1 =strCallFunction
                    if strAction == "":
                        strAction1 ="Msg"
                        if strNextEvent == "" : strNextEvent1 = "empty"
                        if strToState == "" : strToState1 = "empty"
                        if strCallFunction == "" : strCallFunction1 = "empty"
                    mp.track(fbid, strAction1,{'strNextEvent':strNextEvent,'strToState':strToState,'strCallFunction':strCallFunction})
                    #######self.logger.info("step 6.1")
                    recevied_message =  recevied_message.replace('"',"")
                    recevied_message =  recevied_message.replace("'","")
                    if strCallFunction !='':
                        strCallFunctionSyntax = "self.botLogicObj." + strCallFunction + "('" + fbid + "','" + recevied_message + "','" +strDictParams +"')"
                        ##self.logger.info(strCallFunctionSyntax)
                        eval(strCallFunctionSyntax)
                        #######self.logger.info("step 6.1.1-")


                    strMessage = self.buildMessage(strEventID,fbid, recevied_message, strDictParams)
                    #####self.logger.info("step 6.2")

                    self.botLogicObj.setUserCurrentState(fbid,strToState)
                    #self.logger.info(strToState)
                    if strNextEvent1 !='':
                        strMessageNew = self.processEvent(strNextEvent1,fbid, '','')
                        #self.logger.info("printing internal processEvent" + str(strMessageNew))
                        if strMessage is None :
                            strMessage=[]
                        for message in strMessageNew:
                            strMessage.append(message)
                            ######self.logger.info(str(strMessage))
                            #######self.logger.info("step 6.3")
                        strMessageNew = ""

            return strMessage
        except Exception,e:
            self.logger.error("processEvent" + str(e))
            strMessage = self.buildMessage("msg_oops",fbid, "", "")
            return strMessage



    def getProgressBar(self,intRange):
        if intRange < 10:
            intBars = 1
        elif intRange >= 10:
            intBars = int(intRange/10)
        strBars = ""
        for intA in range(0,intBars):
            strBars += ""
        return strBars
    def getAttachment(self):
        try:
            #print 'pppppppppp'
            dictAttachment = {}
            dictAttachment['type'] = 'template'
            dictAttachment['payload'] = self.getPayload('button', 'Hey There! Lets get started', self.getButtons())
            #print dictAttachment
            return dictAttachment
        except KeyError,e:
            self.logger.error("getAttachment "+str(e))
            # Redisplay the question voting form.
            #print 'getAttachment an error here'
            #print str(e)

    def getPayload(self, templateType,text,buttons):
        #print 'pppppppppp2'
        dictPayload = {}
        dictPayload['template_type'] = templateType
        dictPayload['text'] = text
        dictPayload['buttons'] = self.getButtons()
        return dictPayload

    def getButtons(self):
        dictbuttons =[]
        #print 'pppppppppp3'
        dictbuttons.append(self.getButton('postback','Ask a question', surl='', spayload = 'ASK_A_QUESTION'))
        dictbuttons.append(self.getButton('postback','Hours and Location',surl='',spayload = 'HOURS_AND_LOCATION'))
        dictbuttons.append(self.getButton('postback','Place an Order',surl='',spayload = 'ORDER'))
        return dictbuttons

    def getButton(self, stype, stitle, surl='', spayload=''):
        #print 'pppppppppp4'
        dictButton = {}
        if stype =='web_url':
            dictButton['type'] = stype
            dictButton['title'] = stitle
            dictButton['url'] = surl
            dictButton['webview_height_ratio']= "tall"
        elif stype =='postback':
            dictButton['type'] = stype
            dictButton['title'] = stitle
            dictButton['payload'] = spayload
        elif stype == 'element_share':
            dictButton['type'] = stype
        return dictButton



    def buildMessage(self, eventID, fbid, recevied_message,strDictParams):
        try:
            strNotificationType = "SILENT"
            responseMessages = []
            response_msg_item=''
            rawMessages = self.r_server.hgetall("KEY_ACTION_" + ste(eventID))
            dictMessageParams={}
            for message in rawMessages:
                strmessagesDetailsVal = rawMessages[message]
                strSubTitleInfo = ""
                strDictButtons = ""

                if strmessagesDetailsVal !='':
                    dictMessageDetails = json.loads(strmessagesDetailsVal)
                    strMessageList =  dictMessageDetails['MessageText']
                    strMessageType = dictMessageDetails['MessageType']
                    strButtonInfo = dictMessageDetails['MessageButtons']
                    strImageInfo = dictMessageDetails['MessageImage']
                    strMessageImage  = dictMessageDetails['MessageImage']
                    strMessageVideo = dictMessageDetails['MessageVideo']
                    strQuickReplies = dictMessageDetails['MessageQuickReplies']
                    #strListContent = dictMessageDetails["ListContent"]


                    arrMessageList = strMessageList.split("||")
                    strMessage = random.choice(arrMessageList)



                    arrReplaceableKeys = []
                    arrReplaceableKeys = re.findall(r"\{{([A-Za-z0-9_]+)\}}",strMessage)
                    if arrReplaceableKeys is not None:
                        for strReplaceableKey in arrReplaceableKeys:
                            strReplaceableValue = self.botLogicObj.getFromUserStateFromDict(fbid,strReplaceableKey)
                            strMessage = strMessage.replace("{{" + strReplaceableKey + "}}", strReplaceableValue)



                    intStart = strMessage.find('[[')
                    intEnd = strMessage.find(']]')
                    strLink = ""
                    strMessageTypeFromContent=""
                    if intStart > -1:
                        strSubAction = strMessage[intStart+2:intEnd]

                        recevied_message =  recevied_message.replace('"',"")
                        recevied_message =  recevied_message.replace("'","")

                        strSubActionFunctionSyntax = "self.botLogicObj." + strSubAction + "('" + fbid + "','" + recevied_message + "','" + strDictParams  + "')"
                        #####self.logger.info("printing subfunction" + strSubActionFunctionSyntax)
                        arrRetMessageDicts = eval(strSubActionFunctionSyntax)

                        ####self.logger.info("here 1")
                        ####self.logger.info(str(arrRetMessageDicts))
                        for dictMessageParams in arrRetMessageDicts:
                            if "NotificationType" in dictMessageParams:
                                strNotificationType =  dictMessageParams["NotificationType"]
                            strMessageTypeFromContent = dictMessageParams["MessageType"]
                            if strMessageTypeFromContent != "":
                                strMessageType =strMessageTypeFromContent
                                ######self.logger.info("here 2")
                            if strMessageType == 'Text':
                                response_msg_item = self.buildSimpleMessage(fbid, dictMessageParams["Message"],dictMessageParams["ImageURL"],dictMessageParams["VideoURL"],dictMessageParams["QuickReplies"],strNotificationType)
                            elif strMessageType == 'Buttons':
                                ######self.logger.info("test1")
                                response_msg_item = self.buildButtonMessage(fbid, dictMessageParams["Message"],dictMessageParams["DictButtons"],dictMessageParams["ImageURL"], dictMessageParams["SubTitleInfo"],dictMessageParams["ImageURL"],dictMessageParams["VideoURL"], dictMessageParams["Link"],dictMessageParams["DictButtons"],dictMessageParams["QuickReplies"],strNotificationType)
                                ####self.logger.info("test200")
                                ####self.logger.info("here 300000")
                            elif strMessageType == 'Image':
                                response_msg_item = self.buildImageMessage(fbid, dictMessageParams["Message"],dictMessageParams["ImageURL"],dictMessageParams["VideoURL"],dictMessageParams["QuickReplies"],strNotificationType)
                            elif strMessageType == 'List':
                                response_msg_item = self.buildListMessage(fbid,dictMessageParams["QuickReplies"],strNotificationType,dictMessageParams["ListContent"],dictMessageParams["ListButtons"])
                            elif strMessageType == 'Video':
                                #self.logger.info("making video message 1")
                                response_msg_item = self.buildVideoMessage(fbid, dictMessageParams["Message"],dictMessageParams["VideoURL"],dictMessageParams["VideoURL"],dictMessageParams["QuickReplies"],strNotificationType)

                                ######self.logger.info("here 4")

                            if response_msg_item !='':
                                responseMessages.append(response_msg_item)
                                ######self.logger.info("here 5")

                    else:

                        if strMessageType == 'Text':
                            response_msg_item = self.buildSimpleMessage(fbid, strMessage,strMessageImage,strMessageVideo,strQuickReplies,strNotificationType)
                        elif strMessageType == 'Buttons':
                            #######self.logger.info("test1")
                            if "QuickReplies" in dictMessageParams:
                                strQuickReplies1 =  dictMessageParams["QuickReplies"]
                            response_msg_item = self.buildButtonMessage(fbid, strMessage,strButtonInfo,strMessageImage, strSubTitleInfo,strMessageImage,strMessageVideo, "","",strQuickReplies1,strNotificationType)
                            ######self.logger.info("test290")
                        elif strMessageType == 'Image':
                            response_msg_item = self.buildImageMessage(fbid, strMessage,strMessageImage,strMessageVideo,strQuickReplies,strNotificationType)
                        elif strMessageType == 'Video':
                            response_msg_item = self.buildVideoMessage(fbid, strMessage,strMessageVideo,strMessageVideo,strQuickReplies,strNotificationType)


                        if response_msg_item !='':
                            responseMessages.append(response_msg_item)
            ####self.logger.info("-------->>")
            ####self.logger.info(str(responseMessages))
            return responseMessages
        except Exception,e:
            self.logger.error("buildMessage" +str(e))


    def buildSimpleMessage(self,fbid, responseMessage,imageURL="", videoURL="",strQuickReplies="",strNotificationType="SILENT"):
        try:
            response_msg_item = ''
            quickReplies = []
            if responseMessage == "":
                responseMessage = "_"
            dictMessage ={}
            dictMessage["recipient"] = {"id" : fbid}
            dictMessage["message"] ={}
            dictMessage["message"]["text"] =  responseMessage
            if strNotificationType == "SILENT":
                strNotificationType = "NO_PUSH"
            else :
                strNotificationType ="REGULAR"
            dictMessage["notification_type"] = strNotificationType

            if strQuickReplies != "":
                arrQuickReplies = strQuickReplies.split(",")
                for quickReply in arrQuickReplies:
                    quickReplyDetails = quickReply.split(":")
                    contentType = quickReplyDetails[0]
                    title =quickReplyDetails[1][:18]
                    payload = quickReplyDetails[2]
                    imageURL = ""
                    if len(quickReplyDetails)>3:
                        imageURL = quickReplyDetails[3]
                        imageURL =  "http://www.walnutai.com/static/curiousWorkbench/images/" +imageURL
                    if imageURL =="":
                        quickReplies.append({"content_type":contentType,"title":title,"payload":payload})
                    else:
                        quickReplies.append({"content_type":contentType,"title":title,"payload":payload,"image_url":imageURL})
                dictMessage["message"]["quick_replies"] = quickReplies

            if responseMessage !='' or len(quickReplies)!=0:
                response_msg_item = json.dumps(dictMessage)

            return response_msg_item
        except Exception,e:
            self.logger.error('buildSimpleMessage' + str(e))

    def buildVideoMessage(self,fbid, responseMessage,imageURL="", videoURL="",strQuickReplies="",strNotificationType="SILENT"):
        try:
            #self.logger.info("here 1-Video Message")
            response_msg_item = ''
            quickReplies = []
            if responseMessage == "":
                responseMessage = "_"
            dictMessage ={}
            dictAttachment ={}
            dictPayload= {}
            dictAttachment["type"]="video"
            dictPayload["url"]=videoURL
            dictAttachment["payload"]=dictPayload
            #dictMessage["attachment"] =dictAttachment

            dictMessage["recipient"] = {"id" : fbid}
            dictMessage["message"] = {"attachment" : dictAttachment}
            if strNotificationType == "SILENT":
                strNotificationType = "NO_PUSH"
            else :
                strNotificationType ="REGULAR"
            dictMessage["notification_type"] = strNotificationType

            #########self.logger.info("here 2")
            ########self.logger.info(json.dumps(dictMessage))

            if strQuickReplies != "":
                arrQuickReplies = strQuickReplies.split(",")
                for quickReply in arrQuickReplies:
                    quickReplyDetails = quickReply.split(":")
                    contentType = quickReplyDetails[0]
                    title =quickReplyDetails[1][:18]
                    payload = quickReplyDetails[2]

                    quickReplies.append({"content_type":contentType,"title":title,"payload":payload})

                dictMessage["message"]["quick_replies"] = quickReplies

            #if responseMessage !='' or len(quickReplies)!=0:
            #self.logger.info("----ok video message")
            #self.logger.info(str(dictMessage))
            response_msg_item = json.dumps(dictMessage)
            ########self.logger.info(responseMessage)
            return response_msg_item
        except Exception,e:
            self.logger.error('buildVideoMessage' + str(e))

    def buildImageMessage(self,fbid, responseMessage,imageURL="", videoURL="",strQuickReplies="",strNotificationType="SILENT"):
        try:
            #########self.logger.info("here 1")
            response_msg_item = ''
            quickReplies = []
            if responseMessage == "":
                responseMessage = "blank message"
            dictMessage ={}
            dictAttachment ={}
            dictPayload= {}
            dictAttachment["type"]="image"
            dictPayload["url"]=imageURL
            dictAttachment["payload"]=dictPayload
            #dictMessage["attachment"] =dictAttachment

            dictMessage["recipient"] = {"id" : fbid}
            dictMessage["message"] = {"attachment" : dictAttachment}
            if strNotificationType == "SILENT":
                strNotificationType = "NO_PUSH"
            else :
                strNotificationType ="REGULAR"
            dictMessage["notification_type"] = strNotificationType

            #########self.logger.info("here 2")
            ########self.logger.info(json.dumps(dictMessage))

            if strQuickReplies != "":
                arrQuickReplies = strQuickReplies.split(",")
                for quickReply in arrQuickReplies:
                    quickReplyDetails = quickReply.split(":")
                    contentType = quickReplyDetails[0]
                    title =quickReplyDetails[1][:18]
                    payload = quickReplyDetails[2]

                    quickReplies.append({"content_type":contentType,"title":title,"payload":payload})

                dictMessage["message"]["quick_replies"] = quickReplies

            if responseMessage !='' or len(quickReplies)!=0:
                response_msg_item = json.dumps(dictMessage)
            ########self.logger.info(responseMessage)
            return response_msg_item
        except Exception,e:
            self.logger.error('buildImageMessage' + str(e))

    def buildButtonMessage(self, fbid, responseMessage, buttonInfo,imageURL, subTitleInfo, strMessageImage, strMessageVideo, linkURL,strDictButtons,strQuickReplies,strNotificationType):
        try:

            response_msg_item = ''
            ####self.logger.info("1-1")

            if strNotificationType == "SILENT":
                strNotificationType = "NO_PUSH"
            else :
                strNotificationType ="REGULAR"

            if responseMessage !='':
                #---- Create Buttons
                strButtonInfo = buttonInfo
                arrButtons = strButtonInfo.split(',')
                #print '----------------------------1', buttonInfo
                #---------BuildButtons
                dictbuttons =[]
                if strDictButtons == "":

                    for button in arrButtons:
                        #print 'pppppppppp3'
                        #print '----------------------------2'
                        arrButtonInfo = button.split(':')
                        strButtonTitle = arrButtonInfo[0]
                        strButtonPostback = arrButtonInfo[1]
                        strButtonType = ""
                        if len(arrButtonInfo) ==3:
                            flagButtonType = arrButtonInfo[2]
                            if flagButtonType == "P":
                                strButtonType = "postback"
                            elif flagButtonType == "U":
                                strButtonType = "web_url"
                            elif flagButtonType =="S":
                                strButtonType = "element_share"
                        #print '----------------------------2.5'
                        dictbuttons.append(self.getButton(strButtonType,strButtonTitle, surl=linkURL, spayload=strButtonPostback))
                    #print '----------------------------3'
                else:
                    ####self.logger.info("1-2")
                    ####self.logger.info(strDictButtons)

                    dictbuttons = json.loads(strDictButtons)
                #------BuildPayload
                #-------BuildElements
                dictElements =[]
                dictElement = {}
                dictElement['title'] = responseMessage
                #dictElement['item_url'] = linkURL
                dictElement['image_url'] = imageURL
                dictElement['subtitle'] = subTitleInfo
                dictElement['buttons'] = dictbuttons
                dictElements.append(dictElement)
                #print '----------------------------4'

                dictPayload = {}
                dictPayload['template_type'] ='generic'
                dictPayload['elements'] = dictElements

                #------BuildAttachment
                dictAttachment = {}
                dictAttachment['type'] = 'template'
                dictAttachment['payload'] = dictPayload

                quickReplies=[]
                ####self.logger.info("1-3")
                if strQuickReplies != "":
                    arrQuickReplies = strQuickReplies.split(",")
                    for quickReply in arrQuickReplies:
                        quickReplyDetails = quickReply.split(":")
                        contentType = quickReplyDetails[0]
                        title =quickReplyDetails[1][:18]
                        payload = quickReplyDetails[2]
                        imageURL=""
                        if len(quickReplyDetails)>3:
                            imageURL = quickReplyDetails[3]
                            imageURL =  "http://www.walnutai.com/static/curiousWorkbench/images/" +imageURL
                        if imageURL =="":
                            quickReplies.append({"content_type":contentType,"title":title,"payload":payload})
                        else:
                            quickReplies.append({"content_type":contentType,"title":title,"payload":payload,"image_url":imageURL})


                    #dictMessage["message"]["quick_replies"] = quickReplies
                ####self.logger.info("1-4")

                if len(quickReplies) == 0:
                    response_msg_item = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":dictAttachment},"notification_type":strNotificationType})
                else:
                    response_msg_item = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":dictAttachment,"quick_replies":quickReplies},"notification_type":strNotificationType})

                #print '-------------------------------' ,response_msg_item,
            ####self.logger.info("1-5")
            return response_msg_item
        except Exception,e:
            self.logger.error('buildButtonMessage' + str(e))

    def buildListMessage(self, fbid,strQuickReplies,strNotificationType,strListContent,strListButtons):
        try:
            if strNotificationType == "SILENT":
                strNotificationType = "NO_PUSH"
            else :
                strNotificationType ="REGULAR"
            response_msg_item = ''
            responseMessage="1"
            ####self.logger.info("printing list content" +  strListContent[:50])
            arrListButtons = json.loads(strListButtons)
            arrListContent= json.loads(strListContent)
            if responseMessage !='':
                dictElements =[]
                for listContent in arrListContent:
                    dictbuttons =[]
                    arrButtons = []
                    if "Buttons" in listContent:
                        arrButtons=listContent["Buttons"]
                        dictbuttons.append(self.getButton(arrButtons["ButtonType"],arrButtons["ButtonTitle"], surl=arrButtons["ButtonLinkURL"], spayload=arrButtons["ButtonPostback"]))

                    dictElement = {}
                    if "Title" in listContent:
                        dictElement['title'] = listContent["Title"]
                    if "Image" in listContent:
                        dictElement['image_url'] = listContent["Image"]
                    if "SubTitle" in listContent:
                        dictElement['subtitle'] = listContent["SubTitle"]
                    if len(dictbuttons)>0:
                        dictElement['buttons'] = dictbuttons

                    dictElements.append(dictElement)
                #print '----------------------------4'

                dictPayload = {}
                dictPayload['template_type'] ='list'

                dictPayload['elements'] = dictElements
                dictPayload['buttons'] = arrListButtons

                #------BuildAttachment
                dictAttachment = {}
                dictAttachment['type'] = 'template'
                dictAttachment['payload'] = dictPayload

                quickReplies=[]
                ####self.logger.info("1-3")
                if strQuickReplies != "":
                    arrQuickReplies = strQuickReplies.split(",")
                    for quickReply in arrQuickReplies:
                        quickReplyDetails = quickReply.split(":")
                        contentType = quickReplyDetails[0]
                        title =quickReplyDetails[1][:18]
                        payload = quickReplyDetails[2]
                        imageURL=""
                        if len(quickReplyDetails)>3:
                            imageURL = quickReplyDetails[3]
                            imageURL =  "http://www.walnutai.com/static/curiousWorkbench/images/" +imageURL
                        if imageURL =="":
                            quickReplies.append({"content_type":contentType,"title":title,"payload":payload})
                        else:
                            quickReplies.append({"content_type":contentType,"title":title,"payload":payload,"image_url":imageURL})


                ####self.logger.info("1-4")

                if len(quickReplies) == 0:
                    response_msg_item = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":dictAttachment},"notification_type":strNotificationType})
                else:
                    response_msg_item = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":dictAttachment,"quick_replies":quickReplies},"notification_type":strNotificationType})

                #print '-------------------------------' ,response_msg_item,
            ####self.logger.info("1-5")
            #self.logger.info(response_msg_item)
            return response_msg_item
        except Exception,e:
            self.logger.error('buildListMessage' + str(e))
