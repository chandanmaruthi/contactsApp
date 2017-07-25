# -*- coding: utf-8 -*-
import sys
import os
import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
from itertools import izip
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
from django.core.exceptions import ObjectDoesNotExist

from models import UserState, UserSkillStatus
from models import StateMachine, MessageLibrary, ContentLibrary, UserModuleProgress, Module, UserCertification,RoleDemandInfo,Progress, Challenge,ChallengeResultSummary,ChallengeResultUser,PlatformCredentials, UserActions
from django.shortcuts import get_list_or_404, get_object_or_404
import urllib

import os.path
import apiai
from django.forms.models import model_to_dict
import mixpanel
from mixpanel import Mixpanel
mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")
import pygal
from pygal.style import DefaultStyle
from pygal.style import Style
import re
from urlparse import urlparse
from os.path import splitext, basename
from django.db import connection
#A Content is the fundamental unit of knowdledge, It can be redered as part of a module or independent of it, A Challenge may be assiciated with content/module
class botLogic(object):
    configSettingsObj = configSettings()
    #----------------Logging ------------------
    logger = logging.getLogger('fbClientEventBot')
    #--------------------------------------------------------------------------------------------------------
    hdlr = logging.FileHandler( configSettingsObj.logFolderPath + 'botLogic.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    #logger.info('logging log folder path')
    #logger.info(configSettingsObj.logFolderPath)
    #-------------------------------------------
    listOfRemoveStrings = ['<span>' , '</span>', '<br>', '</br>', '<br/>']
    r_server =  redis.Redis(host=configSettingsObj.inMemDbHost,db=configSettingsObj.inMemDataDbName)
    r_stateServer =  redis.Redis(host=configSettingsObj.inMemDbHost,db=configSettingsObj.inMemStateDbName)
    platformFlag="Facebook"

    def __init__(self, platform):
        try:
            inputMsg='no value'
            lastTopicNumber = 15
            db = MySQLdb.connect(host=self.configSettingsObj.dbHost,    # your host, usually localhost
                                 user=self.configSettingsObj.dbUser,         # your username
                                 passwd=self.configSettingsObj.dbPassword,  # your password
                                 db=self.configSettingsObj.dbName)        # name of the data base

            self.platformFlag = platform
        except Exception,e:
            self.logger.error('fbClient init here' + str(e))

    def query_to_dicts(self, query_string, *query_args):
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

    def getButton(self, stype, stitle, surl='', spayload=''):

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

        return dictButton

    def getUserDetails(self, userID):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            if userStateObj.UserName =="":
                if self.platformFlag == "Facebook":
                    self.UpdateUserInfoFacebook(userID)
                elif self.platformFlag ==  "Slack":
                    self.UpdateUserInfoSlack(userID)
        except UserState.DoesNotExist:

            newUserState = UserState(UserID = userID,
                             UserCurrentState = 'INIT' ,
                         	UserLastAccessedTime = datetime.now())
            newUserState.save()
            #mp.track(userID, "New_User",{'User_Gender':dictUserDetails["gender"],'User_Age':'','':''})
            if self.platformFlag == "Facebook":
                self.UpdateUserInfoFacebook(userID)
            elif self.platformFlag ==  "Slack":
                self.UpdateUserInfoSlack(userID)

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

            userSkillStatusObj = UserSkillStatus.objects.get(userID = userID, skill = strSkill)
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

    def action_HandleMessage(self, userID, recevied_message):
        try:
            a='2'
            #print 'here'
        except Exception,e:
            #print '--9900--', str(e)
            self.logger.error('action_HandleMessage' + str(e))

    def action_showRandomMessage(self,userID, recevied_message,strDictParams=""):
        try:
            post_message_url = "http://api.giphy.com/v1/gifs/search?q=say+what&api_key=dc6zaTOxFJmzC&limit=10"
            status = requests.get(post_message_url)
            #jsonContent = json.loads(status)

            strRetMsg = ""
            strImage =""
            intRantInt = randint(0,9)
            if (status.ok):
                strDetails = status.content
                dictResult = json.loads(strDetails)
                strImage = dictResult["data"][intRantInt]["images"]["original"]["url"]
            strMessageType = "Buttons"
            strMessage = "Hmm,I did not get that!"
            strMessage += "\r\n Here are a few things you can do "
            strMessage += "\r\n *Search* : To search for a Stash"
            strMessage += "\r\n *Create Stash*: To create concepts "
            strMessage += "\r\n *Share Stash*: To share Stash "
            strMessage += "\r\n *Show skills*: To see relevant skills say "
            strMessage += "\r\n *Show Insight*: To check out an insight say "
            strVideoURL = ""
            #strImage =""
            strSubTitleInfo = ""
            strLink = ""
            dictButtons =[]
            payload = "SHOW_SKILLS"
            dictButtons.append(self.getButton("postback","explore a skill",surl="",spayload=payload))
            strLink = ""
            strQuickReplies = ""
            strDictButtons = json.dumps(dictButtons)

            strQuickReplies =""
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict(strMessageType,strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('action_showRandomMessage ' + str(e))

    def actionGetLocationFromPin(self, userID, recevied_message,strDictParams="" ):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            strLocationPIN= userStateObj.Location_PIN
            post_message_url = "http://maps.googleapis.com/maps/api/geocode/json?address="
            post_message_url = post_message_url + strLocationPIN

            status = requests.get(post_message_url)
            strRetMsg = ""
            if (status.ok):
                strDetails = status.content
                dictResult = json.loads(strDetails)
                if "results" in dictResult:
                    if "formatted_address" in dictResult["results"][0]:
                        strFormattedAddress =  dictResult["results"][0]["formatted_address"]
                strRetMsg=  "thats " +  strFormattedAddress

            strMessageType = "Text"
            strMessage = strRetMsg
            strVideoURL = ""
            strSubTitleInfo = ""
            strLink = ""
            dictButtons =[]
            payload = ""
            strLink = ""
            strQuickReplies = ""
            strDictButtons = json.dumps(dictButtons)
            strImage = ""

            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict(strMessageType,strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionGetLocationFromPin' + str(e))



    def action_showSkillStats(self, userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            intRandIntUserRole = randint(0,9)
            if intRandIntUserRole < 8 and userStateObj.UserRole=="Product_Manager":
                roleDemandInfoObj = RoleDemandInfo.objects.filter(Enabled="TRUE",Role="Product_Manager")
            else:
                roleDemandInfoObj = RoleDemandInfo.objects.exclude(Role="Product_Manager").filter(Enabled="TRUE")

            intNumberofRoles = roleDemandInfoObj.count()
            intRantInt = randint(0,intNumberofRoles-1)
            dictContent = roleDemandInfoObj[intRantInt]
            strSkilNameOld = "" #dictContent.Skill
            dictSkillName = strSkilNameOld.split(" ")
            strSkillName = ""

            for word in dictSkillName:
                strSkillName +=word[:1].upper() + word[1:] + " "

            strMessageType = "Text"
            strMessage = ""
            if dictContent != None:
                if int(dictContent.Percentage)>0:
                    strMessage = "" + strSkillName + " - was a expected by " + str(dictContent.Percentage) + "%  of companies  for " + str(dictContent.Role).replace("_"," ")
                else:
                    strMessage = "" + strSkillName + " - was a desired skill across roles "
            strVideoURL = ""
            strImage = ""
            strSubTitleInfo = ""
            strLink = ""
            strImage =   ""
            dictButtons =[]
            strLink = ""
            strQuickReplies = ""

            strDictButtons = "" #json.dumps(dictButtons)

            strQuickReplyPostback = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" #+ str(dictContent.SKILL_CODE)
            strQuickReplies += "text" + ":" + "Learn this skill" + ":" + strQuickReplyPostback

            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict(strMessageType,strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('action_showSkillStats ' + str(e))

    def actionTakenPeriodicAction(self, userID, recevied_message,strDictParams=""):
        try:
            retArr=[]
            dictParams={}
            userStateObj = UserState.objects.get(pk=userID)
            intMessageCount=0
            if self.r_stateServer.exists("KEY_UserState_" +str(userID)):
                intMessageCount = int(self.r_stateServer.hget("KEY_UserState_" +str(userID), 'MessageCount'))
                self.r_stateServer.hset("KEY_UserState_" +str(userID), 'MessageCount',intMessageCount+1 )
            else:
                self.r_stateServer.hset("KEY_UserState_" +str(userID), 'MessageCount',1 )
            strNotifyUser=userStateObj.Notify_Subscription

            if intMessageCount % 10 ==0:
                arrSkillStats = self.action_showSkillStats(userID, recevied_message,strDictParams)
                for arr in arrSkillStats:
                    retArr.append(arr)
            #elif intMessageCount % 9==0 and strNotifyUser=="FALSE":
            #    arrMesages = self.processEvent("SUBSCRIPTION_REMINDER",userID, '')
            #    post_message_url = self.configSettingsObj.facebookPostMessageURL%self.configSettingsObj.fbPageAccessTokenArise

            #    for response_msg_item in arrMesages:
            #        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg_item)
            return retArr
        except Exception,e:
            self.logger.error('actionTakenPeriodicAction ' + str(e))



    def actionGetReco(self, userID, recevied_message,strDictParams=""):
        try:
            #--------------Define Variables -------------------------------
            self.logger.info(strDictParams)
            retArr=[]
            dictParams={}
            intProgressUnits = 0
            intUnits = 0
            recevied_message = recevied_message.encode('utf-8')
            intMessageCount = 0
            skillCode = ""
            moduleID = None
            contentID=-1
            contentFeedback=""
            prevTags=""
            userContentOrder = -1
            arrAltMessage = []
            isFirst=False
            dictParamsModuleCompleted = None
            contentLibraryObj = None
            #--------------get Params -------------------------------
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "MODULE_ID" in dictParams:
                    moduleID = dictParams["MODULE_ID"]
                if "CONTENT_FEEDBACK" in dictParams:
                    contentFeedback = dictParams["CONTENT_FEEDBACK"]
                #if postback refers to a specfic content id , get that specific one else get the first one in the module
                if "CONTENT_ID" in dictParams:
                    contentID = dictParams["CONTENT_ID"]
                    objContentLibraryListA= ContentLibrary.objects.filter(ID= contentID)
                    if len(objContentLibraryListA)>0:
                        moduleID =  objContentLibraryListA[0].Module_ID
                    userContentOrder = int(objContentLibraryListA[0].Content_Order)
                    if userContentOrder==0:
                        userContentOrder = 1
                else:
                    objContentLibrary= ContentLibrary.objects.filter(Module_ID= moduleID).order_by("Content_Order").first()
                    moduleID = objContentLibrary.Module_ID
                    if objContentLibrary is not None:
                        contentID = objContentLibrary.ID
                        isFirst=True



            #--------------Define Variables -------------------------------
            if moduleID is not None:
                objUserModuleProgressList = UserModuleProgress.objects.filter(ModuleID=moduleID,UserID=userID)
                objModule = Module.objects.get(ID=moduleID)
                objContentLibraryList = ContentLibrary.objects.filter(Module_ID=moduleID)

                if len(objUserModuleProgressList)>0:
                    intProgressUnits = objUserModuleProgressList[0].CurrentPosition
                intUnits = objContentLibraryList.count()

                if contentID!=-1 :
                    # If it is the first item get it from content ID, if not, get content with module and content order
                    if isFirst == True:
                        contentLibraryObjList = ContentLibrary.objects.filter(ID=contentID)
                    else:
                        contentLibraryObjList = ContentLibrary.objects.filter(Module_ID=moduleID,Content_Order=userContentOrder)

                    if len(contentLibraryObjList)>0:
                        contentLibraryObj=contentLibraryObjList[0]
                # else:
                #     if len(objContentLibraryList)>0 :
                #
                #         arrProgress = []
                #         arrContentLibrary = []
                #
                #         for objUserModuleProgress in objUserModuleProgressList:
                #             arrProgress.append(objUserModuleProgress.Content_ID)
                #
                #         for objContentLibrary in objContentLibraryList:
                #             arrContentLibrary.append(objContentLibrary.ID)
                #
                #         arrUnusedContent = set(arrContentLibrary) - set(arrProgress)
                #
                #         intUnusedContent = len(arrUnusedContent)
                #
                #
                #         if intUnusedContent>1:
                #             intRantInt = randint(0,intUnusedContent-1)
                #             contentID = list(arrUnusedContent)[intRantInt]
                #             self.logger.info("here" + str(contentID))
                #             contentLibraryObj = ContentLibrary.objects.get(ID= contentID)
                #         else :
                #             intRantInt = randint(0,len(arrContentLibrary)-1)
                #             contentID = list(arrContentLibrary)[intRantInt]
                #             self.logger.info("here" + str(contentID))
                #             contentLibraryObj = ContentLibrary.objects.get(ID= contentID)
                #
                #         currentContentOrder = contentLibraryObj.Content_Order
                # self.logger.info("2.2")

                if intProgressUnits +1 >= intUnits:
                    blnLastMessage = True
                    objUserModuleProgressList = UserModuleProgress.objects.filter(ModuleID=moduleID).delete()
                    #dictParamsModuleCompleted =  self.actionGetModuleCompletionMessage(userID, recevied_message,moduleID)

                else:
                    blnLastMessage = False
                    blnIsLastMessage1 = self.updateUserModuleProgress(userID,moduleID,contentLibraryObj.ID)


                if contentLibraryObj is not None:
                    intContentID= contentLibraryObj.ID
                else:
                    intContentID = None

                #if it is the first question give some header information about the stash
                if isFirst ==True:
                    strMessageType = "Text"
                    strMessage = "This 🗃️ Stash has *" +str(intUnits) + "* questions"
                    strImage = ""
                    strSubTitleInfo = ""
                    strImage = ""
                    strVideoURL = ""
                    strLink = ""
                    strDictButtons = ""
                    strQuickReplies = ""
                    strNotificationType = "SILENT"

                    dictParamsMessageFirstQ = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,strNotificationType)
                    retArr.append(dictParamsMessageFirstQ)

                arrParamsConcept = self.getConceptMessage( userID,intContentID, blnLastMessage)
                for dictParamsConcept in arrParamsConcept:
                    retArr.append(dictParamsConcept)
                dictParamsChallenge = self.getChallengeMessage( userID,intContentID, intProgressUnits, intUnits, blnLastMessage)
                self.logger.info("3.1.4")
                if dictParamsChallenge is not None:
                    retArr.append(dictParamsChallenge)
                self.logger.info("3.1")
            else:

                strModuleTitle = objModule.Title
                strMessageType = "Text"
                strMessage = "*" +strModuleTitle + "* \r\n No Content Found"
                strImage = ""
                strSubTitleInfo = ""
                strImage = ""
                strVideoURL = ""
                strLink = ""
                strDictButtons = ""
                strQuickReplies = ""
                strNotificationType = "SILENT"
                self.logger.info("4")

                dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,strNotificationType)
                retArr.append(dictParams)
            self.logger.info("=====>>>>>"+str(retArr))
            return retArr
        except Exception,e:
            self.logger.error('actionGetReco ' + str(e))


    def getConceptMessage(self,userID,contentID, blnLastMessage):
        try:
            retArr=[]
            if contentID is not None:
                contentLibrary = ContentLibrary.objects.get(ID=contentID)

                if contentLibrary.Message_Type =="External_Content":
                    if contentLibrary.Type == "YouTube":
                        dictParamsConcept = self.getContentExternalYouTube( userID,contentLibrary)
                    elif contentLibrary.Type =="URL":
                        dictParamsConcept = self.getContentExternalURL( userID,contentLibrary)
                elif contentLibrary.Message_Type == "UGC":
                    if contentLibrary.Type == "Text":
                        dictParamsConcept = self.getContentUGCText( userID,contentLibrary)
                    elif contentLibrary.Type == "Video":

                        dictParamsConcept = self.getContentUGCVideo( userID,contentLibrary)
                    elif contentLibrary.Type == "Image":

                        dictParamsConcept = self.getContentUGCImage( userID,contentLibrary)

                # strQuickReplies=""
                # recoPayload =""
                # skillCode=""
                # challengeID=""
                #
                # if skillCode == "":
                #     recoPayload="SHOW_RECO"
                # else:
                #     recoPayload = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + skillCode
                # strMessage = "_"
                # strSubTitleInfo ="_"
                # dictParams1 = self.getRecoButtons(recoPayload,strMessage,strSubTitleInfo,str(contentID), str(challengeID),blnLastMessage)
                # strQuickReplies = dictParams1["QuickReplies"]
                # dictParamsConcept["QuickReplies"] = strQuickReplies
                retArr.append(dictParamsConcept)
            return retArr
        except Exception,e:
            self.logger.error('getConceptMessage ' + str(e))

    def getContentExternalYouTube(self, userID, contentLibrary):
        strMessageType = "Buttons"
        strMessage = ""
        strImage = ""
        strSubTitleInfo = ""
        strImage = ""
        strVideoURL = ""
        strLink = ""
        strDictButtons = ""
        strQuickReplies = ""
        strNotificationType = "SILENT"

        if contentLibrary.Title is not None:
            strMessage = contentLibrary.Title[:79]
        # if contentLibrary.Text is not None:
        #     strMessage = contentLibrary.Text[:79]
        # if contentLibrary.Skill is not None:
        #     strSubTitleInfoSkill = contentLibrary.Skill[:30].replace("_", " ")
        strSubTitleInfoSkill =""
        if contentLibrary.Subtitle is not None:
            strSubTitleInfo = "By : " + contentLibrary.Subtitle[:30] + " \r\nSkill : " + strSubTitleInfoSkill + "\r\nTime:< 4 min"
        if contentLibrary.LinkURL is not None:
            strLink = contentLibrary.LinkURL
        if contentLibrary.ImageURL != "":
            strImage =   contentLibrary.ImageURL
        dictButtons =[]
        strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCV/" + str(contentLibrary.ID) +"/" +str(userID)
        dictButtons.append(self.getButton("web_url","View",surl=strLink,spayload=""))
        strDictButtons = json.dumps(dictButtons)

        dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
        return dictParams

    def getContentExternalURL(self, userID, contentLibrary):
        strMessageType = "Buttons"
        strMessage = ""
        strImage = ""
        strSubTitleInfo = ""
        strImage = ""
        strVideoURL = ""
        strLink = ""
        strDictButtons = ""
        strQuickReplies = ""
        strNotificationType = "SILENT"
        if contentLibrary.Title is not None:
            strMessage = contentLibrary.Title[:79]
        if contentLibrary.Text is not None:
            strMessage = contentLibrary.Text[:79]
        # if contentLibrary.Skill is not None:
        #     strSubTitleInfoSkill = contentLibrary.Skill[:30].replace("_", " ")
        strSubTitleInfoSkill = ""
        if contentLibrary.Subtitle is not None:
            strSubTitleInfo = "By : " + contentLibrary.Subtitle[:30] + " \r\nSkill : " + strSubTitleInfoSkill + "\r\nTime:< 4 min"
        if contentLibrary.LinkURL is not None:
            strLink = contentLibrary.LinkURL
        if contentLibrary.ImageURL != "":
            strImage =   contentLibrary.ImageURL
        dictButtons =[]
        strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCV/" + str(contentLibrary.ID) +"/" +str(userID)
        dictButtons.append(self.getButton("web_url","View",surl=strLink,spayload=""))
        strDictButtons = json.dumps(dictButtons)


        dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,strNotificationType)
        return dictParams

    def getContentUGCText(self, userID, contentLibrary):
        strMessageType = "Text"
        strMessage = ""
        if str(contentLibrary.Text).encode('utf-8').strip() !="":
            strMessage += str(contentLibrary.Text).encode('utf-8').strip()
        else:
            strMessage = "*"
        # if contentLibrary is not None:
        #     strAttachmentText =  str(contentLibrary.Text).encode('utf-8').strip()
        # else:
        #     strAttachmentText =  "not found"
        if contentLibrary.Tags is not None:
            strMessage += str(contentLibrary.Tags).replace("#","")

        strImage = ""
        strSubTitleInfo = ""
        strImage = ""
        strVideoURL = ""
        strLink = ""
        strDictButtons = ""
        strQuickReplies = ""
        strNotificationType = "SILENT"


        dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,strNotificationType)
        return dictParams


    def getContentUGCVideo(self, userID, contentLibrary):
        strMessageType = "Video"
        strMessage = str(contentLibrary.LinkURL)
        strImage = ""
        strSubTitleInfo = ""
        strImage = ""
        strVideoURL = contentLibrary.LinkURL
        strLink = ""
        strDictButtons = ""
        strQuickReplies = ""
        strNotificationType = "SILENT"

        if contentLibrary.Text !="":
            strMessage = contentLibrary.Text
        else:
            strMessage ="_"

        dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,strNotificationType)
        return dictParams

    def getContentUGCImage(self, userID, contentLibrary):
        strMessageType = "Image"
        strImage = self.configSettingsObj.webUrl + "/static/curiousWorkbench/uimgs/" + contentLibrary.ImageURL
        strSubTitleInfo = ""

        strVideoURL = contentLibrary.LinkURL
        strLink = ""
        strDictButtons = ""
        strQuickReplies = ""
        strNotificationType = "SILENT"

        if contentLibrary.Text != None:
            if str(contentLibrary.Text) !="":
                strMessage = contentLibrary.Text
            else:
                strMessage ="_"
        else:
            strMessage = "_"

        dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,strNotificationType)
        self.logger.info("----->" + str(dictParams))
        return dictParams


    def getChallengeMessage(self, userID, contentID, intProgressUnits=0, intUnits=0, blnLastMessage=False):
        try:
            strMessageType = "Text"
            strMessage = ""
            strImage = ""
            strSubTitleInfo = ""
            strImage = ""
            strVideoURL = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""
            strNotificationType = "SILENT"
            strQuestion =""
            strQuestionOptions =""
            dictParams={}
            challengeObjAll = Challenge.objects.filter(Content_ID=contentID)
            #contentLibraryObj = ContentLibrary.objects.get(ID= contentID)
            if challengeObjAll is not None:

                for challengeObj in challengeObjAll:
                    if challengeObj is not None:
                        challengeID = challengeObj.id
                        strQuestionOptions = ''.encode('utf-8')
                        if challengeObj.Option_A is not None :
                            strQuickReplies = "text" + ":" + "A" + ":" + "CHECK_CHALLENGE_ANS-ANS|A-CHALLENGE_ID|" + str(challengeID)
                            strQuestionOptions += "`A`: " + str(challengeObj.Option_A) + "\r\n"
                        if challengeObj.Option_B is not None :
                            strQuickReplies += "," + "text" + ":" + "B" + ":" + "CHECK_CHALLENGE_ANS-ANS|B-CHALLENGE_ID|" + str(challengeID)
                            strQuestionOptions += "`B`: " + str(challengeObj.Option_B) + "\r\n"
                        if challengeObj.Option_C is not None :
                            strQuickReplies += "," + "text" + ":" + "C"+ ":" + "CHECK_CHALLENGE_ANS-ANS|C-CHALLENGE_ID|" + str(challengeID)
                            strQuestionOptions += "`C`: " + str(challengeObj.Option_C) + "\r\n"

                        if challengeObj.Option_D is not None :
                            strQuickReplies += "," + "text" + ":" + "D" + ":" + "CHECK_CHALLENGE_ANS-ANS|D-CHALLENGE_ID|" + str(challengeID)
                            strQuestionOptions += "`D`: " + str(challengeObj.Option_D) + "\r\n"

                        if challengeObj.Option_E is not None :
                            strQuickReplies += "," + "text" + ":" + "E" + ":" + "CHECK_CHALLENGE_ANS-ANS|E-CHALLENGE_ID|" + str(challengeID)
                            strQuestionOptions += "`E`: " + str(challengeObj.Option_E) + "\r\n"

                        strQuestion = ""
                        #strQuestion = "🤔  *" +challengeObj.Question_Text.encode('utf-8') + "*"
                        moduleObjList =  Module.objects.filter(ID= challengeObj.Module_ID)
                        if len(moduleObjList)>0:
                            strModuleTitle = moduleObjList[0].Title

                        strQuestion += "\r\n"
                        strQuestion += strQuestionOptions.encode('utf-8')
                        strQuestion += "\r\n Stash: " + strModuleTitle.encode('utf-8') + ", Question " + str(intProgressUnits)  + " of " + str(intUnits)

                        strMessage = strQuestion
                        if challengeObj.Tags is not None:
                            strMessage +="\r\n"
                            strMessage += str(challengeObj.Tags).encode('utf-8')
                    if strMessage=="":
                        strMessage ="Place Holder"
                    dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
                return dictParams
        except Exception,e:
            self.logger.error('getChallengeMessage ' + str(e))


    def actionGetChallenge(self, userID, recevied_message,strDictParams=""):
        try:
            retArr=[]
            dictParams={}

            intMessageCount = 0
            skillCode = ""
            challengeID=-1
            contentFeedback=""
            userCreatedChallengeID =  self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "SKILL_CODE" in dictParams:
                    skillCode = dictParams["SKILL_CODE"]

                # if "CONTENT_FEEDBACK" in dictParams:
                #     contentFeedback = dictParams["CONTENT_FEEDBACK"]
                if userCreatedChallengeID !="":
                    contentID = userCreatedChallengeID
                if "CHALLENGE_ID" in dictParams:
                    challengeID = dictParams["CHALLENGE_ID"]
            else:
                challengeID = userCreatedChallengeID



            if contentID !="":
                challengeObj = Challenge.objects.get(id=challengeID)
                contentLibraryObj =  ContentLibrary.objects.get(ID=challengeObj.Content_ID)

            else:
                challengeObjArr = Challenge.objects.all()
                intNumberOfKeys =  challengeObjArr.count()

                if intNumberOfKeys>1:
                    intRantInt = randint(0,intNumberOfKeys-1)
                else:
                    intRantInt = 0
                    challengeObj = challengeObjArr[intRantInt]

            strMessageType = "Text"
            strMessage = ""
            strImage = ""
            strVideoURL = ""
            strSubTitleInfo=""
            strLink=""
            strDictButtons=""

            if contentLibraryObj.Text is not None:
                strMessage = contentLibraryObj.Text
            if contentLibraryObj.Tags is not None:
                strMessage +="\r\n"
                strMessage += str(contentLibraryObj.Tags)

            if contentLibraryObj.LinkURL is not None:
                strVideoURL = self.configSettingsObj.webUrl + "/static/curiousWorkbench/uvids/" + contentLibraryObj.LinkURL
                dictParams = self.getMessageDict("Video", "_", strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, "","SILENT")
                retArr.append(dictParams)

            if contentLibraryObj.ImageURL is not None:
                strImage = self.configSettingsObj.webUrl + "/static/curiousWorkbench/uimgs/" + contentLibraryObj.ImageURL
                dictParams = self.getMessageDict("Image", "_", strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, "","SILENT")
                retArr.append(dictParams)



            strImage = ""


            dictButtons =[]

            recoPayload =""
            if skillCode == "":
                recoPayload="SHOW_RECO"
            else:
                recoPayload = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + skillCode

            strQuestion = challengeObj.Question_Text.encode('utf-8') + "\r\n"


            strQuickReplies=""
            strQuickReplies= strQuickReplies.encode('utf-8')
            if challengeObj.Option_A is not None :
                strQuickReplies = "text" + ":" + "A" + ":" + "CHECK_CHALLENGE_ANS-ANS|A-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "A: " + challengeObj.Option_A + "\r\n"
            if challengeObj.Option_B is not None:
                strQuickReplies += "," + "text" + ":" + "B" + ":" + "CHECK_CHALLENGE_ANS-ANS|B-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "B: " + challengeObj.Option_B + "\r\n"

            if challengeObj.Option_C is not None:
                strQuickReplies += "," + "text" + ":" + "C"+ ":" + "CHECK_CHALLENGE_ANS-ANS|C-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "C: " + challengeObj.Option_C + "\r\n"

            if challengeObj.Option_D is not None:
                strQuickReplies += "," + "text" + ":" + "D" + ":" + "CHECK_CHALLENGE_ANS-ANS|D-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "D: " + challengeObj.Option_D + "\r\n"

            if challengeObj.Option_E is not None:
                strQuickReplies += "," + "text" + ":" + "E" + ":" + "CHECK_CHALLENGE_ANS-ANS|E-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "E: " + challengeObj.Option_E + "\r\n"

            strQuestion = strQuestion
            if challengeObj.Tags is not None:
                strMessage +="\r\n"
                strMessage = strMessage
                strMessage += str(challengeObj.Tags)
            strSubTitleInfo=""
            strLink =""
            strDictButtons =""

            # if strMessage !="":
            #     dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
            #     retArr.append(dictParams)

            dictParams = self.getMessageDict(strMessageType, strQuestion, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
            retArr.append(dictParams)


            #retArr.append(dictParams1)
            #else:
            #    retArr.append(arrAltMessage[0])
            return retArr
        except Exception,e:
            self.logger.error('actionGetChallenge ' + str(e))

    def actionShareChallenge(self, userID, recevied_message,strDictParams=""):
        try:
            userCreatedChallengeID =  self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "CHALLENGE_ID" in dictParams:
                    userCreatedChallengeID = dictParams["CHALLENGE_ID"]

            strMessage1= "Copy and share the link below with your friends"

            strMessage2 = "Here is a challenge for you \r\n"
            strMessage2 += " https://m.me/TestArise?ref=" + str(userCreatedChallengeID)
            strMessageType = "Text"
            strVideoURL = ""
            strImage = ""
            strDictButtons =""
            strQuickReplies = ""
            strSubTitleInfo =""
            strLink = ""
            strDictButtons = ""
            retArr = []

            dictParams = self.getMessageDict(strMessageType, strMessage1, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons,strQuickReplies,"SILENT")
            retArr.append(dictParams)

            dictParams = self.getMessageDict(strMessageType, strMessage2, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons,strQuickReplies,"SILENT")
            retArr.append(dictParams)


            return retArr
        except Exception,e:
            self.logger.error('actionShareChallenge ' + str(e))

    def actionDeleteChallenge(self, userID, recevied_message,strDictParams=""):
        try:
            userCreatedChallengeID =  self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "CHALLENGE_ID" in dictParams:
                    userCreatedChallengeID = dictParams["CHALLENGE_ID"]

            objChallenge = Challenge.objects.get(id=userCreatedChallengeID)
            objChallenge.delete()

            strMessageType = "Text"
            strMessage = "Challenge removed"
            strVideoURL = ""
            strImage = ""
            strDictButtons =""
            strQuickReplies = "text"+ ":" + "Create Challenge" + ":" + "CREATE_CHALLENGE"
            strSubTitleInfo =""
            strLink = ""
            strDictButtons = ""
            retArr = []

            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons,strQuickReplies,"SILENT")
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionDeleteChallenge ' + str(e))

    def actionDeleteModule(self, userID, recevied_message,strDictParams=""):
        try:
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "MODULE_ID" in dictParams:
                    moduleID = dictParams["MODULE_ID"]

            ContentLibrary.objects.filter(Module_ID=moduleID).delete()
            Challenge.objects.filter(Module_ID=moduleID).delete()
            if Module.objects.filter(ID=moduleID).count()>0:
                strModuleTitle = Module.objects.filter(ID=moduleID)[0].Title
                Module.objects.filter(ID=moduleID).delete()
                strMessage = "Module *" + str(strModuleTitle) +  "* removed"
            else:
                strMessage = "Module was not found, may have been removed"

            strMessageType = "Text"
            strVideoURL = ""
            strImage = ""
            strDictButtons =""
            strQuickReplies = "text"+ ":" + "Create Challenge" + ":" + "CREATE_CHALLENGE"
            strSubTitleInfo =""
            strLink = ""
            strDictButtons = ""
            retArr = []

            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons,strQuickReplies,"SILENT")
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionDeleteModule ' + str(e))


    def actionShareModule(self, userID, recevied_message,strDictParams=""):
        try:
            arrTargetUsers=[]
            retArr=[]
            strModuleID = self.getFromUserStateFromDict(userID,"MODULE_ID")
            strUserName =self.getFromUserStateFromDict(userID,"USER_NAME")
            # if strDictParams.strip()!="":
            #     dictParams = json.loads(strDictParams)
            #     if "MODULE_ID" in dictParams:
            #         strModuleID = dictParams["MODULE_ID"]

            #strMessage= "*" + str(self.getFromUserStateFromDict(userID,"USER_NAME")) + " * wants to share this challenge with you \n"
            arrTargetUsers = self.getShareUserList(userID, recevied_message,strDictParams)


            objUserActions = UserActions()
            objUserActions.User_ID = userID
            objUserActions.Module_ID = strModuleID
            objUserActions.Action = "SHARE_MODULE"
            objUserActions.save()
            strMessageType = ""
            strMessage = strUserName + " would like to share this with you"
            strImage = ""
            strSubTitleInfo = ""
            strImage = ""
            strVideoURL = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""

            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons,strQuickReplies,"SILENT")
            retArr.append(dictParams)
            for userDMID in arrTargetUsers:
                dictParams = {}
                strDictParams =  json.dumps({"MODULE_ID":strModuleID,"CONTENT_ORDER":1})
                dictParams = self.actionStartModule(userID, "",strDictParams=strDictParams)
                for dictParam in dictParams:
                    if dictParam !={}:
                        dictParam["arrTargetUsers"] = [userDMID]
                        retArr.append(dictParam)




            return retArr
        except Exception,e:
            self.logger.error('actionShareModule ' + str(e))

    def getShareUserList(self, userID, recevied_message, strDictParams):
        try:
            isChannel = False
            arrTargetUsers=[]
            strShareUserID=""
            intStart = recevied_message.find('<')
            intEnd = recevied_message.find('>')
            strLink = ""
            strMessageTypeFromContent = ""
            if intStart > -1:
                strShareUserID = recevied_message[intStart + 2 : intEnd]


            arrTryChannels =  strShareUserID.split("|")
            if len(arrTryChannels)==2:
                isChannel = True
                strChannelID= arrTryChannels[0]
            else:
                isChannel = False



            strTeamID = UserState.objects.get(UserID= userID).Org_ID
            strBotAccessToken = PlatformCredentials.objects.get(SlackTeamID=strTeamID).SlackBotAccessToken


            if isChannel == False:
                strGetDMIDURL ="https://slack.com/api/im.list?token="+ strBotAccessToken  +"&pretty=1"
                responseDMIDs = requests.get(strGetDMIDURL)

                strDMIDsContent= responseDMIDs.content
                dictDMIDs = json.loads(strDMIDsContent)
                dmIDs = dictDMIDs["ims"]
                dmAuthUserID = ""
                for im in dmIDs:
                    if im["user"] == strShareUserID:
                        arrTargetUsers.append(im["id"])
            elif isChannel == True:
                # strGetChannelListURL ="https://slack.com/api/channels.list?token="+ strBotAccessToken  +"&pretty=1"
                # responseChannels = requests.get(strGetChannelListURL)
                #
                # strChannelsContent= responseChannels.content
                # dictChannels = json.loads(strChannelsContent)
                # arrChannels = dictChannels["channels"]
                # dmAuthUserID = ""
                # for channel in arrChannels:
                #     if channel["id"] == strChannelID:
                arrTargetUsers.append(strChannelID)
                # strMessage2 = "Here is a challenge for you \r\n"
                # strMessage2 += " https://m.me/TestArise?ref=" + str(userCreatedChallengeID)
            return arrTargetUsers
        except Exception,e:
            self.logger.error('getShareUserList ' + str(e))

    def actionTestChallenge(self, userID, recevied_message,strDictParams=""):
        try:
            retArr=[]
            dictParams={}
            contentLibraryObj = None

            intMessageCount = 0
            skillCode = ""
            challengeID=-1
            contentFeedback=""
            userCreatedChallengeID =  self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "SKILL_CODE" in dictParams:
                    skillCode = dictParams["SKILL_CODE"]

                # if "CONTENT_FEEDBACK" in dictParams:
                #     contentFeedback = dictParams["CONTENT_FEEDBACK"]
                if userCreatedChallengeID !="":
                    challengeID = userCreatedChallengeID
                if "CHALLENGE_ID" in dictParams:
                    challengeID = int(dictParams["CHALLENGE_ID"])

            else:
                challengeID = userCreatedChallengeID

            if challengeID !=-1:
                challengeObj = Challenge.objects.get(id=challengeID)
                if challengeObj.Content_ID is not None:
                    contentLibraryObj =  ContentLibrary.objects.get(ID=challengeObj.Content_ID)
            else:
                challengeObjArr = Challenge.objects.all()
                intNumberOfKeys =  challengeObjArr.count()
                if intNumberOfKeys>1:
                    intRantInt = randint(0,intNumberOfKeys-1)
                else:
                    intRantInt = 0
                    challengeObj = challengeObjArr[intRantInt]

            strMessageType = "Text"
            strMessage = ""
            strImage = ""
            strVideoURL = ""
            strSubTitleInfo=""
            strLink=""
            strDictButtons=""

            if contentLibraryObj is not None:
                if contentLibraryObj.Text is not None:
                    strMessage = contentLibraryObj.Text.encode('utf-8')


                if contentLibraryObj.Tags is not None:
                    strMessage +="\r\n"
                    strMessage += str(contentLibraryObj.Tags)


                if contentLibraryObj.LinkURL is not None:
                    strVideoURL = self.configSettingsObj.webUrl + "/static/curiousWorkbench/uvids/" + contentLibraryObj.LinkURL
                    dictParams = self.getMessageDict("Video", "_", strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, "","SILENT")
                    retArr.append(dictParams)

                if contentLibraryObj.ImageURL is not None:
                    strImage = self.configSettingsObj.webUrl + "/static/curiousWorkbench/uimgs/" + contentLibraryObj.ImageURL
                    dictParams = self.getMessageDict("Image", "_", strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, "","SILENT")
                    retArr.append(dictParams)

            dictButtons =[]

            recoPayload =""
            if skillCode == "":
                recoPayload="SHOW_RECO"
            else:
                recoPayload = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + skillCode

            strQuestion = "".encode('utf-8')
            txtContentText = "".encode('utf-8')
            txtModuleTitle = "".encode('utf-8')
            if challengeObj.Module_ID is not None:
                objModule = Module.objects.get(ID= challengeObj.Module_ID)
                txtModuleTitle = objModule.Title
            if challengeObj.Content_ID is not None:
                objContent = ContentLibrary.objects.get(ID= challengeObj.Content_ID)
                txtContentText = objContent.Text

            if txtModuleTitle is not None:
                if len(txtModuleTitle)>0 :
                    strQuestion += "*" +txtModuleTitle.encode('utf-8') + "*" + "\r\n"
                    # if txtContentText is not None:
            #     strQuestion += txtContentText.encode('utf-8') + "\r\n"

            strQuestion += "❓" + challengeObj.Question_Text.encode('utf-8') + "\r\n"




            if challengeObj.Option_A is not None:
                # strQuickReplies = "text" + ":" + "A" + ":" + "CHECK_CHALLENGE_ANS-ANS|A-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "A: " + challengeObj.Option_A.encode('utf-8') + "\r\n"
            if challengeObj.Option_B is not None:
                # strQuickReplies += "," + "text" + ":" + "B" + ":" + "CHECK_CHALLENGE_ANS-ANS|B-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "B: " + challengeObj.Option_B.encode('utf-8') + "\r\n"

            if challengeObj.Option_C is not None:
                # strQuickReplies += "," + "text" + ":" + "C"+ ":" + "CHECK_CHALLENGE_ANS-ANS|C-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "C: " + challengeObj.Option_C.encode('utf-8') + "\r\n"

            if challengeObj.Option_D is not None:
                # strQuickReplies += "," + "text" + ":" + "D" + ":" + "CHECK_CHALLENGE_ANS-ANS|D-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "D: " + challengeObj.Option_D.encode('utf-8') + "\r\n"

            if challengeObj.Option_E is not None:
                # strQuickReplies += "," + "text" + ":" + "E" + ":" + "CHECK_CHALLENGE_ANS-ANS|E-CHALLENGE_ID|" + str(challengeID)
                strQuestion += "E: " + challengeObj.Option_E.encode('utf-8') + "\r\n"


            strQuickReplies = "text" + ":" + "Share this concept!" + ":" + "SHARE_CHALLENGE-CHALLENGE_ID|" + str(challengeID)
            strQuickReplies += "," + "text" + ":" + "Add another question" + ":" + "ASK_CHALLENGE_QUESTION"
            strQuickReplies += "," + "text" + ":" + "Nah! just delete it" + ":" + "DELETE_CHALLENGE-CHALLENGE_ID|" + str(challengeID)


            if challengeObj.Tags is not None:
                strMessage = strMessage.encode('utf-8')
                strMessage +="\r\n"
                strMessage += str(challengeObj.Tags).encode('utf-8')
            strSubTitleInfo=""
            strLink =""
            strDictButtons =""
            if strMessage !="":
                dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, "","SILENT")
                retArr.append(dictParams)
            dictParams = self.getMessageDict(strMessageType, strQuestion, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
            retArr.append(dictParams)

            return retArr
        except Exception,e:
            self.logger.error('actionTestChallenge ' + str(e))

    def actionTestModule(self, userID, recevied_message,strDictParams=""):
        try:
            retArr=[]
            dictParams={}
            isLastMessage =False
            intMessageCount = 0
            skillCode = ""
            challengeID=-1
            contentFeedback=""
            userCreatedModuleID =  self.getFromUserStateFromDict(userID,"EDITING_MODULE")
            userContentOrder =  self.getFromUserStateFromDict(userID,"CURRENT_CONTENT_ORDER")

            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "SKILL_CODE" in dictParams:
                    skillCode = dictParams["SKILL_CODE"]

                # if "CONTENT_FEEDBACK" in dictParams:
                #     contentFeedback = dictParams["CONTENT_FEEDBACK"]
                if userCreatedModuleID !="":
                    moduleID = userCreatedModuleID
                if "MODULE_ID" in dictParams:
                    moduleID = int(dictParams["MODULE_ID"])
                if "CONTENT_ORDER" in dictParams:
                    userContentOrder = int(dictParams["CONTENT_ORDER"])

            else:
                moduleID = userCreatedModuleID
            if moduleID !=-1:
                if userContentOrder == "":
                    userContentOrder = 1
                else:
                    userContentOrder = userContentOrder + 1
                objModule = Module.objects.get(ID =moduleID )
                strModuleTitle = objModule.Title
                intTotalUnits = ContentLibrary.objects.filter(Module_ID=moduleID).count()
                contentLibraryObj =  ContentLibrary.objects.get(Module_ID=moduleID, Content_Order=userContentOrder)

                challengeObj = Challenge.objects.filter(Content_ID = contentLibraryObj.ID)
                if len(challengeObj) >0:
                    dictParams["CHALLENGE_ID"] = challengeObj[0].id
                    strDictParams1 =  json.dumps(dictParams)
                    retArr =  self.getChallengeMessage(userID, "", strDictParams1)
                else:
                    retArr =  self.getConceptMessage(userID, contentLibraryObj.ID,False)

            return retArr
        except Exception,e:
            self.logger.error('actionTestModule ' + str(e))

    def getRecoButtons(self, recoPayload,strMessage1,strSubTitleInfo1,strContentID,strChallengeID="", isLastMessage=False):
        strMessageType ="Text"
        strMessage = strMessage1 + "\r\n"+strSubTitleInfo1
        strImage = ""
        strSubTitleInfo = ""
        strImage = ""
        strVideoURL = ""
        strLink = ""
        strDictButtons = ""
        strQuickReplies = ""
        strContentID = str(strContentID)
        if isLastMessage == False:
            strQuickReplyPostbackLike = recoPayload + "-" + "CONTENT_FEEDBACK" + "|" + "Like >>" + "-" + "CONTENT_ID" + "|" + strContentID
            strQuickReplyPostbackDisLike = recoPayload + "-" + "CONTENT_FEEDBACK" + "|" + "DisLike" + "-" + "CONTENT_ID" + "|" + strContentID
            strDownImage="1483408247_dislike.png"
            strUpImage="1483408228_like.png"
            strQuickReplies = "" #"text" + ":" + "dislike" + ":" + strQuickReplyPostbackDisLike  + ":" +strDownImage + ","

        if strChallengeID !="":
            strQuickReplies += "text" + ":" + "Share 🗃️" + ":" + "SHARE_CHALLENGE-CHALLENGE_ID|" + str(strChallengeID) + ","

        if isLastMessage == True:
            strQuickReplies += "text" + ":" + "More Stashes🗃️" + ":" + "SHOW_SKILLS" + ","

        if isLastMessage == False:
            strQuickReplies += "text" + ":" + "Next >>" + ":" + strQuickReplyPostbackLike + ":" + strUpImage
        dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
        return dictParams

    # def actionGetRecoNotify(self, userID, recevied_message,strDictParams=""):
    #     try:
    #         retArr=[]
    #         dictParams={}
    #         recevied_message = recevied_message.encode('utf-8')
    #         intMessageCount = 0
    #         skillCode = ""
    #         if strDictParams.strip()!="":
    #             dictParams = json.loads(strDictParams)
    #             if "SKILL_CODE" in dictParams:
    #                 skillCode = dictParams["SKILL_CODE"]
    #
    #
    #         contentLibraryObj = ContentLibrary.objects.filter(Skill=skillCode, Message_Type="External_Content",Rating__gte=3)
    #         intNumberOfKeys =  contentLibraryObj.count()
    #         if intNumberOfKeys == 0 :
    #             contentLibraryObj = ContentLibrary.objects.filter(Message_Type="External_Content",Rating__gte=3)
    #             intNumberOfKeys =  contentLibraryObj.count()
    #         if intNumberOfKeys>1:
    #             intRantInt = randint(0,intNumberOfKeys-1)
    #         else:
    #             intRantInt = 0
    #
    #         contentLibrary = contentLibraryObj[intRantInt]
    #
    #
    #         strMessageType = "Buttons"
    #         strMessage = contentLibrary.Title[:79]
    #         strVideoURL = ""
    #         strImage = ""
    #         strSubTitleInfoSkill = "" #contentLibrary.Skill[:30]
    #         strSubTitleInfo = "by : " + contentLibrary.Subtitle[:30] + ", Skill : " + strSubTitleInfoSkill #+ "    " + "Claim: 1pt"
    #
    #         strLink = contentLibrary.LinkURL
    #         if contentLibrary.ImageURL != "":
    #             strImage =   contentLibrary.ImageURL
    #         dictButtons =[]
    #         strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCV/" + str(contentLibrary.ID) +"/" +str(userID)
    #         dictButtons.append(self.getButton("web_url","read now",surl=strLink,spayload=""))
    #         dictShareLinks = self.getShareLinks(strMessage,strLink)
    #         if str(contentLibrary.Questions.strip()) != "":
    #             payload = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + str(contentLibrary.ID)
    #
    #             dictButtons.append(self.getButton("postback","claim 1 pt",surl="",spayload=payload))
    #         recoPayload =""
    #         if skillCode == "":
    #             recoPayload="SHOW_RECO"
    #         else:
    #             recoPayload = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + skillCode
    #
    #         dictButtons.append(self.getButton("postback","pick another skill",surl="",spayload="SHOW_SKILL_STAT"))
    #         dictButtons.append(self.getButton("postback","next >>",surl="",spayload=recoPayload))
    #
    #         strDictButtons = json.dumps(dictButtons)
    #         strQuickReplies = ""
    #
    #         strMessageNotify = "Today's Skill Alert : " + strSubTitleInfoSkill.replace("_"," ") + ", "
    #         dictParams = self.getMessageDict("Text", strMessageNotify + " " + strMessage , "", "", strImage, strVideoURL, strLink, "", "","SILENT")
    #         retArr.append(dictParams)
    #
    #         dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
    #         retArr.append(dictParams)
    #
    #
    #
    #         return retArr
    #     except Exception,e:
    #         self.logger.error('actionGetRecoNotify ' + str(e))


    def getMessageDict(self,strMessageType = "", strMessage = "", strImage = "", strSubTitleInfo = "", strImage1 = "", strVideoURL = "", strLink = "", strDictButtons = "", strQuickReplies = "",strNotificationType="SILENT",strListContent="",strListButtons="", strAttachmentText="", arrTargetUsers = []):
        dictRet={}
        dictRet["MessageType"] = strMessageType
        dictRet["Message"] = strMessage
        dictRet["ImageURL"] = strImage
        dictRet["SubTitleInfo"] = strSubTitleInfo
        dictRet["ImageURL1"] = strImage1
        dictRet["VideoURL"] = strVideoURL
        dictRet["Link"] = strLink
        dictRet["DictButtons"] = strDictButtons
        dictRet["QuickReplies"] = strQuickReplies
        dictRet["NotificationType"] = strNotificationType
        dictRet["ListContent"] = strListContent
        dictRet["ListButtons"] = strListButtons
        dictRet["strAttachmentText"]= strAttachmentText
        dictRet["arrTargetUsers"] = arrTargetUsers
        return dictRet


    def actionAskShareModule(self, userID, recevied_message,strDictParams=""):
        try:
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "MODULE_ID" in dictParams:
                    moduleID = dictParams["MODULE_ID"]
                else:
                    moduleID = 1
            else:

                moduleID = 1
            self.updateUserStateDict(userID,"MODULE_ID", moduleID)

            moduleObj = Module.objects.get(ID=moduleID)
            if moduleObj != None:
                strMessage = "Who would you like to share *"
                strMessage += str(moduleObj.Title) + "* with, just say share with @tom" #+ " (in " + moduleObj.SKILL_CODE.replace("_"," ")[:29] + " )"
                strVideoURL = ""
                strImage = ""
                strSubTitleInfo = "" #"by: "+ str(moduleObj.Author) + "         " + str(moduleObj.UnitsPerDay) + " mins"
                strDictButtons = ""
                strQuickReplies = ""
                strLink = ""
                retArr=[]
                dictParams={}
                dictParams = self.getMessageDict("",strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                retArr.append(dictParams)
                return retArr
        except Exception,e:
            self.logger.error('actionGetModule' + str(e))

    def actionGetModule(self, userID, recevied_message,strDictParams=""):
        try:
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "ID" in dictParams:
                    moduleID = dictParams["ID"]
                else:
                    moduleID = 1
            else:
                moduleID = 1
            #dictParams={"ID":1}
            #strModule= self.r_server.hget( "KEY_MODULE_"+str(moduleID), "ID")
            #dictModule = json.loads(strModule)
            moduleObj = Module.objects.get(ID=moduleID)
            if moduleObj != None:
                strMessage = str(moduleObj.Title)[:39] #+ " (in " + moduleObj.SKILL_CODE.replace("_"," ")[:29] + " )"
                strMessage += "\r\n" + str(moduleObj.Description)
                strMessage += "\r\n" + "Author :" + str(moduleObj.Author) + " Units:" + str(moduleObj.Units)
                strVideoURL = ""
                strImage = str(moduleObj.AuthorURL)
                strSubTitleInfo = "" #"by: "+ str(moduleObj.Author) + "         " + str(moduleObj.UnitsPerDay) + " mins"
                dictButtons =[]
                strLink =""
                payload = "START_MODULE" + "-" + "MODULE_ID" + "|" + str(moduleID)
                dictButtons.append(self.getButton("postback","Pick up this skill",surl="",spayload=payload))
                strDictButtons = json.dumps(dictButtons)
                strQuickReplies = ""
                retArr=[]
                dictParams={}
                dictParams = self.getMessageDict("",strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                retArr.append(dictParams)
                return retArr
        except Exception,e:
            self.logger.error('actionGetModule' + str(e))

    def actionStartModule(self, userID, recevied_message,strDictParams=""):
        try:

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
                if "MODULE_ID" in dictParams:
                    moduleID=dictParams["MODULE_ID"]
                if "CONTENT_ORDER" in dictParams:
                    contentOrder =dictParams["CONTENT_ORDER"]
                else:
                    contentOrder = 0
            #strModule= self.r_server.hget( "KEY_MODULE_"+str(moduleID), "ID")
            #dictModule = json.loads(strModule)
            #objModule = Module.objects.get()
            # Update Current Module ID in under state
            # userStateObj = UserState.objects.get(pk=userID)
            # userStateObj.Current_Module_ID = moduleID #dictModule["ID"]
            # userStateObj.save()
            # Get first message of content
            #contentObj =  ContentLibrary.objects.filter(Module_ID=dictModule["ID"]).order_by('Content_Order').first()
            #if contentObj !=None:
            #    intCurrentPosition = contentObj.Content_Order
            # Update Current Module ID in under state
            intCurrentPosition =1
            userModuleProgressObjList = UserModuleProgress.objects.filter(UserID=userID, ModuleID=moduleID)
            if len(userModuleProgressObjList)==0 :
                userModuleProgressObj =  UserModuleProgress()
                userModuleProgressObj.UserID = userID
                userModuleProgressObj.ModuleID = moduleID
                userModuleProgressObj.CurrentPosition =intCurrentPosition
                userModuleProgressObj.save()
            else:
                userModuleProgressObj =  userModuleProgressObjList[0]
                userModuleProgressObj.CurrentPosition = intCurrentPosition
                userModuleProgressObj.save()

            objUserActions = UserActions()
            objUserActions.User_ID = userID
            objUserActions.Module_ID = moduleID
            objUserActions.Action = "START_MODULE"
            objUserActions.save()




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
            dictReturnParams = {"MODULE_ID":moduleID,"CONTENT_ORDER":contentOrder+1}
            strDictReturnParams = json.dumps(dictReturnParams)
            retArr = self.actionNextModuleContent(userID, recevied_message,strDictReturnParams)
            #strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies = self.actionNextModuleContent(userID, recevied_message,strDictReturnParams)
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
            #retArr=[]
            #dictParams={}
            #dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
            #retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionStartModule' + str(e))


    def actionNextModuleContent(self, userID, recevied_message,strDictParams=""):
        try:
            intContentOrder = 0
            challengeObj =  None
            if strDictParams!="":
                dictParams = json.loads(strDictParams)
            moduleID = dictParams["MODULE_ID"]

            if "CONTENT_ORDER" in dictParams:
                intContentOrder = dictParams["CONTENT_ORDER"]
            else:
                intContentOrder =0
            # Get first message of content
            objUserActions = UserActions()
            objUserActions.User_ID = userID
            objUserActions.Module_ID = moduleID
            objUserActions.Content_Order = intContentOrder
            objUserActions.Action = "NEXT_MODULE_CONTENT"
            objUserActions.save()
            intContentCount =ContentLibrary.objects.filter(Module_ID=moduleID).count()
            contentObjList =  ContentLibrary.objects.filter(Module_ID=int(moduleID),Content_Order=intContentOrder)
            if len(contentObjList) > 0:
                contentObjList =  ContentLibrary.objects.filter(Module_ID=moduleID)
                contentObj = contentObjList[0]

                challengeObj = Challenge.objects.filter(Content_ID = contentObj.ID)
                if len(challengeObj) >0:
                    dictParams["CHALLENGE_ID"] = challengeObj[0].id
                    strDictParams1 =  json.dumps(dictParams)
                    retArr =  self.getChallengeMessage(userID, "", strDictParams1)
                else:
                    retArr =  self.getConceptMessage(userID, contentObj.ID,False)

            return retArr
        except Exception,e:
            self.logger.error('actionNextModuleContent' + str(e))

    def getShareLinks(self,title, contentURL):
        #---------LinkedIn --------------------
        strLinkedInShareURL = "https://www.linkedin.com/shareArticle?mini=true&"
        dictLinkedInURLParams ={}
        dictLinkedInURLParams["url"] = contentURL
        dictLinkedInURLParams["title"] = title.encode('ascii', 'ignore')
        dictLinkedInURLParams["summary"] = "I just acquired this short skill.".encode('ascii', 'ignore')
        dictLinkedInURLParams["source="] = "Walnut Ai - Learn skills bot".encode('ascii', 'ignore')
        strLinkedInURLParams = urllib.urlencode(dictLinkedInURLParams)
        strLinkedInShareURL = strLinkedInShareURL + strLinkedInURLParams
        #---------Facebook --------------------
        #strFBShareURL = "https://www.facebook.com/sharer/sharer.php?"
        #dictFBURLParams ={}
        #dictFBURLParams["u"] = contentURL
        #strFBURLParams = urllib.urlencode(dictFBURLParams)
        #strFBShareURL = strLinkedInShareURL + strFBURLParams

        dictLShareLinks = {}
        dictLShareLinks["LinkedIn"] =strLinkedInShareURL
        #dictLShareLinks["Facebook"] =strFBShareURL

        return dictLShareLinks



    def actionGetModuleCompletionMessage(self, userID, recevied_message, moduleID):
        try:
            strMessage = ""
            strSubTitleInfo = ""
            strImage = ""
            strImage = ""
            strVideoURL  = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""
            strMessageType = "Buttons"


            objModule = Module.objects.get(ID=moduleID)
            objUserCertification = UserCertification.objects.filter(Module_ID=moduleID, userID=userID).first()
            if objUserCertification is None:
                objUserCertification = UserCertification()
                objUserCertification.userID = userID
                objUserCertification.Module_ID =  int(moduleID)
                objUserCertification.date = datetime.now()
                objUserCertification.Title = objModule.Title
                objUserCertification.Author = objModule.Author
                objUserCertification.AuthorURL = objModule.AuthorURL
                #objUserCertification.SKILL_CODE = objModule.SKILL_CODE
                objUserCertification.save()


            arrCongratulate =[]
            arrCongratulate.append("Yay!, We are done! ")
            arrCongratulate.append("Yippie! You completed this module ! ")
            arrCongratulate.append("Fantastic!, You finished this module ")
            arrCongratulate.append("Super!, We did it! ")
            arrCongratulate.append("Awesome!, Done with this module! ")

            strMessage = strMessage.encode('utf-8')
            strMessage= random.choice(arrCongratulate)

            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/myProfile/" + str(userID)
            strMessage += "\n This has been added to your personal profile"
            strMessage += "\n Check out your profile here " + strLink

            strImage = self.configSettingsObj.webUrl +"/static/curiousWorkbench/images/CertificateImageLarge.png"
            strMessageType = "Image"
            strSubTitleInfo = "This Stash has been added to your skill board. See your Skill board Here \n ➡️➡️"
            strSubTitleInfo += (self.configSettingsObj.webUrl + "/myProfile/" + userID).encode('utf-8')


            strQuickReplies = ""
            strQuickReplies += "text" + ":" + "Share" + ":" + "SHARE_CHALLENGE-MODULE_ID|" + str(moduleID) + ","

            strQuickReplies += "text" + ":" + "Explore" + ":" + "SHOW_SKILLS"




            dictButtons =[]
            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCertV/" + str(userID)

            # strLinkedInShareURL = "https://www.linkedin.com/shareArticle?mini=true&"
            # dictLinkedInURLParams ={}
            # dictLinkedInURLParams["url"] = self.configSettingsObj.webUrl
            # dictLinkedInURLParams["title"] = objModule.Title
            # dictLinkedInURLParams["summary"] = "I just acquired this short skill."
            # dictLinkedInURLParams["source="] = "Walnut Ai - Learn skills bot"
            # strLinkedInURLParams = urllib.urlencode(dictLinkedInURLParams)
            #strLinkedInShareURL = strLinkedInShareURL + strLinkedInURLParams

            # dictButtons.append(self.getButton("web_url","See my skill board",surl=strLink,spayload=""))
            # dictButtons.append(self.getButton("web_url","Share on LinkedIn",surl=strLinkedInShareURL,spayload=""))
            # dictButtons.append(self.getButton("postback","Learn more Topics",surl=strLinkedInShareURL,spayload="SHOW_SKILLS"))
            # strDictButtons= json.dumps(dictButtons)
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
            return dictParams
        except Exception,e:
            self.logger.error('actionGetModuleCompletionMessage' + str(e))

    def actionGetSearch(self, userID, recevied_message,strDictParams=""):
        try:
            return self.actionListModules(userID, "SEARCH", recevied_message,strDictParams)

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
            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCV/" + str(dictContent["ID"])
            dictButtons.append(self.getButton("web_url","read more",surl=strLink,spayload=""))
            if dictContent["Questions"] != "":
                payload = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + dictContent["ID"]
                dictButtons.append(self.getButton("postback","challenge 1 pt",surl="",spayload=payload))
            dictButtons.append(self.getButton("postback","next article",surl="",spayload="SHOW_RECO"))
            strDictButtons = json.dumps(dictButtons)
            strQuickReplies = ""

            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
            retArr.append(dictParams)
            return retArr

        except Exception,e:
            self.logger.error('actionGetSingleReco' + str(e))


    def actionAskQuestion(self, userID, recevied_message,strDictParams=""):
        try:
            retArr=[]
            dictParams={}

            if strDictParams !="":

                dictParams = json.loads(strDictParams)

                strContentID = dictParams["CONTENT_ID"]
                strContent= self.r_server.hget( "KEY_CONTENT_"+strContentID, "Msg")

                dictContent = json.loads(strContent)
                strMessage = dictContent["Questions"][:79]

                strAnswerOptions = dictContent["AnswerOptions"]


                dictAnswerOptions = strAnswerOptions.split("|")
                strVideoURL = ""
                strImage = ""
                #strSubTitleInfo = dictContent["Subtitle"]
                strSubTitleInfo =""
                strLink = ""
                strImage = self.configSettingsObj.webUrl +"/static/curiousWorkbench/images/sunAskQuestion.jpg"
                strImage  =""
                dictButtons =[]
                #quickReplies.append({"content_type":contentType,"title":title,"payload":payload})
                #dictMessage["message"]["quick_replies"] = quickReplies
                quickReplies = []
                for answerOption in dictAnswerOptions:
                    arrAnswerOption = answerOption.split(":")
                    if len(arrAnswerOption)==2:
                        payload = "ANSWER_TO_QUESTION" + "-" + "ContentID" + "|" + str(dictContent["ID"]) + "-" + "AnswerID" + "|" + str(arrAnswerOption[0])
                        strAnswerOptionText = arrAnswerOption[1][:19]
                        dictButtons.append(self.getButton("postback",strAnswerOptionText,surl="",spayload=payload))
                        quickReplies.append({"content_type":contentType,"title":strAnswerOptionText,"payload":payload})

                strQuickReplies = str(quickReplies)

                strDictButtons = json.dumps(dictButtons)
                strDictButtons = ""
                dictParams = self.getMessageDict("Text", strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                retArr.append(dictParams)
                return retArr

            else:
                strImage=""
                strVideoURL=""
                strLink=""
                strDictButtons=""
                strQuickReplies=""

                dictParams = self.getMessageDict("", "no content", strImage, "no content", strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                retArr.append(dictParams)
                return retArr

        except Exception,e:
            self.logger.error('actionAskQuestion' + str(e))




    def actionReviewAnswer(self, userID, recevied_message,strDictParams=""):
        try:
            dictParams={}
            retArr=[]
            if strDictParams !="":
                dictParams = json.loads(strDictParams)
                strContentID = dictParams["CONTENT_ID"]
                strAnswerID = dictParams["ANSWER_ID"]
                strContent= self.r_server.hget( "KEY_CONTENT_"+strContentID, "Msg")
                dictContent = json.loads(strContent)
                strCorrectAnswerID = dictContent["RightAnswer"]
                strQuickReplies = ""
                userModuleProgressObj = UserModuleProgress.objects.filter(ModuleID=dictContent["MODULE_ID"], UserID=userID).first()
                intCurrentPosition = userModuleProgressObj.CurrentPosition
                if strAnswerID == strCorrectAnswerID :
                    strMessage = "Thats Correct :-), you claimed 1 pt"
                    userSkillStatusObj = self.updateUserSkillStatus(userID,dictContent["Skill"],1)
                    strQuickReplyPostback = "NEXT_MODULE_CONTENT" + "-" +"MODULE_ID" + "|" +str(dictContent["MODULE_ID"])+ "-"+ "CONTENT_ORDER" + "|" + str(intCurrentPosition+1)
                    strQuickReplies += "text" + ":" + "ok" + ":" +strQuickReplyPostback

                if strAnswerID != strCorrectAnswerID:
                    strMessage = "Oops! :-( thats incorrect , try again"

                strVideoURL = ""
                strImage = ""
                strSubTitleInfo = ""
                strLink = ""
                strImage = ""
                strDictButtons =""
                dictParams = self.getMessageDict("Text", strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                retArr.append(dictParams)
                return retArr
                return
            else:
                strImage=""
                strVideoURL=""
                strLink=""
                strDictButtons=""
                strQuickReplies=""

                dictParams = self.getMessageDict("","no content", strImage, "no content", strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                retArr.append(dictParams)
                return retArr
                return
        except Exception,e:
            self.logger.error('actionReviewAnswer' + str(e))


    def actionListModules(self, userID, listType, recevied_message,strDictParams=""):
        try:
            if listType=="":
                listType="STANDARD"
            strMessage = ""
            strSubTitleInfo = ""
            strImage = ""
            strImage = ""
            strVideoURL  = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""

            strMessageType = "List"
            strMessage="Here we go click on view progress."
            strImage = self.configSettingsObj.webUrl +"/static/curiousWorkbench/images/CertificateImageLarge.png"
            strSubTitleInfo = "Check It Out"
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCertV/" + str(userID)
            dictButtons.append(self.getButton("web_url","View Progress",surl=strLink,spayload=""))

            strDictButtons= json.dumps(dictButtons)
            retArr=[]
            dictParams={}
            strMessage = "1"
            recevied_message =""
            strListContent , strListButtons = self.getModuleList(userID,listType, recevied_message,strDictParams,False)
            strMessage=strMessage[:400]

            if strListContent !="":
                dictParams = self.getMessageDict(strMessageType,  strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT",strListContent,strListButtons)
            else:
                strMessageType = "Text"
                strDictButtons = ""
                strQuickReplies =""
                strMessage = "Could not find anything for *" + recevied_message + "*, try another Stash like *Presentation Skills*"

                dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT",strListContent,strListButtons)
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionListModules' + str(e))




    def actionGetUserProgress(self, userID, recevied_message,strDictParams=""):
        try:
            strMessage = ""
            strSubTitleInfo = ""
            strImage = ""
            strImage = ""
            strVideoURL  = ""
            strLink = ""
            strDictButtons = ""
            strQuickReplies = ""

            strRandomKey = str(randint(0,9000))
            strSql_1= "select DATE(CreatedDate) AS 'createdDateVal', count(id) as 'units' from curiousWorkbench_usercertification where UserID ='" + userID + "' group by createdDateVal;"
            results_1 = list(self.query_to_dicts(strSql_1))
            chartFileName_1 = "profile_chart_1_" + "-" + str(userID) + strRandomKey + ".png"
            chartPath_1 = self.configSettingsObj.absFileLocation + "/images/plots/" + chartFileName_1
            custom_style= Style(legend_font_size=20, value_font_size=20,title_font_size=40, colors=('#29b992','#f77b71'))
            bar_chart = pygal.Bar(title=u'Modules I Acquired', print_values=True,print_values_position='top',  print_labels=False,show_y_labels=False, legend_at_bottom=True,include_x_axis=False,include_y_axis=False,show_y_guides=False,margin=50,style=custom_style)
            for result_1 in results_1:
                bar_chart.add(str(result_1["createdDateVal"]),[result_1["units"]], rounded_bars=2 * 10)

            bar_chart.render_to_png(filename=chartPath_1)
            chartURL_1 = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/plots/" + chartFileName_1

            strMessageType = "Image"
            strMessage="Here we go click on view progress."


            strImage = chartURL_1
            strSubTitleInfo = "Check It Out"
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/myProfile/" + str(userID)
            #dictButtons.append(self.getButton("web_url","View Progress",surl=strLink,spayload=""))


            # strQuickReplyPostback = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" #+ str(dictContent.SKILL_CODE)
            # strQuickReplies += "text" + ":" + "Learn this skill" + ":" + strQuickReplyPostback

            strMessage += "\n *Check out your profile, click here* \n"
            strMessage += strLink
            strDictButtons= json.dumps(dictButtons)
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"SILENT")
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionGetUserProgress' + str(e))



    def actionSaveContentTitle(self, userID, recevied_message,strDictParams=""):
        try:
            strType = "UGC"
            contentLibraryObj =  ContentLibrary.objects.create(
            Title=recevied_message.encode('ascii','replace'),
            Subtitle="na",
            ImageURL="na",
            LinkURL="na",
            Embed_ID="na",
            Skill = "UGC",
            Questions ="na",
            RightAnswer = "na",
            Content_Order = 0,
            Type=strType)

            #contentLibraryObj.refresh_from_db()
            strContentID = contentLibraryObj.ID

            #self.getFromUserStateFromDict(userID, "EDITING_MODULE")
            self.updateUserStateDict(userID, "UGC_ID", strContentID )
            #self.updateUserStateDict(userID, "UGC_ID", strContentID )
            return
        except Exception,e:
            self.logger.error('actionSaveContentTitle' + str(e))

    def actionSaveContentVideo(self, userID, recevied_message,strDictParams=""):
        try:
            if strDictParams!="":
                dictParams = json.loads(strDictParams)
                if 'Headers' in dictParams:
                    strHeader = dictParams['HEADERS']
                if 'VideoURL' in dictParams:
                    VideoURL =  dictParams['VIDEO_URL']

                    contentID = self.getFromUserStateFromDict(userID,"EDITING_CONTENT")
                    contentLibraryObj = get_object_or_404(ContentLibrary, ID= contentID)
                    contentLibraryObj.LinkURL = str(contentID) + ".mp4" #VideoURL
                    contentLibraryObj.save()

                    videoPath = self.configSettingsObj.absFileLocation + "/uvids/" + str(contentID) + ".mp4"

                    if strHeader !="":
                        arrVal= strHeader.split("|")
                        dictHeaders ={}
                        dictHeaders[arrVal[0]]=arrVal[1]
                        strHeaderVal = json.dumps(dictHeaders)
                        fileResp = requests.get(VideoURL, headers=strHeaderVal)
                    else:
                        fileResp = requests.get(VideoURL)

                    fileObj = open(videoPath,'wb')
                    f.write(fileResp.read())
                    f.close()
                    #urllib.urlretrieve(VideoURL, videoPath)
            return
        except Exception,e:
            self.logger.error('actionSaveContentVideo' + str(e))




    def actionSaveContentImage(self, userID, recevied_message,strDictParams=""):
        try:
            moduleID = self.getFromUserStateFromDict(userID,"MODULE_ID")

            intContentOrder = 0
            intContentOrder = ContentLibrary.objects.filter(Module_ID = moduleID).count() + 1
            self.updateUserStateDict(userID,"CONTENT_ORDER",int(intContentOrder))

            ImageURL=""
            strHeader=""
            if strDictParams!="":
                dictParams = json.loads(strDictParams)
                if 'ImageURL' in dictParams:
                    ImageURL =  dictParams['ImageURL']
                if 'Headers' in dictParams:
                    strHeader = dictParams['Headers']

                    disassembled = urlparse(ImageURL)
                    filename, file_ext = splitext(basename(disassembled.path))

                    imagePath = self.configSettingsObj.absFileLocation + "/uimgs/" + str(filename + file_ext)
                    self.logger.info("printing image url" + str(ImageURL))
                    if strHeader !="":

                        arrVal= strHeader.split("|")

                        dictHeaders ={}
                        dictHeaders[arrVal[0]]=arrVal[1]

                        strHeaderVal = json.dumps(dictHeaders)


                        self.logger.info("image url and headers" + str(ImageURL) + str(dictHeaders))
                        fileResp = requests.get(ImageURL, headers=dictHeaders)
                    else:
                        fileResp = requests.get(ImageURL)
                    self.logger.info(str(ImageURL))
                    if fileResp is not None:
                        fileObj = open(imagePath,'wb')
                        fileObj.write(fileResp.content)
                        fileObj.close()

                    #urllib.urlretrieve(ImageURL, imagePath)

                    contentID =-1
                    #contentID = self.getFromUserStateFromDict(userID,"EDITING_CONTENT")
                    self.logger.info("--->" + str(contentID))
                    if contentID !=-1:
                        contentLibraryObj = get_object_or_404(ContentLibrary, ID= contentID)
                        contentLibraryObj.ImageURL = str(filename + file_ext)
                        contentLibraryObj.Text =recevied_message
                        contentLibraryObj.Type = "Image"
                        contentLibraryObj.Message_Type = "UGC"
                        contentLibraryObj.save()
                    else:
                        contentLibraryObj = ContentLibrary()
                        contentLibraryObj.userID = userID
                        contentLibraryObj.Module_ID = moduleID
                        contentLibraryObj.Content_Order = intContentOrder
                        contentLibraryObj.Text =recevied_message
                        contentLibraryObj.Type = "Image"
                        contentLibraryObj.Message_Type = "UGC"
                        contentLibraryObj.ImageURL = str(filename + file_ext)
                        contentLibraryObj.save()
                    self.logger.info(str(contentLibraryObj.ID))

                    selectedChallenge = Challenge()
                    selectedChallenge.Content_ID = contentLibraryObj.ID
                    selectedChallenge.Module_ID=int(moduleID)
                    selectedChallenge.Correct_Answer = "A"
                    selectedChallenge.UserID = userID
                    selectedChallenge.save()

                self.updateUserStateDict(userID,"EDITING_CHALLENGE",int(selectedChallenge.id))
                self.updateUserStateDict(userID,"CONTENT_ID",int(contentLibraryObj.ID))

            return
        except Exception,e:
            self.logger.error('actionSaveContentImage' + str(e))


    def actionSaveContentSkill(self, userID, recevied_message,strDictParams=""):
        try:

            contentID = self.getFromUserStateFromDict(userID, "UGC_ID")
            contentLibraryObj = get_object_or_404(ContentLibrary, ID= contentID)
            #contentLibraryObj.Skill = recevied_message
            contentLibraryObj.save()

            return
        except Exception,e:
            self.logger.error('actionSaveContentSkill' + str(e))

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
            userStateObj = get_object_or_404(UserState, UserID=userID)

            if recevied_message == "Product Manager":
                strRole = "Product_Manager"
            else :
                strRole = recevied_message.strip().replace(" ","_")

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
            self.actionSetUserRole(userID, "Product_Manager")
        except Exception,e:
            self.logger.error('actionSaveUserLocationProdM' + str(e))

    def actionSaveConfirmSubscription(self, userID, recevied_message,strDictParams=""):
        try:
            strNotifyTime="MOR"
            userStateObj = get_object_or_404(UserState, UserID=userID)
            userStateObj.Notify_Subscription = "TRUE"
            if strDictParams !="":
                dictParams= json.loads(strDictParams)
                if "NOTE_TIME" in dictParams:
                    strNotifyTime = dictParams["NOTE_TIME"]
            userStateObj.Notify_Time = strNotifyTime
            userStateObj.save()
        except Exception,e:
            self.logger.error('actionSaveConfirmSubscription' + str(e))

    def actionSaveConfirmUnSubscription(self, userID, recevied_message,strDictParams=""):
        try:
            userStateObj = get_object_or_404(UserState, UserID=userID)
            userStateObj.Notify_Subscription = "FALSE"
            userStateObj.save()
        except Exception,e:
            self.logger.error('actionSaveConfirmSubscription' + str(e))



    def actionSaveUserLocationProgM(self, userID, recevied_message,strDictParams=""):
        try:
            self.actionSetUserRole(userID, "Program_Manager")
        except Exception,e:
            self.logger.error('actionSaveUserLocationProgM' + str(e))

    def actionSaveUserLocationEggM(self, userID, recevied_message,strDictParams=""):
        try:
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

            strRoleInfoDesc = ""
            moduleID = ""
            roleInfo = self.r_server.hgetall("KEY_ROLE_" + strUserRole)
            strMessage = "Here are the top 3 skills by demand\r\n"
            intMax = 4
            intCount = 0
            strQuickReplies = ""
            strRoleInfoDesc = ""
            strPayLoad = ""
            strQuickReplies =""
            for role in roleInfo:
                if intCount <= intMax:
                    dictRoleInfo = json.loads(roleInfo[role])
                    if dictRoleInfo["Enabled"]=="TRUE":
                        moduleObj = Module.objects.filter(SKILL_CODE=dictRoleInfo["SKILL_CODE"]).first()
                        if moduleObj is not None:
                            if moduleObj.count()>0:
                                strRoleInfoDesc += dictRoleInfo["Skill"] + " [Code : " + str(moduleObj.ID) + "]"+ "\r\n"
                            if intCount != 0:
                                strQuickReplies += ","

                        if moduleObj != None:
                            moduleID = moduleObj.ID
                            strPayLoad = "SHOW_MODULE" + "-" + "ID" + "|" + str(moduleID)
                            strQuickReplies += "text" + ":" + str(moduleID) + ":" + strPayLoad
                        intCount +=1
            strRoleInfoDesc += "I will keep looking for more. \r\n Select a code below to acquire a skill "
            strMessage += strRoleInfoDesc

            strSubTitleInfo = ""
            strImage=""
            strMessage =  strMessage[:295]
            #strMessage = self.getSkillList(userID,"","")
            strDictButtons = ""
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict("",strMessage, strImage, strSubTitleInfo, strImage, "",self.configSettingsObj.webUrl, strDictButtons,strQuickReplies,"SILENT")
            retArr.append(dictParams)
            return retArr
            return
        except Exception,e:
            self.logger.error('actionGetRoleDemandInfo' + str(e))


    def actionCheckChallengeAns(self, userID, recevied_message,strDictParams=""):
        try:
            strMessage=""
            arrCongratulate=[]
            arrConsole=[]
            isLastMessage = False
            strSubTitleInfo = ""
            strImage=""
            strMessage =  strMessage[:295]
            strQuickReplies = ""
            strDictButtons = ""
            retArr=[]
            dictParams={}
            skillCode = ""
            arrCongratulate.append("Yay!  🎉🎉🎉, Thats right! ")
            arrCongratulate.append("Yippie!  🥂, Good Job ! ")
            arrCongratulate.append("Fantastic!  👏,, you got it! ")
            arrCongratulate.append("Super!  💃, Thats right! ")
            arrCongratulate.append("Awesome!  🕺, right again! ")
            arrConsole.append("Nope! Thats ok, we are learning 😌! ")
            arrConsole.append("Nay! But we will learn right? ")
            arrConsole.append("Hmm! nope 😢!, lets learn the concept ")
            arrConsole.append("Lets see....  😩 not right! ")
            arrConsole.append("Wrong, but keep going 💪! ")

            self.logger.info("1")
            #------------------Get Variables ----------------------------------
            userStateObj = UserState.objects.get(pk=userID)
            strUserRole =  userStateObj.UserRole
            if strDictParams !="":
                dictParams = json.loads(strDictParams)
                if "CHALLENGE_ID" in dictParams:
                    challengeID = int(dictParams["CHALLENGE_ID"])
                if "ANS" in dictParams:
                    strAns = str(dictParams["ANS"])
            objChallenge = Challenge.objects.get(id=challengeID)
            moduleID =  objChallenge.Module_ID
            contentID =  objChallenge.Content_ID

            self.LogUserAction(userID,"ANSWER_CHALLENGE",None,None,challengeID)

            self.logger.info("2")
            #---------------------Update Challenge Result Summary---------------------------------------------

            try:
                objChallengeResultSummary = ChallengeResultSummary.objects.get(Challenge_ID= challengeID)
            except ObjectDoesNotExist:
                objChallengeResultSummary = ChallengeResultSummary()
                objChallengeResultSummary.Challenge_ID = challengeID
                objChallengeResultSummary.Option_A_Count = 0
                objChallengeResultSummary.Option_B_Count = 0
                objChallengeResultSummary.Option_C_Count = 0
                objChallengeResultSummary.Option_D_Count = 0
                objChallengeResultSummary.Option_E_Count = 0

            self.logger.info("3")
            if strAns =="A":
                objChallengeResultSummary.Option_A_Count +=1
            elif strAns == "B":
                objChallengeResultSummary.Option_B_Count +=1
            elif strAns == "C":
                objChallengeResultSummary.Option_C_Count +=1
            elif strAns == "D":
                objChallengeResultSummary.Option_D_Count +=1
            elif strAns == "E":
                objChallengeResultSummary.Option_E_Count +=1

            objChallengeResultSummary.save()
            self.logger.info("4")
            #------------------------Update User Module Progress------------------------------------------------------------------------------
            isLastMessage = self.updateUserModuleProgress(userID,moduleID, contentID)
            if isLastMessage == True:
                dictParamsModuleCompleted =  self.actionGetModuleCompletionMessage(userID, recevied_message,moduleID)
            #-----------------------User Challenge Result User-------------------------------------------------------------------------------
            try:
                objChallengeResultUser = ChallengeResultUser.objects.get(Challenge_ID= challengeID, UserID = str(userID))
            except ObjectDoesNotExist:
                objChallengeResultUser = ChallengeResultUser()
                objChallengeResultUser.Challenge_ID = challengeID
                objChallengeResultUser.UserID = userID

            if objChallenge.Correct_Answer == "A":
                strCorrectAnswerText = "A: " + objChallenge.Option_A
            elif objChallenge.Correct_Answer == "B":
                strCorrectAnswerText = "B: " + objChallenge.Option_B
            elif objChallenge.Correct_Answer == "C":
                strCorrectAnswerText = "C: " + objChallenge.Option_C
            elif objChallenge.Correct_Answer == "D":
                strCorrectAnswerText = "D: " + objChallenge.Option_D
            elif objChallenge.Correct_Answer == "E":
                strCorrectAnswerText = "E: " + objChallenge.Option_E
            self.logger.info("5")
            strMessage =''.encode('utf-8')
            objChallengeResultUser.Ans = strAns
            if strAns == objChallenge.Correct_Answer:
                objChallengeResultUser.IsCorrect == "Y"
                strMessage = random.choice(arrCongratulate)
            else:
                objChallengeResultUser.IsCorrect == "N"
                strMessage = random.choice(arrConsole)
                strMessage += "The right answer would be : *" + str(strCorrectAnswerText) +  "* [you picked " + strAns + " ]" + "\r\n" + "\r\n"
            arrSummary=[]

            objChallengeResultUser.save()

            #--------------- Get the Chart ----------------------------------------

            intRightAnsCount =0
            intTotalAnsCount =0
            intTotalAnsCount = int(objChallengeResultSummary.Option_A_Count + objChallengeResultSummary.Option_B_Count + objChallengeResultSummary.Option_C_Count + objChallengeResultSummary.Option_D_Count + objChallengeResultSummary.Option_E_Count)
            self.logger.info("6")
            if objChallenge.Correct_Answer== "A":
                intRightAnsCount = objChallengeResultSummary.Option_A_Count
            if objChallenge.Correct_Answer== "B":
                intRightAnsCount = objChallengeResultSummary.Option_B_Count
            if objChallenge.Correct_Answer== "C":
                intRightAnsCount = objChallengeResultSummary.Option_C_Count
            if objChallenge.Correct_Answer== "D":
                intRightAnsCount = objChallengeResultSummary.Option_D_Count
            if objChallenge.Correct_Answer== "E":
                intRightAnsCount = objChallengeResultSummary.Option_E_Count


            chartURL = self.getCheckChallengeAnsChartURL(userID,challengeID,intRightAnsCount,intTotalAnsCount)
            dictParams = self.getMessageDict("Image",strMessage, chartURL, "", chartURL, "",self.configSettingsObj.webUrl, "","","SILENT")
            dictParams["QUICK_REPLIES"] = strQuickReplies
            #retArr.append(dictParams)
            #self.logger.info(str(retArr))
            self.logger.info("7")
            #-----------------------------Get Reco Buttons ----------------
            strMessage = "_"
            strSubTitleInfo ="_"

            contentID= objChallenge.Content_ID
            selectedContentLibraryObj =  ContentLibrary.objects.get(ID=contentID)
            intUnits =  ContentLibrary.objects.filter(Module_ID=objChallenge.Module_ID).count()
            intNextContentOder = 0
            blnLastMessage = False
            self.logger.info("7.0")
            self.logger.info(str(intUnits))
            self.logger.info(str(selectedContentLibraryObj.Content_Order))
            if selectedContentLibraryObj.Content_Order >= intUnits:
                blnLastMessage =True
                self.logger.info("7.0.1")
            else:
                self.logger.info("7.0.2")
                blnLastMessage = False
                intNextContentOder = int(selectedContentLibraryObj.Content_Order)+1
                self.logger.info(str(intNextContentOder))
                objNextContent = ContentLibrary.objects.get(Module_ID=objChallenge.Module_ID,Content_Order=intNextContentOder)
                nextContentID=objNextContent.ID

                recoPayload="SHOW_RECO"+"-CONTENT_ID" + "|" + str(nextContentID)
                self.logger.info("7.1")
                dictParams1 = self.getRecoButtons(recoPayload,strMessage,strSubTitleInfo,nextContentID)
                self.logger.info("7.2")
                #self.logger.info(str(dictParams1))
                strQuickReplies = dictParams1["QuickReplies"]
                dictParams["QuickReplies"] = strQuickReplies
            retArr.append(dictParams)
            self.logger.info("8")
            #--------------------------------------------------------------------

            if blnLastMessage == True:
                retArr.append(dictParamsModuleCompleted)
            return retArr
            self.logger.info("9")

        except Exception,e:
            self.logger.error('actionCheckChallengeAns' + str(e))

    def LogUserAction(self,userID, ActionType, moduleID, contentID, challengeID ):
        objUserActions = UserActions()
        objUserActions.User_ID = userID
        objUserActions.Module_ID = moduleID
        objUserActions.Challenge_ID = challengeID
        objUserActions.Action = "ANSWER_CHALLENGE"
        objUserActions.save()

    def getCheckChallengeAnsChartURL(self, userID, challengeID,intRightAnsCount,intTotalAnsCount):
        intPercentageRight =0
        intPercentageWrong =0

        if intTotalAnsCount>0:
            intPercentageRight = int((float(intRightAnsCount)/intTotalAnsCount)*100)
            intPercentageWrong = 100-intPercentageRight


        strRandomKey = str(randint(0,9000))
        chartPath = self.configSettingsObj.absFileLocation + "/images/plots/" + str(challengeID) + "-" + str(userID) + strRandomKey + ".png"
        chartFileName = str(challengeID) + "-" + str(userID) + strRandomKey  + ".png"

        custom_style= Style(legend_font_size=20, value_font_size=20,title_font_size=40)

        bar_chart = pygal.Bar(title=u'See how others did', print_values=True,print_values_position='top',  print_labels=False,show_y_labels=False, legend_at_bottom=True,include_x_axis=False,include_y_axis=False,show_y_guides=False,margin=50,style=custom_style,)

        bar_chart.add('Got it Right',[intPercentageRight], rounded_bars=2 * 10)
        bar_chart.add('Got it Wrong',[intPercentageWrong], rounded_bars=2 * 10)
        bar_chart.render_to_png(filename=chartPath)
        chartURL = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/plots/" + chartFileName
        self.logger.info(str(intRightAnsCount)+ " _ " + str(intTotalAnsCount))
        return chartURL

    def updateUserModuleProgress(self, userID, ModuleID, ContentID):
        moduleID = ModuleID
        isLastMessage = False
        intUnits = ContentLibrary.objects.filter(Module_ID=moduleID).count()
        intContentOrder = ContentLibrary.objects.get(ID=ContentID).Content_Order
        arrProgress = []
        arrContentLibrary = []
        intProgressUnits = 0
        objUserModuleProgressList = UserModuleProgress.objects.filter(ModuleID=moduleID, UserID = str(userID))

        if len(objUserModuleProgressList)>0:
            objUserModuleProgress = objUserModuleProgressList[0]
            intProgressUnits = objUserModuleProgress.CurrentPosition

            objUserModuleProgress.CurrentPosition = intContentOrder
            objUserModuleProgress.LastUpdatedDate = datetime.now()
            objUserModuleProgress.save()

        else:
            intProgressUnits = 1
            objUserModuleProgress = UserModuleProgress()
            objUserModuleProgress.Content_ID = ContentID
            objUserModuleProgress.ModuleID = ModuleID
            objUserModuleProgress.UserID = userID
            objUserModuleProgress.CurrentPosition = 1
            objUserModuleProgress.save()


        if intContentOrder == intUnits:
            isLastMessage = True
        else:
            isLastMessage = False

        return isLastMessage


    def getModuleList(self,userID,listType, recevied_message,strDictParams="",UserSkillOnlyFlag=False,Type="LIST"):
        try:
            if listType=="":
                listType="STANDARD"
            intListItems=0
            intStartPos = 0
            blnModuleCompleted = False
            isLastPage = False
            isSearch = False
            if strDictParams !="":
                dictParams = json.loads(strDictParams)
                if "START_POSITION" in dictParams:
                    intStartPos = int(dictParams["START_POSITION"])

            userStateObj = UserState.objects.get(pk=userID)
            if listType =="SEARCH":
                moduleObj = Module.objects.filter( Title__icontains=recevied_message)
            else:
                moduleObj = Module.objects.all()


            intNumberofModules = moduleObj.count()

            strMessage = "more options >>"
            strMessageType = "Text"
            arrSkillList =[]
            dictSkillList={}
            intStartIndex = intStartPos
            intMax= intStartIndex + 10
            if intMax <= intNumberofModules:
                isLastPage = True
            else:
                isLastPage = False
            intCount=0
            if UserSkillOnlyFlag==False:
                dictSkillList["Title"] = "Topics"
                dictSkillList["SubTitle"] = "Select a topic to learn about it \r\n"
                dictSkillList["Image"] = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/bannerWithLogo.jpg"
            elif UserSkillOnlyFlag == True:
                dictSkillList["Title"] = "Skills you acquired"
                dictSkillList["SubTitle"] = ""
                dictSkillList["Image"] = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/bannerWithLogoProgress.jpg"

            dictButton ={}
            arrSkillList.append(dictSkillList)

            #----------------------------------------------------

            for moduleInstance in moduleObj:
                dictSkillList={}

                arrCertList = UserCertification.objects.filter(userID=userID, Module_ID=moduleInstance.ID)
                intChallengeCount = Challenge.objects.filter(Module_ID=int(moduleInstance.ID)).count()
                if intChallengeCount>0:
                    if len(arrCertList)>0:
                        blnModuleCompleted = True
                        strModuleCompleted = " 🏆 Completed"
                    else:
                        blnModuleCompleted = False
                        strModuleCompleted = ""

                    if intCount>=intStartIndex and intCount<=intMax:
                        dictSkillList["Title"]=""
                        dictContent = moduleInstance
                        strSkilNameOld = dictContent.Title
                        dictSkillName = strSkilNameOld.split(" ")
                        strSkillName = ""
                        skillProgressCredits =0
                        try:
                            #skillProgressObj = Progress.objects.get(userID=userID,SKILL_CODE=dictContent.Skill.strip().replace(" ","_"))
                            skillProgressObj = Progress.objects.get(userID=userID,SKILL_CODE="")
                            skillProgressCredits = skillProgressObj.Credits

                        except Progress.DoesNotExist:
                            skillProgressCredits=0



                        for word in dictSkillName:
                            strSkillName +=word[:1].upper() + word[1:] + " "
                        # if dictContent.Live == True:
                        dictSkillList["Title"] = strSkillName
                        dictSkillList["SubTitle"] =dictContent.Description.encode('utf-8') #"Demand 🔥 :" + str(dictContent.Percentage) + "%  My Credits 🏆 : " + str(skillProgressCredits)
                        dictSkillList["SubTitle"] += "\r\n by :" + moduleInstance.Author.encode('utf-8') +  " 💡 Concepts : " + str(intChallengeCount) +  strModuleCompleted
                        # else:
                        #     dictSkillList["Title"] += "" + strSkillName
                        #     dictSkillList["SubTitle"] = dictContent.Description.encode('utf-8') + strModuleCompleted #"🔥 Common Skill My Credits 🏆 :" +  str(intContentCount)

                        dictButtons = []
                        dictButton ={}
                        #dictbuttons.append(self.getButton(arrButtons["ButtonType"],arrButtons["ButtonTitle"], surl=arrButtons["ButtonLinkURL"], spayload=arrButtons["ButtonPostback"]))
                        dictButton["ButtonType"] = "postback"
                        dictButton["ButtonTitle"] = "Get it"
                        dictButton["ButtonLinkURL"] = ""
                        dictButton["ButtonPostback"] = "SHOW_RECO" + "-" + "MODULE_ID" + "|" + str(moduleInstance.ID)
                        dictButtons.append(dictButton)


                        dictButton ={}
                        #dictbuttons.append(self.getButton(arrButtons["ButtonType"],arrButtons["ButtonTitle"], surl=arrButtons["ButtonLinkURL"], spayload=arrButtons["ButtonPostback"]))
                        dictButton["ButtonType"] = "postback"
                        dictButton["ButtonTitle"] = "Share"
                        dictButton["ButtonLinkURL"] = ""
                        dictButton["ButtonPostback"] = "SHARE_CHALLENGE" + "-" + "MODULE_ID" + "|" + str(moduleInstance.ID)
                        self.updateUserStateDict(userID,"MODULE_ID",moduleInstance.ID)
                        dictButtons.append(dictButton)


                        if userID == moduleInstance.UserID:

                            dictButton ={}
                            #dictbuttons.append(self.getButton(arrButtons["ButtonType"],arrButtons["ButtonTitle"], surl=arrButtons["ButtonLinkURL"], spayload=arrButtons["ButtonPostback"]))
                            dictButton["ButtonType"] = "postback"
                            dictButton["ButtonTitle"] = "delete"
                            dictButton["ButtonLinkURL"] = ""
                            dictButton["ButtonPostback"] = "DELETE_MODULE" + "-" + "MODULE_ID" + "|" + str(moduleInstance.ID)
                            dictButtons.append(dictButton)


                        # if dictContent.UserID == userID :
                        #     dictButton ={}
                        #     #dictbuttons.append(self.getButton(arrButtons["ButtonType"],arrButtons["ButtonTitle"], surl=arrButtons["ButtonLinkURL"], spayload=arrButtons["ButtonPostback"]))
                        #     dictButton["ButtonType"] = "postback"
                        #     dictButton["ButtonTitle"] = "Manage"
                        #     dictButton["ButtonLinkURL"] = ""
                        #     dictButton["ButtonPostback"] = "MANAGE_MODULE" + "-" + "MODULE_ID" + "|" + str(moduleInstance.ID)
                        #     self.updateUserStateDict(userID,"MODULE_ID",moduleInstance.ID)
                        #     dictButtons.append(dictButton)

                        dictSkillList["Buttons"] = dictButtons



                        if UserSkillOnlyFlag == True and skillProgressCredits >0:
                            arrSkillList.append(dictSkillList)
                            intListItems+=1
                        elif UserSkillOnlyFlag ==False:
                            arrSkillList.append(dictSkillList)
                            intListItems+=1
                        intCount+=1
            dictButton ={}
            arrListFooterButtons =[]


            if isLastPage ==False:
                if UserSkillOnlyFlag == True:
                    dictButton["ButtonType"] = "postback"
                    dictButton["ButtonTitle"] = "View more"
                    dictButton["ButtonPostback"] = "CHECK_PROGRESS"+ "-" + "START_POSITION" + "|" + str(intStartPos + 3)
                    dictButton["ButtonLinkURL"] = ""
                elif UserSkillOnlyFlag == False:
                    dictButton["ButtonType"] = "postback"
                    dictButton["ButtonTitle"] = "View more"
                    dictButton["ButtonLinkURL"] = ""
                    dictButton["ButtonPostback"] = "SHOW_SKILLS"+ "-" + "START_POSITION" + "|" + str(intStartPos + 3)

                arrListFooterButtons.append(dictButton)
            #dictSkillList["Buttons"] = dictButton


            if isSearch == True:

                dictButton ={}
                dictButton["ButtonType"] = "postback"
                dictButton["ButtonTitle"] = "Search again"
                dictButton["ButtonPostback"] = "TAG_SEARCH"
                dictButton["ButtonLinkURL"] = ""
                arrListFooterButtons.append(dictButton)


            dictButton ={}
            dictButton["ButtonType"] = "postback"
            dictButton["ButtonTitle"] = "Create your own"
            dictButton["ButtonPostback"] = "CREATE_CHALLENGE"
            dictButton["ButtonLinkURL"] = ""
            arrListFooterButtons.append(dictButton)


            dictButton ={}
            dictButton["ButtonType"] = "postback"
            dictButton["ButtonTitle"] = "My Profile"
            dictButton["ButtonPostback"] = "CHECK_PROGRESS"
            dictButton["ButtonLinkURL"] = ""
            arrListFooterButtons.append(dictButton)

            strListButtons =  json.dumps(arrListFooterButtons)

            #---------------------------------------------
            if intListItems >0:
                strSkillList= json.dumps(arrSkillList)
            else:
                strSkillList =""
            return strSkillList, strListButtons
        except Exception,e:
            self.logger.error('getSkillList' + str(e))


    def actionShowModules(self, userID, recevied_message,strDictParams=""):
        try:
            moduleObj =  Module.objects.all()
            # userStateObj = UserState.objects.get(pk=userID)
            # strUserRole =  userStateObj.UserRole
            # mo
            # roleInfo = self.r_server.hgetall("KEY_ROLE_" + strUserRole)
            # strMessage = "Here are the top 3 skills by demand\r\n"
            intMax = 4
            intCount = 0
            strQuickReplies = ""
            # strRoleInfoDesc = ""
            strMessage = "Check out these modules \r\n"
            for module in moduleObj:
                if intCount <= intMax:
                    if intCount != 0:
                        strQuickReplies += ","
                    if module != None:
                        moduleID = module.ID
                        strPayLoad = "SHOW_MODULE" + "-" + "ID" + "|" + str(moduleID)
                        strMessage += str(module.Title) + ":" + str(moduleID) + "\r\n"
                        strQuickReplies += "text" + ":" + str(moduleID) + ":" + strPayLoad
                intCount +=1
            # strRoleInfoDesc += "I will keep looking for more. \r\n Select a code below to acquire a skill "
            strSubTitleInfo = ""
            strImage=""
            strMessage =  strMessage[:295]
            strDictButtons = ""
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict("",strMessage, strImage, strSubTitleInfo, strImage, "",self.configSettingsObj.webUrl , strDictButtons,strQuickReplies,"SILENT")
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionGetRoleDemandInfo' + str(e))



    def actionCompleteModule(self, userID, recevied_message,strDictParams=""):
        try:

            if strDictParams !="":
                dictParams = json.loads(strDictParams)
                if "MODULE_ID" in dictParams:
                    intModuleID = int(dictParams["MODULE_ID"])






            moduleObj =  Module.objects.all()
            # userStateObj = UserState.objects.get(pk=userID)
            # strUserRole =  userStateObj.UserRole
            # mo
            # roleInfo = self.r_server.hgetall("KEY_ROLE_" + strUserRole)
            # strMessage = "Here are the top 3 skills by demand\r\n"
            intMax = 4
            intCount = 0
            strQuickReplies = ""
            # strRoleInfoDesc = ""
            strMessage = "Check out these modules \r\n"
            for module in moduleObj:
                if intCount <= intMax:
                    if intCount != 0:
                        strQuickReplies += ","
                    if module != None:
                        moduleID = module.ID
                        strPayLoad = "SHOW_MODULE" + "-" + "ID" + "|" + str(moduleID)
                        strMessage += str(module.Title) + ":" + str(moduleID) + "\r\n"
                        strQuickReplies += "text" + ":" + str(moduleID) + ":" + strPayLoad
                intCount +=1
            # strRoleInfoDesc += "I will keep looking for more. \r\n Select a code below to acquire a skill "
            strSubTitleInfo = ""
            strImage=""
            strMessage =  strMessage[:295]
            strDictButtons = ""
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict("",strMessage, strImage, strSubTitleInfo, strImage, "",self.configSettingsObj.webUrl , strDictButtons,strQuickReplies,"SILENT")
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionGetRoleDemandInfo' + str(e))

    def actionSaveContent(self,userID, recevied_message,strDictParams=""):
        try:

            strModuleID = self.getFromUserStateFromDict(userID, "EDITING_MODULE")
            strContentOrder = self.getFromUserStateFromDict(userID, "CONTENT_ORDER")
            if strContentOrder == "":
                strContentOrder = 0
            intCurrentContentOrder = int(strContentOrder) + 1
            selectedContentLibrary = ContentLibrary()
            selectedContentLibrary.Module_ID = strModuleID
            selectedContentLibrary.Content_Order = intCurrentContentOrder
            selectedContentLibrary.Message_Type = "UGC"
            selectedContentLibrary.Text = recevied_message.encode('ascii','replace')
            selectedContentLibrary.Title = "na"
            selectedContentLibrary.Subtitle = "na"
            selectedContentLibrary.ImageURL =  "na"
            selectedContentLibrary.LinkURL = "na"
            selectedContentLibrary.Embed_ID =  "na"
            selectedContentLibrary.Type = "Text"
            #selectedContentLibrary.Skill = ""
            selectedContentLibrary.Questions = ""
            #selectedContentLibrary.AnswerOptions = request.POST['AnswerOptions'].encode('ascii','replace')
            selectedContentLibrary.RightAnswer = ""
            #selectedContentLibrary.Right_Ans_Response = request.POST['Right_Ans_Response'].encode('ascii','replace')
            #selectedContentLibrary.Wrong_Ans_Response = request.POST['Wrong_Ans_Response'].encode('ascii','replace')

            selectedContentLibrary.save()
            self.updateUserStateDict(userID, "CONTENT_ORDER",intCurrentContentOrder)
            return selectedContentLibrary
        except KeyError,e:
            self.logger.error("actionSaveContent "+str(e))

    def actionSaveModuleTitle(self,userID, recevied_message,strDictParams=""):
        try:
            self.updateUserStateDict(userID,"EDITING_CHALLENGE",None)
            userStateObj = UserState.objects.get(UserID=userID)
            selectedModule = Module()
            selectedModule.Title = recevied_message
            selectedModule.UserID = userStateObj.UserID
            selectedModule.AuthorURL = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/walnuty_small.png"
            selectedModule.Goal =  ""
            selectedModule.Author = userStateObj.UserName
            selectedModule.Units = 0
            selectedModule.save()
            #selectedModule.refresh_from_db()
            self.updateUserStateDict(userID, "EDITING_MODULE",selectedModule.ID)
            self.updateUserStateDict(userID, "EDITING_MODULE_TITLE",selectedModule.ID)
            self.updateUserStateDict(userID, "MODULE_ID",selectedModule.ID)

            self.updateUserStateDict(userID, "CONTENT_ORDER","0")
        except KeyError,e:
            self.logger.error("actionSaveModuleTitle "+str(e))


    def actionEndContent(self,userID, recevied_message,strDictParams=""):
        try:
            #self.updateUserStateDict(userID,"EDITING_MODULE","")
            #self.updateUserStateDict(userID,"CONTENT_ORDER","0")
            a=1
        except KeyError,e:
            self.logger.error("actionSaveModuleTitle "+str(e))


    def updateUserStateDict(self,userID, key="",value=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            strDict =  userStateObj.UserStateDict
            if strDict is None :
                strDict = ""
            if strDict.strip() != "":
                dictUserState = json.loads(strDict)
            else:
                dictUserState = {}
            dictUserState[key] = value
            userStateObj.UserStateDict = json.dumps(dictUserState)
            userStateObj.save()
        except KeyError,e:
            self.logger.error("updateUserStateDict "+str(e))

    def getFromUserStateFromDict(self,userID, key=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            if userStateObj.UserName =="":
                self.UpdateUserInfoSlack(userID)
                userStateObj = UserState.objects.get(UserID=userID)
            strDict =  userStateObj.UserStateDict
            if strDict is None:
                strDict = ""
            strReturnValue = ""
            dictUserState={}
            if strDict.strip() != "":
                dictUserState = json.loads(strDict)
            dictUserState["USER_NAME"] = userStateObj.UserName
            dictUserState["USER_EMAIL"] = userStateObj.UserEmail
            dictUserState["USER_GENDER"] =userStateObj.UserGender
            dictUserState["USER_ROLE"] = userStateObj.UserRole
            dictUserState["USER_TIME_ZONE"] = userStateObj.UserTimeZone




            intLocalHour = 0
            intLocalHour = self.getCurrentUserLocalHour(userID)
            if intLocalHour < 12:
                strGreeting = "Good Morning"
            elif intLocalHour >12 and intLocalHour < 18:
                strGreeting = "Good Afternoon"
            else:
                strGreeting ="Good Evening"
            dictUserState["GREETING_TIME_OF_DAY"] = strGreeting

            if key in dictUserState:
                strReturnValue = dictUserState[key]
            return strReturnValue
        except KeyError,e:
            self.logger.error("getFromUserStateFromDict "+str(e))



    def actionSaveChallenge(self,userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            strModuleID = self.getFromUserStateFromDict(userID,"EDITING_MODULE")

            selectedChallenge = Challenge()

            intContentCount = ContentLibrary.objects.filter(Module_ID=int(strModuleID)).count()

            # Save to ContentLibrary
            selectedContentLibrary = ContentLibrary()
            selectedContentLibrary.Type = "Text"
            selectedContentLibrary.Module_ID =  strModuleID
            selectedContentLibrary.Text = recevied_message
            selectedContentLibrary.Content_Order= intContentCount+1
            selectedContentLibrary.Message_Type = "UGC"

            selectedContentLibrary.save()

            selectedChallenge.Content_ID = selectedContentLibrary.ID
            selectedChallenge.Module_ID=int(strModuleID)
            selectedChallenge.Correct_Answer = "A"
            selectedChallenge.UserID = userID
            selectedChallenge.save()


            #selectedModule.refresh_from_db()
            self.updateUserStateDict(userID, "EDITING_CHALLENGE",selectedChallenge.id)
            self.updateUserStateDict(userID, "EDITING_CONTENT",selectedContentLibrary.ID)

            #self.updateUserStateDict(userID, "CONTENT_ORDER","0")
        except KeyError,e:
            self.logger.error("actionSaveChallenge "+str(e))



    def actionSaveChallengeText(self,userID, recevied_message,strDictParams=""):
        try:
            strChallengeText = ""
            strTags = ""
            arrTags = re.findall(r'([#?]\w+)', recevied_message)
            strChallengeText = recevied_message

            if arrTags is not None:
                for tag in arrTags:
                    strTags += tag + ","
                    strChallengeText =  strChallengeText.replace(tag,"")
            strChallengeText = strChallengeText.strip()



            userStateObj = UserState.objects.get(UserID=userID)

            strContentID = self.getFromUserStateFromDict(userID,"EDITING_CONTENT")
            if strContentID is not "":
                selectedContentLibrary = ContentLibrary.objects.get(ID = strContentID)
                selectedContentLibrary.Tags = strTags
                selectedContentLibrary.Text = strChallengeText
                selectedContentLibrary.save()
            #selectedModule.refresh_from_db()
            #self.updateUserStateDict(userID, "EDITING_CHALLENGE",selectedChallenge.ID)
            #self.updateUserStateDict(userID, "CONTENT_ORDER","0")
        except KeyError,e:
            self.logger.error("actionSaveChallengeText "+str(e))

    def actionSaveChallengeQuestion(self,userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            self.actionSaveChallenge(userID,"",strDictParams)
            strChallengeKey = self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            strModuleID = self.getFromUserStateFromDict(userID,"EDITING_MODULE")

            if strChallengeKey =="" or strChallengeKey is None:
                selectedChallenge = Challenge()
                selectedChallenge.Module_ID = strModuleID
                selectedChallenge.Correct_Answer = "A"
                selectedChallenge.UserID = userID
            else:
                selectedChallenge = Challenge.objects.get(id = strChallengeKey)
            selectedChallenge.Question_Text = recevied_message
            selectedChallenge.save()

            contentLibraryObj = ContentLibrary.objects.get(ID=selectedChallenge.Content_ID)
            contentLibraryObj.Text = recevied_message
            contentLibraryObj.save()

            self.updateUserStateDict(userID,"EDITING_CHALLENGE",selectedChallenge.id)
            #selectedModule.refresh_from_db()
            #self.updateUserStateDict(userID, "EDITING_CHALLENGE",selectedChallenge.ID)
            #self.updateUserStateDict(userID, "CONTENT_ORDER","0")
        except KeyError,e:
            self.logger.error("actionSaveChallengeQuestion "+str(e))




    def actionSaveChallengeRightOption(self,userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            strChallengeKey = self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            selectedChallenge = Challenge.objects.get(id = strChallengeKey)
            selectedChallenge.Option_A = recevied_message
            selectedChallenge.save()
            #selectedModule.refresh_from_db()
            #self.updateUserStateDict(userID, "EDITING_CHALLENGE",selectedChallenge.ID)
            #self.updateUserStateDict(userID, "CONTENT_ORDER","0")
        except KeyError,e:
            self.logger.error("actionSaveChallengeRightOption "+str(e))

    def actionSaveChallengeWrongOption(self,userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            strChallengeKey = self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            selectedChallenge = Challenge.objects.get(id = strChallengeKey)

            if recevied_message!="":
                arrWrongOptions = recevied_message.split(",")

            for wrongOption in arrWrongOptions:
                wrongOption = wrongOption.strip()
                if selectedChallenge.Option_B is None:
                    selectedChallenge.Option_B = wrongOption
                elif selectedChallenge.Option_C is None:
                    selectedChallenge.Option_C = wrongOption
                elif selectedChallenge.Option_D is None:
                    selectedChallenge.Option_D = wrongOption
                elif selectedChallenge.Option_E is None:
                    selectedChallenge.Option_E = wrongOption

            selectedChallenge.save()
            #selectedModule.refresh_from_db()
            #self.updateUserStateDict(userID, "EDITING_CHALLENGE",selectedChallenge.ID)
            #self.updateUserStateDict(userID, "CONTENT_ORDER","0")
        except KeyError,e:
            self.logger.error("actionSaveChallengeWrongOption "+str(e))

    def getCurrentUserLocalHour(self,userID):
        userStateObj = UserState.objects.get(UserID=userID)
        currentUTCHour=0
        if userStateObj is not None:
            dateTimeObj = datetime.now()
            currentUTCHour = dateTimeObj.hour

            if currentUTCHour + int(userStateObj.UserTimeZone)<0:
                currentLocalHour = 24 + currentUTCHour + int(userStateObj.UserTimeZone)
            elif currentUTCHour + int(userStateObj.UserTimeZone)>24:
                currentLocalHour = currentUTCHour + int(userStateObj.UserTimeZone)-24
            else:
                currentLocalHour = currentUTCHour + int(userStateObj.UserTimeZone)
        return currentLocalHour

    def UpdateUserInfoFacebook(self, userID):
        try:
            post_message_url = self.configSettingsObj.facebookGraphAPIURL + userID + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + self.configSettingsObj.fbPageAccessTokenArise
            status = requests.get(post_message_url)
            if (status.ok):
                strUserDetails = status.content
                dictUserDetails = json.loads(strUserDetails)

                userStateObj = UserState.objects.get(pk=userID)
                userStateObj.UserName = str(dictUserDetails["first_name"]) +" " + str(dictUserDetails["last_name"])
                if "gender" in dictUserDetails:
                    userStateObj.UserGender = dictUserDetails["gender"]
                if "timezone" in dictUserDetails:
                    userStateObj.UserTimeZone = dictUserDetails["timezone"]
                else:
                    userStateObj.UserTimeZone = -8
                if "email" in dictUserDetails:
                    userStateObj.UserEmail = dictUserDetails["email"]

                userStateObj.save()

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

    def UpdateUserInfoSlack(self, userID):
        try:
            strTeamID = UserState.objects.get(UserID= userID).Org_ID
            strBotAccessToken = PlatformCredentials.objects.filter(SlackTeamID=strTeamID)[0].SlackBotAccessToken
            strSlackToken = strBotAccessToken
            strUserID = userID
            slackURL = "https://slack.com/api/users.info?token=" + strSlackToken + "&user=" + strUserID + "&include_labels=True&pretty=1"
            #post_message_url = self.configSettingsObj.facebookGraphAPIURL + userID + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + self.configSettingsObj.fbPageAccessTokenArise
            status = requests.get(slackURL)
            if (status.ok):
                strUserDetails = status.content
                dictUserDetailsAll = json.loads(strUserDetails)
                if "user" in dictUserDetailsAll:
                    if "profile" in dictUserDetailsAll["user"]:
                        dictUserDetails = dictUserDetailsAll["user"]["profile"]
                        userStateObj = UserState.objects.get(pk=userID)
                        userStateObj.UserName = str(dictUserDetails["first_name"]) +" " + str(dictUserDetails["last_name"])
                        if "gender" in dictUserDetails:
                            userStateObj.UserGender = dictUserDetails["gender"]
                        if "timezone" in dictUserDetails:
                            userStateObj.UserTimeZone = dictUserDetails["timezone"]
                        if "email" in dictUserDetails:
                            userStateObj.UserEmail = dictUserDetails["email"]
                        if "title" in dictUserDetails:
                            userStateObj.UserRole = dictUserDetails["title"]
                        if "Phone" in dictUserDetails:
                            userStateObj.UserPhone = dictUserDetails["Phone"]
                        if "image_512" in dictUserDetails:
                            userStateObj.UserImageSmall = dictUserDetails["image_512"]
                        if "image_1024" in dictUserDetails:
                            userStateObj.UserImageBig = dictUserDetails["image_512"]
                        userStateObj.save()

                        #----Set MixPanelUserDetails
                        dictMPUserDetails = {}
                        dictMPUserDetails["$first_name"] = dictUserDetails["first_name"]
                        dictMPUserDetails["$last_name"] =dictUserDetails["last_name"]
                        dictMPUserDetails["$email"] =""
                        dictMPUserDetails["$phone"] =""
                        if "gender" in dictUserDetails:
                            dictMPUserDetails["$gender"] =dictUserDetails["gender"]
                        mp.people_set(userID, dictMPUserDetails)
        except Exception,e:
            self.logger.error('UpdateUserInfoSlack' + str(e))
