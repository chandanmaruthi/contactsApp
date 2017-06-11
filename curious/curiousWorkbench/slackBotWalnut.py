# -*- coding: utf-8 -*-

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
import os
import json, requests, random, re
import MySQLdb
import logging
from configSettings import *
from elasticsearch import Elasticsearch
from dateutil import parser
from models import UserState, UserSkillStatus
from models import StateMachine, MessageLibrary, ContentLibrary, UserModuleProgress, Module, UserCertification
from django.shortcuts import get_list_or_404, get_object_or_404
import urllib

from models import UserState
import os.path
import apiai
from django.forms.models import model_to_dict
import mixpanel
from mixpanel import Mixpanel
mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")

class slackBotWalnut():

    configSettingsObj = configSettings()
    #----------------Logging ------------------
    logger = logging.getLogger('fbClientEventBot')
    #--------------------------------------------------------------------------------------------------------
    hdlr = logging.FileHandler( configSettingsObj.logFolderPath + 'fbClientAriseBot.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    #logger.info('logging log folder path')
    #logger.info(configSettingsObj.logFolderPath)
    #-------------------------------------------
    listOfRemoveStrings = ['<span>' , '</span>', '<br>', '</br>', '<br/>']
    logger.info('startedLoadingContent')
    r_server =  redis.Redis(host="localhost",db="14")



    def __init__(self):
        try:
            inputMsg='no value'
            lastTopicNumber = 15
            #self.logger.info('init')
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
                #self.logger.info( "starting NLP : " + inputMessage)
                apiAIRequest.query = inputMessage
                apiAIResponse = apiAIRequest.getresponse()
                strApiAIIntent =  apiAIResponse.read()
                responseDict =json.loads(strApiAIIntent)
                #self.logger.info( "NLP Feed : " + str(responseDict))

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


    def processEvent(self, event, fbid, recevied_message=''):
        try:
            self.logger.info("in  processEvent 1")
            self.logger.info(str(recevied_message))

            strToState = ''
            strCurrentState = self.getUserState(fbid)
            strMessage = ''
            self.logger.info("in  processEvent 2")

            if event == '' and strCurrentState=="CLEAR" and recevied_message !="":
                strEvent = self.NLProcessMessage(recevied_message)["INTENT"]
                if strEvent !="":
                    event = strEvent
                else:
                    event = 'MSG'
            elif event =='' and strCurrentState !="CLEAR" and recevied_message!="":
                event = 'MSG'
            self.logger.info("in  processEvent 3")

            dictEventInfo = event.split("-")
            eventCode = dictEventInfo[0]
            dictParams ={}
            for dictItem in dictEventInfo:
                arrParamInfo = dictItem.split("|")
                if len(arrParamInfo) == 2:
                    dictParams[arrParamInfo[0]] = arrParamInfo[1]
            strDictParams = json.dumps(dictParams)
            self.logger.info("strDictParams" + strDictParams)
            self.logger.info("KEY_EVENT_" + str(eventCode))

            stateMachineSubscriptions = self.r_server.hgetall("KEY_EVENT_" + str(eventCode))

            self.logger.info("step 2" + str(eventCode))
            self.logger.info(eventCode)

            self.logger.info("stateMachineSubscriptions" + str(stateMachineSubscriptions))
            self.logger.info("step 3")

            #strCurrentState = self.getUserState(fbid)
            self.logger.info("step 4")

            stateMachineSubscriptions = self.r_server.hgetall("KEY_EVENT_" + str(eventCode))
            self.logger.info("step 5")

            self.logger.info("stateMachineSubscriptions", str(stateMachineSubscriptions))
            for subscription in stateMachineSubscriptions:
                strAction = ""
                strNextEvent = ""
                strToState = ""
                strCallFunction = ""

                strVal = stateMachineSubscriptions[subscription]
                dictStateMachine = json.loads(strVal)
                strExpectedState = dictStateMachine['ExpectedState']
                self.logger.info(strCurrentState +" " + strExpectedState)
                process = False
                if strExpectedState == strCurrentState:
                    process = True
                elif strExpectedState =='':
                    process = True
                if process == True:
                    strAction =  dictStateMachine['Action']
                    strNextEvent = dictStateMachine['NextEvent']
                    strToState = dictStateMachine['State']
                    strCallFunction = dictStateMachine['CallFunction']

                    strAction1=strAction
                    strNextEvent1 =strNextEvent
                    strToState1 =strToState
                    strCallFunction1 =strCallFunction
                    if strAction == "":
                        strAction1 ="Msg"
                        if strNextEvent == "" : strNextEvent1 = "empty"
                        if strToState == "" : strToState1 = "empty"
                        if strCallFunction == "" : strCallFunction1 = "empty"
                    mp.track(fbid, strAction1,{'strNextEvent':strNextEvent,'strToState':strToState,'strCallFunction':strCallFunction})
                    self.logger.info("step 6.1")
                    if strCallFunction !='':
                        strCallFunctionSyntax = "self." + strCallFunction + "('" + fbid + "','" + recevied_message + "')"
                        self.logger.info(strCallFunctionSyntax)
                        eval(strCallFunctionSyntax)
                        self.logger.info("step 6.1.1-")


                    strMessage = self.buildMessage(strAction,fbid, recevied_message, strDictParams)
                    self.logger.info("step 6.2")

                    self.setUserCurrentState(fbid,strToState)
                    self.logger.info(strToState)
                    if strNextEvent1 !='':
                        strMessageNew = self.processEvent(strNextEvent1,fbid, '')
                        self.logger.info("printing internal processEvent" + str(strMessageNew))
                        if strMessage is None :
                            strMessage=[]
                        for message in strMessageNew:
                            strMessage.append(message)
                            self.logger.info(str(strMessage))
                            self.logger.info("step 6.3")
                        strMessageNew = ""

            return strMessage
        except Exception,e:
            self.logger.error("processEvent" + str(e))
            strMessage = self.buildMessage("msg_oops",fbid, "", "")
            return strMessage


    def getUserDetails(self, userID):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            if userStateObj.UserName =="":
                self.UpdateUserInfo(userID)

        except UserState.DoesNotExist:

            newUserState = UserState(UserID = userID,
                             UserCurrentState = 'INIT' ,
                         	UserLastAccessedTime = datetime.now())
            newUserState.save()

            self.UpdateUserInfo(userID)
            userStateObj = newUserState
        return userStateObj



    def setUserSkillStatus(self, userID,strDictSkills):
        try:

            if strDictSkills !="":
                dictSkills = json.loads(strDictSkills)
                for dictSkill in dictSkills:
                    newUserSkillStatus = UserSkillStatus(userID = userID,
                                     skill = dictSkill ,
                                     points = 0,
                                 	 LastActivityDate = datetime.now())
                    newUserSkillStatus.save()
        except Exception,e:
            self.logger.error('setUserSkillStatus' + str(e))


    def updateUserSkillStatus(self, userID,strSkill,intPoints):
        try:
            #self.logger.info("user details " + str(userID) + str(strSkill) +str(intPoints))

            userSkillStatusObj = UserSkillStatus.objects.get(userID = userID, skill = strSkill)
            #self.logger.info("check here")
            intOldPoints = int(userSkillStatusObj.points)
            intNewPoints = intOldPoints + int(intPoints)
            userSkillStatusObj.points = intNewPoints
            userSkillStatusObj.save()
        except UserSkillStatus.DoesNotExist:
            newUserSkillStatusObj = UserSkillStatus(userID = userID,
                             skill = strSkill ,
                             points = intPoints,
                         	 LastActivityDate = datetime.now())
            newUserSkillStatusObj.save()
            userSkillStatusObj = newUserSkillStatusObj
        return userSkillStatusObj

    def getUserSkillStatus(self, userID):
        userSkills = UserSkillStatus.objects.filter(userID=userID)
        return userSkills


    def UpdateUserInfo(self, userID):
        try:
            #self.logger.info("in add user" )
            post_message_url = self.configSettingsObj.facebookGraphAPIURL + userID + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + self.configSettingsObj.fbPageAccessTokenArise
            #self.logger.info("post url" + post_message_url )
            status = requests.get(post_message_url)
            if (status.ok):
                strUserDetails = status.content
                #self.logger.info("recevived response" + str(strUserDetails) )
                dictUserDetails = json.loads(strUserDetails)

                userStateObj = UserState.objects.get(pk=userID)
                userStateObj.UserName = dictUserDetails["first_name"] +" " + dictUserDetails["last_name"]
                userStateObj.UserEmail = ""
                userStateObj.UserGender = dictUserDetails["gender"]
                userStateObj.save()

                mp.track(userID, "New_User",{'User_Gender':dictUserDetails["gender"],'User_Age':'','':''})


                #----Set MixPanelUserDetails
                dictMPUserDetails = {}
                dictMPUserDetails["$first_name"] = dictUserDetails["first_name"]
                dictMPUserDetails["$last_name"] =dictUserDetails["last_name"]
                dictMPUserDetails["$email"] =""
                dictMPUserDetails["$phone"] =""
                dictMPUserDetails["$gender"] =dictUserDetails["gender"]
                mp.people_set(userID, dictMPUserDetails)
        except Exception,e:
            self.logger.error('UpdateUserInfo' + str(e))

    def getUserState(self, userID):
        try:
            userObj = self.getUserDetails(userID)
            return userObj.UserCurrentState
        except Exception,e:
            self.logger.error('getUserState' + str(e))

    def setUserCurrentState(self, userID, state):
        try:
            userObj = self.getUserDetails(userID)
            userObj.UserCurrentState = state
            userObj.save(force_update=True)
            return userObj.UserCurrentState
        except Exception,e:
            self.logger.error('setUserCurrentState' + str(e))

    def buildMessage(self, action, fbid, recevied_message,strDictParams):
        try:

            responseMessages = []
            response_msg_item=''
            rawMessages = self.r_server.hgetall("KEY_ACTION_" + action)

            for message in rawMessages:
                strmessagesDetailsVal = rawMessages[message]
                strSubTitleInfo = ""
                strDictButtons = ""

                if strmessagesDetailsVal !='':
                    dictMessageDetails = json.loads(strmessagesDetailsVal)
                    strMessage =  dictMessageDetails['MessageText']
                    strMessageType = dictMessageDetails['MessageType']
                    strButtonInfo = dictMessageDetails['MessageButtons']
                    strImageInfo = dictMessageDetails['MessageImage']
                    strMessageImage  = dictMessageDetails['MessageImage']
                    strMessageVideo = dictMessageDetails['MessageVideo']
                    strQuickReplies = dictMessageDetails['MessageQuickReplies']
                    intStart = strMessage.find('[[')
                    intEnd = strMessage.find(']]')
                    strLink = ""
                    strMessageTypeFromContent=""
                    if intStart > -1:
                        strSubAction = strMessage[intStart+2:intEnd]
                        strSubActionFunctionSyntax = "self." + strSubAction + "('" + fbid + "','" + recevied_message + "','" + strDictParams  + "')"
                        #self.logger.info(strSubActionFunctionSyntax)
                        strMessageTypeFromContent, strSubMessage,strImageInfo,strSubTitleInfo,strimageURL,strVideoURL,strLink,strDictButtons,strQuickReplies = eval(strSubActionFunctionSyntax)
                        strMessageImage = strimageURL
                        strMessageVideo = strVideoURL
                        strMessage = strSubMessage

                    if strMessageTypeFromContent != "":
                        strMessageType = strMessageTypeFromContent
                    if strMessageType == 'Text':
                        response_msg_item = self.buildSimpleMessage(fbid, strMessage,strMessageImage,strMessageVideo,strQuickReplies)
                    elif strMessageType == 'Buttons':
                        response_msg_item = self.buildButtonMessage(fbid, strMessage,strButtonInfo,strImageInfo, strSubTitleInfo,strMessageImage,strMessageVideo, strLink,strDictButtons)
                    elif strMessageType == 'Image':
                        response_msg_item = self.buildImageMessage(fbid, strMessage,strMessageImage,strMessageVideo,strQuickReplies)
                    if response_msg_item !='':
                        responseMessages.append(response_msg_item)
            return responseMessages
        except Exception,e:
            self.logger.error("buildMessage" +str(e))


    def buildSimpleMessage(self,fbid, responseMessage,imageURL="", videoURL="",strQuickReplies=""):
        try:
            response_msg_item = ''
            quickReplies = []
            if responseMessage == "":
                responseMessage = "blank message"
            dictMessage ={}
            dictMessage["recipient"] = {"id" : fbid}
            dictMessage["message"] ={}
            dictMessage["message"]["text"] =  responseMessage

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

            return response_msg_item
        except Exception,e:
            self.logger.error('buildSimpleMessage' + str(e))


    def buildImageMessage(self,fbid, responseMessage,imageURL="", videoURL="",strQuickReplies=""):
        try:
            #self.logger.info("here 1")
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
            #self.logger.info("here 2")
            #self.logger.info(json.dumps(dictMessage))

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
            #self.logger.info(responseMessage)
            return response_msg_item
        except Exception,e:
            self.logger.error('buildImageMessage' + str(e))

    def buildButtonMessage(self, fbid, responseMessage, buttonInfo,imageURL, subTitleInfo, strMessageImage, strMessageVideo, linkURL,strDictButtons):
        try:

            response_msg_item = ''
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

                if imageURL =='':
                    response_msg_item = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":dictAttachment}})
                else:
                    response_msg_item = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":dictAttachment}})

                #print '-------------------------------' ,response_msg_item,
            return response_msg_item
        except Exception,e:
            self.logger.error('buildButtonMessage' + str(e))



    def action_HandleMessage(self, userID, recevied_message):
        try:
            a='2'
            #print 'here'
        except Exception,e:
            #print '--9900--', str(e)
            self.logger.error('action_HandleMessage' + str(e))


    def actionGetLocationFromPin(self, userID, recevied_message,strDictParams="" ):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            strLocationPIN= userStateObj.Location_PIN
            #self.logger.info("in actionGetLocationFromPin " + strLocationPIN)
            post_message_url = "http://maps.googleapis.com/maps/api/geocode/json?address="
            post_message_url = post_message_url + strLocationPIN
            #self.logger.info(post_message_url)

            status = requests.get(post_message_url)
            strRetMsg = ""
            if (status.ok):
                strDetails = status.content
                dictResult = json.loads(strDetails)
                if "results" in dictResult:
                    if "formatted_address" in dictResult["results"][0]:
                        strFormattedAddress =  dictResult["results"][0]["formatted_address"]
                strRetMsg=  "thats " +  strFormattedAddress
            return "Text", strRetMsg, "", "", "", "", "", "",""
        except Exception,e:
            self.logger.error('actionGetLocationFromPin' + str(e))



    def actionGetReco(self, userID, recevied_message,strDictParams=""):
        try:

            intNumberOfKeys = len(self.r_server.keys(pattern="KEY_CONTENT_*"))

            intRantInt = randint(0,intNumberOfKeys)
            strContent= self.r_server.hget( "KEY_CONTENT_"+str(intRantInt), "Msg")
            dictContent = json.loads(strContent)
            strMessageType = dictContent["Message_Type"]
            if len(dictContent["Title"]) >79:
                strMessage = dictContent["Title"][:79]
            else :
                strMessage = dictContent["Title"]
            strVideoURL = ""
            strImage = ""
            if len(dictContent["Skill"]) > 70:
                strSubTitleInfo = dictContent["Skill"][:69]
            else:
                strSubTitleInfo = dictContent["Skill"]
            strSubTitleInfo = "Skill : " + strSubTitleInfo + "    " + "Claim: 1pt"
            strLink = dictContent["LinkURL"]
            if dictContent["ImageURL"] != "":
                strImage =   dictContent["ImageURL"]

            dictButtons =[]
            strLink = self.configSettingsObj.webUrl + "/curiousWorkbench/fbABWCV/" + str(dictContent["ID"])

            dictButtons.append(self.getButton("web_url","read",surl=strLink,spayload=""))
            if dictContent["Questions"] != "":
                payload = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + str(dictContent["ID"])
                dictButtons.append(self.getButton("postback","claim 1 pt",surl="",spayload=payload))
            dictButtons.append(self.getButton("postback","next",surl="",spayload="SHOW_RECO"))
            strDictButtons = json.dumps(dictButtons)
            strQuickReplies = ""

            return strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
        except Exception,e:
            self.logger.error('actionGetReco' + str(e))

    def actionGetModule(self, userID, recevied_message,strDictParams=""):
        try:
            #self.logger.info("actionGetModule", userID, recevied_message, strDictParams)
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "ID" in dictParams:
                    moduleID = dictParams["ID"]
                else:
                    moduleID = 1
            else:
                moduleID = 1
            #dictParams={"ID":1}
            strModule= self.r_server.hget( "KEY_MODULE_"+str(moduleID), "ID")
            dictModule = json.loads(strModule)
            strMessage = dictModule["Title"][:39] + " (in " + dictModule["SKILL_CODE"].replace("_"," ")[:29] + " )"
            strVideoURL = ""
            strImage = dictModule["AuthorURL"]
            strSubTitleInfo = "by: "+ str(dictModule["Author"][:20]) + "         " + str(dictModule["UnitsPerDay"]) + " mins"
            dictButtons =[]
            strLink =""
            payload = "START_MODULE" + "-" + "Module_ID" + "|" + str(dictModule["ID"])
            dictButtons.append(self.getButton("postback","Pick up this skill",surl="",spayload=payload))
            strDictButtons = json.dumps(dictButtons)
            strQuickReplies = ""

            return "",strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
        except Exception,e:
            self.logger.error('actionGetModule' + str(e))

    def actionStartModule(self, userID, recevied_message,strDictParams=""):
        try:

            #self.logger.info("")
            #User Accepts Module
            # - postback: Start_Module(ModuleID)
            # - Update UserState.Current Module with Module ID
            # - If No Entry in Module Progress , add and entry
            # - Get the first entry from Module
            # - Show user
            moduleID=0
            contentOrder=0
            if strDictParams!="":
                dictParams = json.loads(strDictParams)
                if "Module_ID" in dictParams:
                    moduleID=dictParams["Module_ID"]
                if "Content_Order" in dictParams:
                    contentOrder =dictParams["Content_Order"]
                else:
                    contentOrder = 0
            strModule= self.r_server.hget( "KEY_MODULE_"+str(moduleID), "ID")
            dictModule = json.loads(strModule)

            # Update Current Module ID in under state
            userStateObj = UserState.objects.get(pk=userID)
            userStateObj.Current_Module_ID = dictModule["ID"]
            userStateObj.save()
            # Get first message of content
            #contentObj =  ContentLibrary.objects.filter(Module_ID=dictModule["ID"]).order_by('Content_Order').first()
            #if contentObj !=None:
            #    intCurrentPosition = contentObj.Content_Order
            # Update Current Module ID in under state
            intCurrentPosition =1
            userModuleProgressObj = UserModuleProgress.objects.filter(ModuleID=dictModule["ID"], UserID=userID)
            if userModuleProgressObj == None:
                userModuleProgressObj =  UserModuleProgress()
                userModuleProgressObj.UserID = userID
                userModuleProgressObj.ModuleID = dictModule["ID"]
                userModuleProgressObj.CurrentPosition =intCurrentPosition
                userStateObj.save()
            else:
                userModuleProgressObj.CurrentPosition = intCurrentPosition
                userStateObj.save()

            #prepare content to send
            strMessage = ""
            strSubTitleInfo = ""
            strImage = ""
            strImage = ""
            strVideoURL  = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""
            strMessageType = ""
            strMessageType = ""
            # if strMessageType =="Text":
            #     strMessage = contentObj.Text[:295]
            #     strQuickReplyPostback = "NEXT_MODULE_CONTENT" + "-" +"Module_ID" + "|" +str(dictModule["ID"])+ "-"+ "Content_Order" + "|" + str(intCurrentPosition+1)
            #     strQuickReplies += "text" + ":" + "ok" + ":" + strQuickReplyPostback
            dictReturnParams = {"Module_ID":moduleID,"Content_Order":contentOrder+1}
            strDictReturnParams = json.dumps(dictReturnParams)
            strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies = self.actionNextModuleContent(userID, recevied_message,strDictReturnParams)
            # strMessage = contentObj["Title"][:79]
            # strVideoURL = ""
            # strImage = dictModule["AuthorURL"]
            # strSubTitleInfo = dictModule["Description"][:69]
            # dictButtons =[]
            # strLink =""
            # payload = "START_MODULE" + "-" + "ID" + "|" + str(dictModule["ID"])
            # dictButtons.append(self.getButton("postback","Get Started",surl="",spayload=payload))
            # strDictButtons = json.dumps(dictButtons)
            # strQuickReplies = ""

            return strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
        except Exception,e:
            self.logger.error('actionStartModule' + str(e))


    def actionNextModuleContent(self, userID, recevied_message,strDictParams=""):
        try:


            #User Accepts Module
            # - postback: Start_Module(ModuleID)
            # - Update UserState.Current Module with Module ID
            # - If No Entry in Module Progress , add and entry
            # - Get the first entry from Module
            # - Show user
            #self.logger.info("actionNextModuleContent" + str(userID) +str(recevied_message)+str(strDictParams))

            if strDictParams!="":
                dictParams = json.loads(strDictParams)
            #self.logger.info("heeree 1")

            strModule= self.r_server.hget( "KEY_MODULE_"+str(dictParams["Module_ID"]), "ID")
            dictModule = json.loads(strModule)
            #self.logger.info("heeree 2")

            strMessage = ""
            strSubTitleInfo = ""
            strImage = ""
            strImage = ""
            strVideoURL  = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""
            strMessageType = ""
            strMessageType = ""

            # Get first message of content
            contentObj =  ContentLibrary.objects.filter(Module_ID=dictParams["Module_ID"],Content_Order=dictParams["Content_Order"]).first()
            #self.logger.info("heeree 3")
            #self.logger.info(str(contentObj))
            if contentObj !=None:
                #self.logger.info("heeree 4")
                #self.logger.info(contentObj.Content_Order)
                intCurrentPosition = contentObj.Content_Order
            # Update Current Module ID in under state
                #self.logger.info("ok")
                userModuleProgressObj = UserModuleProgress.objects.filter(ModuleID=dictModule["ID"], UserID=userID).first()
                #self.logger.info("ok1")

                if userModuleProgressObj == None:
                    userModuleProgressObj =  UserModuleProgress()
                    userModuleProgressObj.UserID = userID
                    userModuleProgressObj.ModuleID = dictModule["ID"]
                    userModuleProgressObj.CurrentPosition = intCurrentPosition
                    userModuleProgressObj.save()
                else:
                    userModuleProgressObj.CurrentPosition = intCurrentPosition
                    userModuleProgressObj.save()
                #self.logger.info("ok2")

                #prepare content to send
                strMessageType = contentObj.Message_Type
                if strMessageType =="Text":
                    strMessage = contentObj.Text[:255]
                    strMessage += " (" + str(contentObj.Content_Order) + "/" + str(dictModule["Units"]) + ")"
                elif strMessageType =="Image":
                    strImage = contentObj.ImageURL
                #self.logger.info("ok3")
                if contentObj.Questions !="":
                    strQuickReplyPostback = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + str(contentObj.ID)
                    strQuickReplies += "text" + ":" + "ok" + ":" +strQuickReplyPostback
                else:
                    strQuickReplyPostback = "NEXT_MODULE_CONTENT" + "-" +"Module_ID" + "|" +str(dictParams["Module_ID"])+ "-"+ "Content_Order" + "|" + str(intCurrentPosition+1)
                    strQuickReplies += "text" + ":" + "ok" + ":" +strQuickReplyPostback

                return strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
            else:
                #self.logger.info("heeree 4")

                # Module Ended, clear memory
                userStateObj = UserState.objects.get(pk=userID)
                userStateObj.Current_Module_ID = None
                userStateObj.save()
                # Remove Progress Entries in Module Progress
                userModuleProgressObj = UserModuleProgress.objects.filter(ModuleID=dictParams["Module_ID"], UserID=userID).first()
                if userModuleProgressObj != None:
                    userModuleProgressObj.delete()

                strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies = self.actionGetModuleCompletionMessage(userID,recevied_message,strDictParams)
                return strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies


        except Exception,e:
            self.logger.error('actionNextModuleContent' + str(e))


    def actionGetModuleCompletionMessage(self, userID, recevied_message, strDictParams=""):
        try:
            strMessage = ""
            strSubTitleInfo = ""
            strImage = ""
            strImage = ""
            strVideoURL  = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""
            strMessageType = "Text"
            #self.logger.info("heeree 10")
            if strDictParams!="":
                dictParams = json.loads(strDictParams)
            objModule = Module.objects.get(ID=int(dictParams["Module_ID"]))
            objUserCertification = UserCertification.objects.filter(Module_ID=int(dictParams["Module_ID"]), userID=userID).first()
            #self.logger.info("heeree 20")
            if objUserCertification == None:
                objUserCertification = UserCertification()
                objUserCertification.userID = userID
                objUserCertification.Module_ID =  int(dictParams["Module_ID"])
                objUserCertification.date = datetime.now()
                objUserCertification.Title = objModule.Title
                objUserCertification.Author = objModule.Author
                objUserCertification.AuthorURL = objModule.AuthorURL
                objUserCertification.SKILL_CODE = objModule.SKILL_CODE
                objUserCertification.save()
                #self.logger.info("heeree 25")
            else:
                objUserCertification.date =datetime.now()
                objUserCertification.Title = objModule.Title
                objUserCertification.Author = objModule.Author
                objUserCertification.AuthorURL = objModule.AuthorURL
                objUserCertification.SKILL_CODE = objModule.SKILL_CODE
                objUserCertification.save()
                #self.logger.info("heeree 26")
            #self.logger.info("heeree 30")
            strMessage="Awesome, you have compelted this topic"
            strImage = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/CertificateImageLarge.png"
            strMessageType = "Buttons"
            strSubTitleInfo = "This topic has been added to your skill board"
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl + "/curiousWorkbench/fbABWCertV/" + str(userID)
            #self.logger.info("heeree 40")

            strLinkedInShareURL = "https://www.linkedin.com/shareArticle?mini=true&"
            dictLinkedInURLParams ={}
            dictLinkedInURLParams["url"] = self.configSettingsObj.webUrl
            dictLinkedInURLParams["title"] = objModule.Title
            dictLinkedInURLParams["summary"] = "I just acquired this short skill."
            dictLinkedInURLParams["source="] = "Walnut Ai - Learn skills bot"
            strLinkedInURLParams = urllib.urlencode(dictLinkedInURLParams)
            strLinkedInShareURL = strLinkedInShareURL + strLinkedInURLParams

            dictButtons.append(self.getButton("web_url","See my skill board",surl=strLink,spayload=""))
            dictButtons.append(self.getButton("web_url","Share on LinkedIn",surl=strLinkedInShareURL,spayload=""))
            dictButtons.append(self.getButton("postback","Learn more skills",surl=strLinkedInShareURL,spayload="ROLE_DEMAND_INFO"))
            strDictButtons= json.dumps(dictButtons)
            #self.logger.info("heeree 59")
            return strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
        except Exception,e:
            self.logger.error('actionGetModuleCompletionMessage' + str(e))

    def actionGetSearch(self, userID, recevied_message,strDictParams=""):
        try:
            strMessage = ""
            es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
            results =  es.search(index="messages", body={"query": {"match": {'_all':str(recevied_message)}}})
            dD = results["hits"]["hits"]
            if not dD :
                strMessage = "Did not find anything, try something else"
            else:
                lenD = len(results["hits"]["hits"])
                if lenD >1 :
                    intRantInt = randint(0,lenD-1)
                    strMessage = results["hits"]["hits"][intRantInt]["_source"]["title"][0].encode('ascii', 'ignore')
                else:
                    strMessage = "Did not find anything, try something else"
            strImage = results["hits"]["hits"][intRantInt]["_source"]["image"][0].encode('ascii', 'ignore')
            strDate = results["hits"]["hits"][intRantInt]["_source"]["date"][0].encode('ascii', 'ignore')

            if strDate != "":
                dt = parser.parse(strDate)
                strFmtDate = str(dt.date()) + " " + str(dt.hour) + ":00" + " @ "

            strLocation = results["hits"]["hits"][intRantInt]["_source"]["location"][0].encode('ascii', 'ignore')
            for strReplaceStr in self.listOfRemoveStrings:
                strLocation = strLocation.replace(strReplaceStr,"")

            strSubTitleInfo = strFmtDate + strLocation
            return strMessage, strImage, strSubTitleInfo, "", ""
        except Exception,e:
            self.logger.error("actionGetSearch" + str(e))

    def actionGetSingleReco(self, userID, recevied_message,strDictParams=""):
        try:



            intNumberOfKeys = len(self.r_server.keys(pattern="KEY_CONTENT_*"))
            intRantInt = randint(0,intNumberOfKeys)
            strContent= self.r_server.hget( "KEY_CONTENT_"+intRantInt, "Msg")
            dictContent = json.loads(strContent)
            if len(dictContent["Title"]) >79:
                strMessage = dictContent["Title"][:79]
            else :
                strMessage = dictContent["Title"]
            strVideoURL = ""
            strImage = ""
            if len(dictContent["Skill"]) > 70:
                strSubTitleInfo = dictContent["Skill"][:69]
            else:
                strSubTitleInfo = dictContent["Skill"]
            strSubTitleInfo = "Skill : " + strSubTitleInfo + "    " + "Claim: 1pt"
            strLink = dictContent["LinkURL"]
            if dictContent["ImageURL"] != "":
                strImage =  dictContent["ImageURL"]
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl + "/curiousWorkbench/fbABWCV/" + str(dictContent["ID"])
            dictButtons.append(self.getButton("web_url","read more",surl=strLink,spayload=""))
            if dictContent["Questions"] != "":
                payload = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + dictContent["ID"]
                dictButtons.append(self.getButton("postback","challenge 1 pt",surl="",spayload=payload))
            dictButtons.append(self.getButton("postback","next article",surl="",spayload="SHOW_RECO"))
            strDictButtons = json.dumps(dictButtons)
            strQuickReplies = ""

            return strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies

        except Exception,e:
            self.logger.error('actionGetSingleReco' + str(e))


    def actionAskQuestion(self, userID, recevied_message,strDictParams=""):
        try:
            if strDictParams !="":

                #self.logger.info("askQuestions params:" + strDictParams)
                dictParams = json.loads(strDictParams)
                #self.logger.info("here -2")

                strContentID = dictParams["ContentID"]
                strContent= self.r_server.hget( "KEY_CONTENT_"+strContentID, "Msg")
                #self.logger.info("here -1")
                #self.logger.info(strContent)

                dictContent = json.loads(strContent)
                strMessage = dictContent["Questions"][:79]
                #self.logger.info("here 0")

                strAnswerOptions = dictContent["AnswerOptions"]

                #self.logger.info("here 1")

                dictAnswerOptions = strAnswerOptions.split("|")
                strVideoURL = ""
                strImage = ""
                #strSubTitleInfo = dictContent["Subtitle"]
                strSubTitleInfo =""
                strLink = ""
                strImage = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/sunAskQuestion.jpg"
                dictButtons =[]
                #self.logger.info("In Ask Question")
                for answerOption in dictAnswerOptions:
                    arrAnswerOption = answerOption.split(":")
                    if len(arrAnswerOption)==2:
                        payload = "ANSWER_TO_QUESTION" + "-" + "ContentID" + "|" + str(dictContent["ID"]) + "-" + "AnswerID" + "|" + str(arrAnswerOption[0])
                        strAnswerOptionText = arrAnswerOption[1][:19]
                        dictButtons.append(self.getButton("postback",strAnswerOptionText,surl="",spayload=payload))
                strDictButtons = json.dumps(dictButtons)
                strQuickReplies = ""
                #self.logger.info("Posted Message")
                return "", strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
            else:
                strImage=""
                strVideoURL=""
                strLink=""
                strDictButtons=""
                strQuickReplies=""
                return "", "no content", strImage, "no content", strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
        except Exception,e:
            self.logger.error('actionAskQuestion' + str(e))




    def actionReviewAnswer(self, userID, recevied_message,strDictParams=""):
        try:
            if strDictParams !="":
                #self.logger.info("actionReviewAnswer:" + strDictParams)
                dictParams = json.loads(strDictParams)
                strContentID = dictParams["ContentID"]
                strAnswerID = dictParams["AnswerID"]
                strContent= self.r_server.hget( "KEY_CONTENT_"+strContentID, "Msg")
                dictContent = json.loads(strContent)
                strCorrectAnswerID = dictContent["RightAnswer"]
                #self.logger.info( "---review ans "+ strAnswerID + strCorrectAnswerID )
                strQuickReplies = ""
                userModuleProgressObj = UserModuleProgress.objects.filter(ModuleID=dictContent["Module_ID"], UserID=userID).first()
                intCurrentPosition = userModuleProgressObj.CurrentPosition
                if strAnswerID == strCorrectAnswerID :
                    strMessage = "Thats Correct :-), you claimed 1 pt"
                    userSkillStatusObj = self.updateUserSkillStatus(userID,dictContent["Skill"],1)
                    strQuickReplyPostback = "NEXT_MODULE_CONTENT" + "-" +"Module_ID" + "|" +str(dictContent["Module_ID"])+ "-"+ "Content_Order" + "|" + str(intCurrentPosition+1)
                    strQuickReplies += "text" + ":" + "ok" + ":" +strQuickReplyPostback

                if strAnswerID != strCorrectAnswerID:
                    strMessage = "Oops! :-( thats incorrect , try again"

                strVideoURL = ""
                strImage = ""
                strSubTitleInfo = ""
                strLink = ""
                strImage = ""
                strDictButtons =""
                return "Text", strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
            else:
                strImage=""
                strVideoURL=""
                strLink=""
                strDictButtons=""
                strQuickReplies=""
                return "","no content", strImage, "no content", strImage, strVideoURL, strLink, strDictButtons, strQuickReplies
        except Exception,e:
            self.logger.error('actionReviewAnswer' + str(e))


    def actionGetUserProgress(self, userID, recevied_message,strDictParams=""):
        try:
            # objQuerySet= self.getUserSkillStatus(userID)
            # strSkillStatus = ""
            # for objUserSkillStatus in objQuerySet:
            #     strSkillStatus += objUserSkillStatus.skill + " : " + objUserSkillStatus.points + "points \r\n"
            # if strSkillStatus !="":
            #     strSkillStatus = "Ok here is our progress so far \r\n" + strSkillStatus
            #
            # if strSkillStatus == "":
            #     strSkillStatus = "Your points are at 0, Check out a skill and claim points to get started"
            # strMessage =strSkillStatus
            # strVideoURL = ""
            # strImage = ""
            # strSubTitleInfo = ""
            # strLink = ""
            # strImage =  ""
            # strLink = ""
            # strDictButtons =""
            # if len(dictContent["Skill"]) > 70:
            #     strSubTitleInfo = dictContent["Skill"][:69]
            # else:
            #     strSubTitleInfo = dictContent["Skill"]
            # strSubTitleInfo = "Skill : " + strSubTitleInfo + "    " + "Claim: 1pt"
            # strLink = dictContent["LinkURL"]
            # if dictContent["ImageURL"] != "":
            #     strImage =  dictContent["ImageURL"]
            # dictButtons =[]
            # strLink = self.configSettingsObj.webUrl + "/curiousWorkbench/fbABWCV/" + str(dictContent["ID"])
            # dictButtons.append(self.getButton("web_url","read more",surl=strLink,spayload=""))
            # dictButtons.append(self.getButton("postback","next article",surl="",spayload="SHOW_RECO"))
            # strDictButtons = json.dumps(dictButtons)
            # strQuickReplies = ""
            strMessage = ""
            strSubTitleInfo = ""
            strImage = ""
            strImage = ""
            strVideoURL  = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""
            strMessageType = "Text"
            strMessage="Here we go, click on view progress."
            strImage = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/CertificateImageLarge.png"
            strMessageType = "Buttons"
            strSubTitleInfo = "Check It Out"
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl + "/curiousWorkbench/fbABWCertV/" + str(userID)
            #self.logger.info("heeree 40")
            dictButtons.append(self.getButton("web_url","View Proress",surl=strLink,spayload=""))
            strDictButtons= json.dumps(dictButtons)
            #self.logger.info("heeree 59")
            return strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies

        except Exception,e:
            self.logger.error('actionGetUserProgress' + str(e))



    def actionSaveUserLocation(self, userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            userStateObj.Location_PIN = recevied_message
            userStateObj.save()
            strMessage = "BLANK BLANK"
            strImage=""
            strSubTitleInfo=""
            return strMessage, strImage, strSubTitleInfo, "", ""
        except Exception,e:
            self.logger.error('actionSaveUserLocation' + str(e))

    def actionSetUserRole(self, userID, recevied_message,strDictParams=""):
        try:
            #self.logger.info('actionSetUserRole')
            #self.logger.info('--' + str(userID))
            userStateObj = get_object_or_404(UserState, UserID=userID)

            if recevied_message == "Product Manager":
                strRole = "Product_Manager"
            elif recevied_message == "Program Manager":
                strRole = "Program_Manager"
            elif recevied_message =="Engineering Manager":
                strRole ="Engineering_Manager"
            else :
                strRole = "Product_Manager"

            userStateObj.UserRole = strRole
            userStateObj.save()
            strMessage = "BLANK BLANK"
            strImage=""
            strSubTitleInfo=""
            return strMessage, strImage, strSubTitleInfo, "", ""
        except Exception,e:
            self.logger.error('actionSetUserRole' + str(e))

    def actionSaveUserLocationProdM(self, userID, recevied_message,strDictParams=""):
        try:
            #self.logger.info('actionSaveUserLocationProdM')
            self.actionSetUserRole(userID, "Product_Manager")
        except Exception,e:
            self.logger.error('actionSaveUserLocationProdM' + str(e))

    def actionSaveUserLocationProgM(self, userID, recevied_message,strDictParams=""):
        try:
            #self.logger.info('actionSaveUserLocationProgM')
            self.actionSetUserRole(userID, "Program_Manager")
        except Exception,e:
            self.logger.error('actionSaveUserLocationProgM' + str(e))

    def actionSaveUserLocationEggM(self, userID, recevied_message,strDictParams=""):
        try:
            #self.logger.info('actionSaveUserLocationEggM')
            self.actionSetUserRole(userID, "Engineering_Manager")
        except Exception,e:
            self.logger.error('actionSaveUserLocationEggM' + str(e))


    def actionSetUserCompany(self, userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            userStateObj.UserCompany = recevied_message
            userStateObj.save()
            strMessage = "BLANK BLANK"
            strImage=""
            strSubTitleInfo=""
            return strMessage, strImage, strSubTitleInfo, "", ""
        except Exception,e:
            self.logger.error('actionSetUserCompany' + str(e))


    def actionSaveSelfEvalSkillData(self, userID, recevied_message,strDictParams=""):
        try:

            strMessage = "BLANK BLANK"
            strImage=""
            strSubTitleInfo=""
            return strMessage, strImage, strSubTitleInfo, "", ""
        except Exception,e:
            self.logger.error('actionSaveSelfEvalSkillData' + str(e))

    def actionGetRoleDemandInfo(self, userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            strUserRole =  userStateObj.UserRole

            roleInfo = self.r_server.hgetall("KEY_ROLE_" + strUserRole)
            #self.logger.info(str(roleInfo))
            strMessage = "Here are the top 3 skills by demand\r\n"
            intMax = 4
            intCount = 0
            strQuickReplies = ""
            strRoleInfoDesc = ""
            for role in roleInfo:
                if intCount <= intMax:
                    dictRoleInfo = json.loads(roleInfo[role])
                    if dictRoleInfo["Enabled"]=="TRUE":
                        moduleObj = Module.objects.filter(SKILL_CODE=dictRoleInfo["SKILL_CODE"]).first()
                        strRoleInfoDesc += dictRoleInfo["Skill"] + " [Code : " + str(moduleObj.ID) + "]"+ "\r\n"
                        if intCount != 0:
                            strQuickReplies += ","

                        #self.logger.info("---->Module Options" + dictRoleInfo["SKILL_CODE"] + strUserRole)
                        if moduleObj != None:
                            moduleID = moduleObj.ID
                            strPayLoad = "SHOW_MODULE" + "-" + "ID" + "|" + str(moduleID)
                        strQuickReplies += "text" + ":" + str(moduleID) + ":" + strPayLoad
                        #self.logger.info("I am still here -------")
                        intCount +=1
            strRoleInfoDesc += "I will keep looking for more. \r\n Select a code below to acquire a skill "
            strMessage += strRoleInfoDesc

            strSubTitleInfo = ""
            strImage=""
            strMessage =  strMessage[:295]
            strDictButtons = ""

            return "",strMessage, strImage, strSubTitleInfo, strImage, "",self.configSettingsObj.webUrl , strDictButtons,strQuickReplies
        except Exception,e:
            self.logger.error('actionGetRoleDemandInfo' + str(e))

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
