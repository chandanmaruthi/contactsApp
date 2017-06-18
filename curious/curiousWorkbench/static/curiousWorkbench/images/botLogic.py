# -*- coding: utf-8 -*-
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

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
from models import StateMachine, MessageLibrary, ContentLibrary, UserModuleProgress, Module, UserCertification,RoleDemandInfo,Progress, Challenge,ChallengeResultSummary,ChallengeResultUser
from django.shortcuts import get_list_or_404, get_object_or_404
import urllib

import os.path
import apiai
from django.forms.models import model_to_dict
import mixpanel
from mixpanel import Mixpanel
mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")
import pygal

class botLogic():
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
    r_server =  redis.Redis(host=configSettingsObj.inMemDbHost,db=configSettingsObj.inMemDataDbName)
    r_stateServer =  redis.Redis(host=configSettingsObj.inMemDbHost,db=configSettingsObj.inMemStateDbName)

    def __init__(self):
        try:
            inputMsg='no value'
            lastTopicNumber = 15
            ######self.logger.info('init')
            db = MySQLdb.connect(host=self.configSettingsObj.dbHost,    # your host, usually localhost
                                 user=self.configSettingsObj.dbUser,         # your username
                                 passwd=self.configSettingsObj.dbPassword,  # your password
                                 db=self.configSettingsObj.dbName)        # name of the data base
        except Exception,e:
            self.logger.error('fbClient init here' + str(e))


    def getButton(self, stype, stitle, surl='', spayload=''):
        #self.logger.info("3.5-----" + stype +"---" + stitle +"---" + surl +"---" +spayload )

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
                self.UpdateUserInfo(userID)

        except UserState.DoesNotExist:

            newUserState = UserState(UserID = userID,
                             UserCurrentState = 'INIT' ,
                         	UserLastAccessedTime = datetime.now())
            newUserState.save()
            #mp.track(userID, "New_User",{'User_Gender':dictUserDetails["gender"],'User_Age':'','':''})
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
            #######self.logger.info("user details " + str(userID) + str(strSkill) +str(intPoints))

            userSkillStatusObj = UserSkillStatus.objects.get(userID = userID, skill = strSkill)
            #######self.logger.info("check here")
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
            #######self.logger.info("in add user" )
            post_message_url = self.configSettingsObj.facebookGraphAPIURL + userID + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + self.configSettingsObj.fbPageAccessTokenArise
            #####self.logger.info("post url" + post_message_url )
            status = requests.get(post_message_url)
            if (status.ok):
                strUserDetails = status.content
                ####self.logger.info("recevived response" + str(strUserDetails) )
                dictUserDetails = json.loads(strUserDetails)

                userStateObj = UserState.objects.get(pk=userID)
                userStateObj.UserName = str(dictUserDetails["first_name"]) +" " + str(dictUserDetails["last_name"])
                if "gender" in dictUserDetails:
                    userStateObj.UserGender = dictUserDetails["gender"]
                if "timezone" in dictUserDetails:
                    userStateObj.UserTimeZone = dictUserDetails["timezone"]
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
                ######self.logger.info(dictResult["data"][intRantInt]["images"]["original"]["url"])
                strImage = dictResult["data"][intRantInt]["images"]["original"]["url"]
            strMessageType = "Buttons"
            strMessage = "Hmm,I did not get that!"
            strVideoURL = ""
            strSubTitleInfo = ""
            strLink = ""
            dictButtons =[]
            payload = "SHOW_RECO"
            dictButtons.append(self.getButton("postback","explore a skill",surl="",spayload=payload))
            strLink = ""
            strQuickReplies = ""
            strDictButtons = json.dumps(dictButtons)

            strQuickReplies =""
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict(strMessageType,strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"REGULAR")
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('action_showRandomMessage ' + str(e))

    def actionGetLocationFromPin(self, userID, recevied_message,strDictParams="" ):
        try:
            userStateObj = UserState.objects.get(pk=userID)
            strLocationPIN= userStateObj.Location_PIN
            self.logger.info("in actionGetLocationFromPin " + strLocationPIN)
            post_message_url = "http://maps.googleapis.com/maps/api/geocode/json?address="
            post_message_url = post_message_url + strLocationPIN
            #######self.logger.info(post_message_url)

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
            strSkilNameOld = dictContent.Skill
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

            strQuickReplyPostback = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + str(dictContent.SKILL_CODE)
            strQuickReplies += "text" + ":" + "Learn this skill" + ":" + strQuickReplyPostback

            #######self.logger.info()
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
            #####self.logger.info(str("here"))
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
                    #####self.logger.info(str(arr))
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
            retArr=[]
            dictParams={}
            self.logger.info("0")
            ######self.logger.info(strDictParams)

            intMessageCount = 0
            skillCode = ""
            contentID=-1
            contentFeedback=""
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "SKILL_CODE" in dictParams:
                    skillCode = dictParams["SKILL_CODE"]

                if "CONTENT_FEEDBACK" in dictParams:
                    contentFeedback = dictParams["CONTENT_FEEDBACK"]
                if "CONTENT_ID" in dictParams:
                    contentID = int(dictParams["CONTENT_ID"])

            if contentID !=-1:
                prevContentLibraryObj = ContentLibrary.objects.get(ID=contentID)
                if contentFeedback == "Like":
                    prevContentLibraryObj.Rating +=1
                elif contentFeedback == "DisLike":
                    prevContentLibraryObj.Rating -=1
                prevContentLibraryObj.save()

            self.logger.info("1")
            arrAltMessage = []
            #arrAltMessage = self.actionTakenPeriodicAction(userID, recevied_message,strDictParams)
            #if len(arrAltMessage)==0:
            contentLibraryObj = ContentLibrary.objects.filter(Skill=skillCode, Message_Type="External_Content",Rating__gte=1)
            intNumberOfKeys =  contentLibraryObj.count()
            if intNumberOfKeys == 0 :
                contentLibraryObj = ContentLibrary.objects.filter(Message_Type="External_Content",Rating__gte=1)
                intNumberOfKeys =  contentLibraryObj.count()
            if intNumberOfKeys>1:
                intRantInt = randint(0,intNumberOfKeys-1)
            else:
                intRantInt = 0

            contentLibrary = contentLibraryObj[intRantInt]

            self.logger.info("2")
            strMessageType = "Buttons"
            strMessage = contentLibrary.Title[:79]
            strVideoURL = ""
            strImage = ""
            strSubTitleInfoSkill = contentLibrary.Skill[:30].replace("_", " ")
            strSubTitleInfo = "By : " + contentLibrary.Subtitle[:30] + " \r\nSkill : " + strSubTitleInfoSkill + "\r\nTime:< 4 min"
            self.logger.info("3")
            strLink = contentLibrary.LinkURL
            if contentLibrary.ImageURL != "":
                strImage =   contentLibrary.ImageURL
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCV/" + str(contentLibrary.ID) +"/" +str(userID)
            dictButtons.append(self.getButton("web_url","Learn, 1 credit 🏆",surl=strLink,spayload=""))
            dictButtons.append(self.getButton("postback","See my progress 📈 ",surl="",spayload="CHECK_PROGRESS"))
            dictShareLinks = self.getShareLinks(strMessage,strLink)
            if str(contentLibrary.Questions.strip()) != "":
                payload = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + str(contentLibrary.ID)
                self.logger.info("4")
                dictButtons.append(self.getButton("postback","claim 1 pt",surl="",spayload=payload))
            recoPayload =""
            if skillCode == "":
                recoPayload="SHOW_RECO"
            else:
                recoPayload = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + skillCode

            #dictButtons.append(self.getButton("postback","try another skill",surl="",spayload="SHOW_SKILL_STAT"))
            #dictButtons.append(self.getButton("postback","next >>",surl="",spayload=recoPayload))

            strDictButtons = json.dumps(dictButtons)
            strQuickReplies = ""
            self.logger.info("5")

            dictParams1 = self.getRecoButtons(recoPayload,strMessage,strSubTitleInfo,str(contentLibrary.ID))
            strQuickReplies = dictParams1["QuickReplies"]

            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"REGULAR")
            retArr.append(dictParams)


            #retArr.append(dictParams1)
            #else:
            #    retArr.append(arrAltMessage[0])
            return retArr
        except Exception,e:
            self.logger.error('actionGetReco ' + str(e))


    def actionGetChallenge(self, userID, recevied_message,strDictParams=""):
        try:
            retArr=[]
            dictParams={}
            self.logger.info("0")
            ######self.logger.info(strDictParams)

            intMessageCount = 0
            skillCode = ""
            challengeID=-1
            contentFeedback=""
            userCreatedContentID =  self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "SKILL_CODE" in dictParams:
                    skillCode = dictParams["SKILL_CODE"]

                # if "CONTENT_FEEDBACK" in dictParams:
                #     contentFeedback = dictParams["CONTENT_FEEDBACK"]
                if "CHALLENGE_ID" in dictParams:
                    challengeID = int(dictParams["CONTENT_ID"])
                elif userCreatedContentID !="":
                    challengeID = userCreatedContentID
            else:
                challengeID = userCreatedContentID

            if challengeID !=-1:
                challengeObj = Challenge.objects.get(id=challengeID)
                #challengeObjArr = Challenge.objects.all()
                #intNumberOfKeys =  challengeObjArr.count()

                # if contentFeedback == "Like":
                #     prevContentLibraryObj.Rating +=1
                # elif contentFeedback == "DisLike":
                #     prevContentLibraryObj.Rating -=1
                # prevContentLibraryObj.save()
            else:
                challengeObjArr = Challenge.objects.all()
                intNumberOfKeys =  challengeObjArr.count()

                #if intNumberOfKeys > 0 :
                    #contentLibraryObj = ContentLibrary.objects.filter(Message_Type="External_Content",Rating__gte=1)
                    #intNumberOfKeys =  contentLibraryObj.count()
                if intNumberOfKeys>1:
                    intRantInt = randint(0,intNumberOfKeys-1)
                else:
                    intRantInt = 0
                    challengeObj = challengeObjArr[intRantInt]
            self.logger.info("1")
            #arrAltMessage = []
            #arrAltMessage = self.actionTakenPeriodicAction(userID, recevied_message,strDictParams)
            #if len(arrAltMessage)==0:
            # contentLibraryObj = ContentLibrary.objects.filter(Skill=skillCode, Message_Type="External_Content",Rating__gte=1)
            # intNumberOfKeys =  contentLibraryObj.count()
            # if intNumberOfKeys == 0 :
            #     contentLibraryObj = ContentLibrary.objects.filter(Message_Type="External_Content",Rating__gte=1)
            #     intNumberOfKeys =  contentLibraryObj.count()
            # if intNumberOfKeys>1:
            #     intRantInt = randint(0,intNumberOfKeys-1)
            # else:
            #     intRantInt = 0



            self.logger.info("2")
            strMessageType = "Text"
            strMessage = challengeObj.Challenge_Text
            strVideoURL = ""
            strImage = ""
            #strSubTitleInfoSkill = contentLibrary.Skill[:30].replace("_", " ")
            #strSubTitleInfo = "By : " + contentLibrary.Subtitle[:30] + " \r\nSkill : " + strSubTitleInfoSkill + "\r\nTime:< 4 min"
            self.logger.info("3")
            #strLink = contentLibrary.LinkURL
            # if contentLibrary.ImageURL != "":
            #     strImage =   contentLibrary.ImageURL
            dictButtons =[]
            # strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCV/" + str(contentLibrary.ID) +"/" +str(userID)
            # dictButtons.append(self.getButton("web_url","Learn, 1 credit 🏆",surl=strLink,spayload=""))
            # dictButtons.append(self.getButton("postback","See my progress 📈 ",surl="",spayload="CHECK_PROGRESS"))
            # dictShareLinks = self.getShareLinks(strMessage,strLink)
            # if str(contentLibrary.Questions.strip()) != "":
            #     payload = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + str(contentLibrary.ID)
            #     self.logger.info("4")
            #     dictButtons.append(self.getButton("postback","claim 1 pt",surl="",spayload=payload))
            recoPayload =""
            if skillCode == "":
                recoPayload="SHOW_RECO"
            else:
                recoPayload = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + skillCode

            #dictButtons.append(self.getButton("postback","try another skill",surl="",spayload="SHOW_SKILL_STAT"))
            #dictButtons.append(self.getButton("postback","next >>",surl="",spayload=recoPayload))

            # strDictButtons = json.dumps(dictButtons)
            # strQuickReplies = ""
            # self.logger.info("5")
            #
            # dictParams1 = self.getRecoButtons(recoPayload,strMessage,strSubTitleInfo,str(contentLibrary.ID))
            # strQuickReplies = dictParams1["QuickReplies"]

            if challengeObj.Option_A is not None:
                strQuickReplies = "text" + ":" + str(challengeObj.Option_A) + ":" + "CHECK_CHALLENGE_ANS-ANS|A-CHALLENGE_ID|" + str(challengeID)
            if challengeObj.Option_B is not None:
                strQuickReplies += "," + "text" + ":" + str(challengeObj.Option_B) + ":" + "CHECK_CHALLENGE_ANS-ANS|B-CHALLENGE_ID|" + str(challengeID)
            if challengeObj.Option_C is not None:
                strQuickReplies += "," + "text" + ":" + str(challengeObj.Option_C) + ":" + "CHECK_CHALLENGE_ANS-ANS|C-CHALLENGE_ID|" + str(challengeID)
            if challengeObj.Option_D is not None:
                strQuickReplies += "," + "text" + ":" + str(challengeObj.Option_D) + ":" + "CHECK_CHALLENGE_ANS-ANS|D-CHALLENGE_ID|" + str(challengeID)
            if challengeObj.Option_E is not None:
                strQuickReplies += "," + "text" + ":" + str(challengeObj.Option_E) + ":" + "CHECK_CHALLENGE_ANS-ANS|E-CHALLENGE_ID|" + str(challengeID)

            strSubTitleInfo=""
            strLink =""
            strDictButtons =""
            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"REGULAR")
            retArr.append(dictParams)


            #retArr.append(dictParams1)
            #else:
            #    retArr.append(arrAltMessage[0])
            return retArr
        except Exception,e:
            self.logger.error('actionGetChallenge ' + str(e))

    def getRecoButtons(self, recoPayload,strMessage1,strSubTitleInfo1,strContentID):
        strMessageType ="Text"
        strMessage = strMessage1 + "\r\n"+strSubTitleInfo1
        strImage = ""
        strSubTitleInfo = ""
        strImage = ""
        strVideoURL = ""
        strLink = ""
        strDictButtons = ""
        strQuickReplies = ""
        strQuickReplyPostbackLike = recoPayload + "-" + "CONTENT_FEEDBACK" + "|" + "Like" + "-" + "CONTENT_ID" + "|" + strContentID
        strQuickReplyPostbackDisLike = recoPayload + "-" + "CONTENT_FEEDBACK" + "|" + "DisLike" + "-" + "CONTENT_ID" + "|" + strContentID
        ###self.logger.info("11")
        strDownImage="1483408247_dislike.png"
        strUpImage="1483408228_like.png"
        ###self.logger.info("22")
        strQuickReplies = "text" + ":" + "dislike" + ":" + strQuickReplyPostbackDisLike  + ":" +strDownImage + ","
        strQuickReplies += "text" + ":" + "Try another skill" + ":" + "SHOW_SKILLS" + ","
        strQuickReplies += "text" + ":" + "like" + ":" + strQuickReplyPostbackLike + ":" + strUpImage
        ###self.logger.info("33")
        ###self.logger.info(strQuickReplies)
        dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"REGULAR")
        return dictParams

    def actionGetRecoNotify(self, userID, recevied_message,strDictParams=""):
        try:
            retArr=[]
            dictParams={}
            ######self.logger.info("0")
            ######self.logger.info(strDictParams)
            intMessageCount = 0
            skillCode = ""
            if strDictParams.strip()!="":
                dictParams = json.loads(strDictParams)
                if "SKILL_CODE" in dictParams:
                    skillCode = dictParams["SKILL_CODE"]
            ######self.logger.info("2")


            contentLibraryObj = ContentLibrary.objects.filter(Skill=skillCode, Message_Type="External_Content",Rating__gte=3)
            intNumberOfKeys =  contentLibraryObj.count()
            if intNumberOfKeys == 0 :
                contentLibraryObj = ContentLibrary.objects.filter(Message_Type="External_Content",Rating__gte=3)
                intNumberOfKeys =  contentLibraryObj.count()
            if intNumberOfKeys>1:
                intRantInt = randint(0,intNumberOfKeys-1)
            else:
                intRantInt = 0

            contentLibrary = contentLibraryObj[intRantInt]
            ######self.logger.info("2")


            strMessageType = "Buttons"
            strMessage = contentLibrary.Title[:79]
            strVideoURL = ""
            strImage = ""
            strSubTitleInfoSkill = contentLibrary.Skill[:30]
            strSubTitleInfo = "by : " + contentLibrary.Subtitle[:30] + ", Skill : " + strSubTitleInfoSkill #+ "    " + "Claim: 1pt"

            strLink = contentLibrary.LinkURL
            if contentLibrary.ImageURL != "":
                strImage =   contentLibrary.ImageURL
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCV/" + str(contentLibrary.ID) +"/" +str(userID)
            dictButtons.append(self.getButton("web_url","read now",surl=strLink,spayload=""))
            dictShareLinks = self.getShareLinks(strMessage,strLink)
            if str(contentLibrary.Questions.strip()) != "":
                payload = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + str(contentLibrary.ID)

                dictButtons.append(self.getButton("postback","claim 1 pt",surl="",spayload=payload))
            recoPayload =""
            if skillCode == "":
                recoPayload="SHOW_RECO"
            else:
                recoPayload = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + skillCode

            dictButtons.append(self.getButton("postback","pick another skill",surl="",spayload="SHOW_SKILL_STAT"))
            dictButtons.append(self.getButton("postback","next >>",surl="",spayload=recoPayload))

            strDictButtons = json.dumps(dictButtons)
            strQuickReplies = ""

            strMessageNotify = "Today's Skill Alert : " + strSubTitleInfoSkill.replace("_"," ") + ", "
            dictParams = self.getMessageDict("Text", strMessageNotify + " " + strMessage , "", "", strImage, strVideoURL, strLink, "", "","REGULAR")
            retArr.append(dictParams)

            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"NO_PUSH")
            retArr.append(dictParams)



            return retArr
        except Exception,e:
            self.logger.error('actionGetRecoNotify ' + str(e))


    def getMessageDict(self, strMessageType, strMessage, strImage, strSubTitleInfo, strImage1, strVideoURL, strLink, strDictButtons, strQuickReplies,strNotificationType="REGULAR",strListContent="",strListButtons=""):
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
        return dictRet

    def actionGetModule(self, userID, recevied_message,strDictParams=""):
        try:
            ########self.logger.info("actionGetModule", userID, recevied_message, strDictParams)
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
                #######self.logger.info("1")
                strMessage = str(moduleObj.Title)[:39] #+ " (in " + moduleObj.SKILL_CODE.replace("_"," ")[:29] + " )"
                strVideoURL = ""
                strImage = str(moduleObj.AuthorURL)
                #######self.logger.info("2")
                strSubTitleInfo = "" #"by: "+ str(moduleObj.Author) + "         " + str(moduleObj.UnitsPerDay) + " mins"
                dictButtons =[]
                strLink =""
                #######self.logger.info("3")
                payload = "START_MODULE" + "-" + "Module_ID" + "|" + str(moduleID)
                dictButtons.append(self.getButton("postback","Pick up this skill",surl="",spayload=payload))
                strDictButtons = json.dumps(dictButtons)
                strQuickReplies = ""
                ######self.logger.info("4")
                #####self.logger.info(strMessage)
                retArr=[]
                dictParams={}
                dictParams = self.getMessageDict("",strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                retArr.append(dictParams)
                return retArr
        except Exception,e:
            self.logger.error('actionGetModule' + str(e))

    def actionStartModule(self, userID, recevied_message,strDictParams=""):
        try:

            #######self.logger.info("")
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
            #strModule= self.r_server.hget( "KEY_MODULE_"+str(moduleID), "ID")
            #dictModule = json.loads(strModule)
            #objModule = Module.objects.get()
            # Update Current Module ID in under state
            userStateObj = UserState.objects.get(pk=userID)
            userStateObj.Current_Module_ID = moduleID #dictModule["ID"]
            userStateObj.save()
            # Get first message of content
            #contentObj =  ContentLibrary.objects.filter(Module_ID=dictModule["ID"]).order_by('Content_Order').first()
            #if contentObj !=None:
            #    intCurrentPosition = contentObj.Content_Order
            # Update Current Module ID in under state
            intCurrentPosition =1
            userModuleProgressObj = UserModuleProgress.objects.filter(ModuleID=moduleID, UserID=userID)
            if userModuleProgressObj == None:
                userModuleProgressObj =  UserModuleProgress()
                userModuleProgressObj.UserID = userID
                userModuleProgressObj.ModuleID = moduleID
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


            #User Accepts Module
            # - postback: Start_Module(ModuleID)
            # - Update UserState.Current Module with Module ID
            # - If No Entry in Module Progress , add and entry
            # - Get the first entry from Module
            # - Show user
            #######self.logger.info("actionNextModuleContent" + str(userID) +str(recevied_message)+str(strDictParams))

            if strDictParams!="":
                dictParams = json.loads(strDictParams)
            #######self.logger.info("heeree 1")
            moduleID = dictParams["Module_ID"]
            #strModule= self.r_server.hget( "KEY_MODULE_"+str(dictParams["Module_ID"]), "ID")
            #dictModule = json.loads(strModule)
            #######self.logger.info("heeree 2")

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
            contentObj =  ContentLibrary.objects.filter(Module_ID=moduleID,Content_Order=dictParams["Content_Order"]).first()
            #######self.logger.info("heeree 3")
            ######self.logger.info(str(contentObj))
            if contentObj !=None:
                #######self.logger.info("heeree 4")
                ######self.logger.info(contentObj.Content_Order)
                intCurrentPosition = contentObj.Content_Order
            # Update Current Module ID in under state
                #######self.logger.info("ok")
                userModuleProgressObj = UserModuleProgress.objects.filter(ModuleID=moduleID, UserID=userID).first()
                #######self.logger.info("ok1")

                if userModuleProgressObj == None:
                    userModuleProgressObj =  UserModuleProgress()
                    userModuleProgressObj.UserID = userID
                    userModuleProgressObj.ModuleID = moduleID
                    userModuleProgressObj.CurrentPosition = intCurrentPosition
                    userModuleProgressObj.save()
                else:
                    userModuleProgressObj.CurrentPosition = intCurrentPosition
                    userModuleProgressObj.save()
                #######self.logger.info("ok2")

                #prepare content to send
                strMessageType = contentObj.Message_Type
                if strMessageType =="Text":
                    strMessage = contentObj.Text[:255]
                    #strMessage += " (" + str(contentObj.Content_Order) + "/" + str(dictModule["Units"]) + ")"
                elif strMessageType =="Image":
                    strImage = contentObj.ImageURL
                #######self.logger.info("ok3")
                if contentObj.Questions !="":
                    strQuickReplyPostback = "SHOW_QUESTIONS" + "-" + "ContentID" + "|" + str(contentObj.ID)
                    strQuickReplies += "text" + ":" + "ok" + ":" +strQuickReplyPostback
                else:
                    strQuickReplyPostback = "NEXT_MODULE_CONTENT" + "-" +"Module_ID" + "|" +str(dictParams["Module_ID"])+ "-"+ "Content_Order" + "|" + str(intCurrentPosition+1)
                    strQuickReplies += "text" + ":" + "ok" + ":" +strQuickReplyPostback


                retArr=[]
                dictParams={}
                dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                retArr.append(dictParams)

                return retArr
            else:
                #######self.logger.info("heeree 4")

                # Module Ended, clear memory
                userStateObj = UserState.objects.get(pk=userID)
                userStateObj.Current_Module_ID = None
                userStateObj.save()
                # Remove Progress Entries in Module Progress
                userModuleProgressObj = UserModuleProgress.objects.filter(ModuleID=dictParams["Module_ID"], UserID=userID).first()
                if userModuleProgressObj != None:
                    userModuleProgressObj.delete()

                retArr = self.actionGetModuleCompletionMessage(userID,recevied_message,strDictParams)

                #retArr=[]
                #dictParams={}
                #dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
                #retArr.append(dictParams)
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
            #######self.logger.info("heeree 10")
            if strDictParams!="":
                dictParams = json.loads(strDictParams)
            objModule = Module.objects.get(ID=int(dictParams["Module_ID"]))
            objUserCertification = UserCertification.objects.filter(Module_ID=int(dictParams["Module_ID"]), userID=userID).first()
            #######self.logger.info("heeree 20")
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
                #######self.logger.info("heeree 25")
            else:
                objUserCertification.date =datetime.now()
                objUserCertification.Title = objModule.Title
                objUserCertification.Author = objModule.Author
                objUserCertification.AuthorURL = objModule.AuthorURL
                objUserCertification.SKILL_CODE = objModule.SKILL_CODE
                objUserCertification.save()
                #######self.logger.info("heeree 26")
            #######self.logger.info("heeree 30")
            strMessage="Awesome, you have compelted this topic"
            strImage = self.configSettingsObj.webUrl +"/static/curiousWorkbench/images/CertificateImageLarge.png"
            strMessageType = "Buttons"
            strSubTitleInfo = "This topic has been added to your skill board"
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCertV/" + str(userID)
            #######self.logger.info("heeree 40")

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
            #######self.logger.info("heeree 59")
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies)
            retArr.append(dictParams)
            return retArr
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

                #######self.logger.info("askQuestions params:" + strDictParams)
                dictParams = json.loads(strDictParams)
                #######self.logger.info("here -2")

                strContentID = dictParams["ContentID"]
                strContent= self.r_server.hget( "KEY_CONTENT_"+strContentID, "Msg")
                #######self.logger.info("here -1")
                ######self.logger.info(strContent)

                dictContent = json.loads(strContent)
                strMessage = dictContent["Questions"][:79]
                #######self.logger.info("here 0")

                strAnswerOptions = dictContent["AnswerOptions"]

                #######self.logger.info("here 1")

                dictAnswerOptions = strAnswerOptions.split("|")
                strVideoURL = ""
                strImage = ""
                #strSubTitleInfo = dictContent["Subtitle"]
                strSubTitleInfo =""
                strLink = ""
                strImage = self.configSettingsObj.webUrl +"/static/curiousWorkbench/images/sunAskQuestion.jpg"
                strImage  =""
                dictButtons =[]
                #######self.logger.info("In Ask Question")
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
                #######self.logger.info("Posted Message")
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
                #######self.logger.info("actionReviewAnswer:" + strDictParams)
                dictParams = json.loads(strDictParams)
                strContentID = dictParams["ContentID"]
                strAnswerID = dictParams["AnswerID"]
                strContent= self.r_server.hget( "KEY_CONTENT_"+strContentID, "Msg")
                dictContent = json.loads(strContent)
                strCorrectAnswerID = dictContent["RightAnswer"]
                ######self.logger.info( "---review ans "+ strAnswerID + strCorrectAnswerID )
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


    def actionShowUserSkills(self, userID, recevied_message,strDictParams=""):
        try:
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
            ###self.logger.info("heeree 59")
            retArr=[]
            dictParams={}
            ###self.logger.info("printing message start")
            strMessage = "1"
            strListContent , strListButtons = self.getSkillList(userID,recevied_message,strDictParams,False)
            strMessage=strMessage[:400]
            ###self.logger.info("printing message end")
            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"REGULAR",strListContent,strListButtons)
            ###self.logger.info(str(dictParams))
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionShowUserSkills' + str(e))

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


            strMessageType = "List"
            strMessage="Here we go click on view progress."
            strImage = self.configSettingsObj.webUrl +"/static/curiousWorkbench/images/CertificateImageLarge.png"
            strSubTitleInfo = "Check It Out"
            dictButtons =[]
            strLink = self.configSettingsObj.webUrl +"/curiousWorkbench/fbABWCertV/" + str(userID)
            dictButtons.append(self.getButton("web_url","View Progress",surl=strLink,spayload=""))

            strDictButtons= json.dumps(dictButtons)
            ###self.logger.info("heeree 59")
            retArr=[]
            dictParams={}
            ###self.logger.info("printing message start")
            strMessage = "1"
            strListContent , strListButtons = self.getSkillList(userID,recevied_message,strDictParams,True)
            strMessage=strMessage[:400]
            ###self.logger.info("printing message end")
            dictParams = self.getMessageDict(strMessageType, strMessage, strImage, strSubTitleInfo, strImage, strVideoURL, strLink, strDictButtons, strQuickReplies,"REGULAR",strListContent,strListButtons)
            ###self.logger.info(str(dictParams))
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
            #self.logger.info("printing 3" + str(strContentID))

            #self.logger.info("printing id" + str(strContentID))
            #self.getFromUserStateFromDict(userID, "EDITING_MODULE")
            self.updateUserStateDict(userID, "UGC_ID", strContentID )
            #self.logger.info("I am gere")
            return
        except Exception,e:
            self.logger.error('actionSaveContentTitle' + str(e))

    def actionSaveContentVideo(self, userID, recevied_message,strDictParams=""):
        try:
            #self.logger.info("I am gere")
            if strDictParams!="":
                dictParams = json.loads(strDictParams)
                if 'VideoURL' in dictParams:
                    VideoURL =  dictParams['VideoURL']
                    contentID = self.getFromUserStateFromDict(userID, "UGC_ID")
                    contentLibraryObj = get_object_or_404(ContentLibrary, ID= contentID)
                    contentLibraryObj.LinkURL = str(contentID) + ".mp4" #VideoURL
                    contentLibraryObj.save()

                    videoPath = self.configSettingsObj.absFileLocation + "/videos/" + str(contentID) + ".mp4"
                    urllib.urlretrieve(VideoURL, videoPath)
            return
        except Exception,e:
            self.logger.error('actionSaveContentVideo' + str(e))

    def actionSaveContentSkill(self, userID, recevied_message,strDictParams=""):
        try:

            contentID = self.getFromUserStateFromDict(userID, "UGC_ID")
            contentLibraryObj = get_object_or_404(ContentLibrary, ID= contentID)
            contentLibraryObj.Skill = recevied_message
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
            ######self.logger.info('actionSetUserRole')
            ######self.logger.info('--' + str(userID))
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
            ######self.logger.info('actionSaveUserLocationProdM')
            self.actionSetUserRole(userID, "Product_Manager")
        except Exception,e:
            self.logger.error('actionSaveUserLocationProdM' + str(e))

    def actionSaveConfirmSubscription(self, userID, recevied_message,strDictParams=""):
        try:
            strNotifyTime="MOR"
            userStateObj = get_object_or_404(UserState, UserID=userID)
            userStateObj.Notify_Subscription = "TRUE"
            ###self.logger.info("received params" + strDictParams)
            if strDictParams !="":
                dictParams= json.loads(strDictParams)
                ####self.logger.info("user notify time" + strDictParams )
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
            ######self.logger.info('actionSaveUserLocationProgM')
            self.actionSetUserRole(userID, "Program_Manager")
        except Exception,e:
            self.logger.error('actionSaveUserLocationProgM' + str(e))

    def actionSaveUserLocationEggM(self, userID, recevied_message,strDictParams=""):
        try:
            ######self.logger.info('actionSaveUserLocationEggM')
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
            self.logger.info( "user role" +  strUserRole)

            strRoleInfoDesc = ""
            moduleID = ""
            roleInfo = self.r_server.hgetall("KEY_ROLE_" + strUserRole)
            self.logger.info("role info " + str(roleInfo))
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

                        #######self.logger.info("---->Module Options" + dictRoleInfo["SKILL_CODE"] + strUserRole)
                        if moduleObj != None:
                            moduleID = moduleObj.ID
                            strPayLoad = "SHOW_MODULE" + "-" + "ID" + "|" + str(moduleID)
                            strQuickReplies += "text" + ":" + str(moduleID) + ":" + strPayLoad
                        #######self.logger.info("I am still here -------")
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
            dictParams = self.getMessageDict("",strMessage, strImage, strSubTitleInfo, strImage, "",self.configSettingsObj.webUrl, strDictButtons,strQuickReplies,"REGULAR")
            retArr.append(dictParams)
            return retArr
            return
        except Exception,e:
            self.logger.error('actionGetRoleDemandInfo' + str(e))


    def actionCheckChallengeAns(self, userID, recevied_message,strDictParams=""):
        try:
            strMessage=""
            self.logger.info("1")
            userStateObj = UserState.objects.get(pk=userID)
            strUserRole =  userStateObj.UserRole
            if strDictParams !="":
                dictParams = json.loads(strDictParams)
                if "CHALLENGE_ID" in dictParams:
                    challengeID = int(dictParams["CHALLENGE_ID"])
                if "ANS" in dictParams:
                    strAns = str(dictParams["ANS"])
            self.logger.info("2")
            objChallenge = Challenge.objects.get(id=challengeID)

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
            try:
                objChallengeResultUser = ChallengeResultUser.objects.get(Challenge_ID= challengeID, UserID = userID)
            except ObjectDoesNotExist:
                objChallengeResultUser = ChallengeResultUser()
                objChallengeResultUser.Challenge_ID = challengeID
                objChallengeResultUser.UserID = userID

            self.logger.info("4")

            objChallengeResultUser.Ans = strAns
            if strAns == "A":
                objChallengeResultUser.IsCorrect == "Y"
                strMessage = "You are right ! "
            else:
                objChallengeResultUser.IsCorrect == "N"
                strMessage = "Oops that was not right ! The right answer was \r\n"
                strMessage += str(objChallenge.Option_A)

            arrSummary=[]
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


            strMessage += "A:" + str(objChallengeResultSummary.Option_A_Count) + "\r\n"
            strMessage += "B:" + str(objChallengeResultSummary.Option_B_Count) + "\r\n"
            strMessage += "C:" + str(objChallengeResultSummary.Option_C_Count) + "\r\n"
            strMessage += "D:" + str(objChallengeResultSummary.Option_D_Count) + "\r\n"
            strMessage += "E:" + str(objChallengeResultSummary.Option_E_Count) + "\r\n"


            objChallengeResultSummary.save()
            objChallengeResultUser.save()

            chartPath = self.configSettingsObj.absFileLocation + "/images/plots/" + str(challengeID) + "-" + str(userID) + ".png"
            chartFileName = str(challengeID) + "-" + str(userID) + ".png"
            bar_chart = pygal.Bar()
            #bar_chart.add('Fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
            bar_chart.add(objChallenge.Option_A, [objChallengeResultSummary.Option_A_Count])
            bar_chart.add(objChallenge.Option_B, [objChallengeResultSummary.Option_B_Count] )
            bar_chart.add(objChallenge.Option_C, [objChallengeResultSummary.Option_C_Count] )
            bar_chart.add(objChallenge.Option_D, [objChallengeResultSummary.Option_D_Count] )
            bar_chart.add(objChallenge.Option_E, [objChallengeResultSummary.Option_E_Count] )
            #bar_chart.render_to_file('bar_chart.svg')
            bar_chart.render_to_png(filename=chartPath)


            self.logger.info("5")
            #
            #
            # userStateObj = UserState.objects.get(pk=userID)
            # strUserRole =  userStateObj.UserRole
            # self.logger.info( "user role" +  strUserRole)
            # intChallengeID =  json.loads(strDictParams)
            # strRoleInfoDesc = ""
            # moduleID = ""
            # ##roleInfo = self.r_server.hgetall("KEY_ROLE_" + strUserRole)
            # self.logger.info("role info " + str(roleInfo))
            # strMessage = "Here are the top 3 skills by demand\r\n"
            # intMax = 4
            # intCount = 0
            # strQuickReplies = ""
            # strRoleInfoDesc = ""
            # strPayLoad = ""
            # strQuickReplies =""
            # for role in roleInfo:
            #     if intCount <= intMax:
            #         dictRoleInfo = json.loads(roleInfo[role])
            #         if dictRoleInfo["Enabled"]=="TRUE":
            #             moduleObj = Module.objects.filter(SKILL_CODE=dictRoleInfo["SKILL_CODE"]).first()
            #             if moduleObj is not None:
            #                 if moduleObj.count()>0:
            #                     strRoleInfoDesc += dictRoleInfo["Skill"] + " [Code : " + str(moduleObj.ID) + "]"+ "\r\n"
            #                 if intCount != 0:
            #                     strQuickReplies += ","
            #
            #             #######self.logger.info("---->Module Options" + dictRoleInfo["SKILL_CODE"] + strUserRole)
            #             if moduleObj != None:
            #                 moduleID = moduleObj.ID
            #                 strPayLoad = "SHOW_MODULE" + "-" + "ID" + "|" + str(moduleID)
            #                 strQuickReplies += "text" + ":" + str(moduleID) + ":" + strPayLoad
            #             #######self.logger.info("I am still here -------")
            #             intCount +=1
            # strRoleInfoDesc += "I will keep looking for more. \r\n Select a code below to acquire a skill "
            # strMessage += strRoleInfoDesc

            #strMessage ="your ans us" + strAns
            strSubTitleInfo = ""
            strImage=""
            strMessage =  strMessage[:295]
            strQuickReplies = ""
            #strMessage = self.getSkillList(userID,"","")
            strDictButtons = ""
            retArr=[]
            dictParams={}
            self.logger.info("6")
            chartURL = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/plots/" + chartFileName
            self.logger.info(chartURL)
            dictParams = self.getMessageDict("Image","", chartURL, "", chartURL, "",self.configSettingsObj.webUrl, strDictButtons,strQuickReplies,"REGULAR")
            retArr.append(dictParams)
            dictParams = self.getMessageDict("Text",strMessage, strImage, strSubTitleInfo, strImage, "",self.configSettingsObj.webUrl, strDictButtons,strQuickReplies,"REGULAR")
            retArr.append(dictParams)

            return retArr
        except Exception,e:
            self.logger.error('actionCheckChallengeAns' + str(e))

    def getSkillList(self,userID,recevied_message,strDictParams="",UserSkillOnlyFlag=False):
        try:
            intListItems=0
            intStartPos = 0
            if strDictParams !="":
                dictParams = json.loads(strDictParams)
                if "START_POSITION" in dictParams:
                    intStartPos = int(dictParams["START_POSITION"])
            ###self.logger.info("tape 1" +  str(intStartPos) + "---" + strDictParams)

            userStateObj = UserState.objects.get(pk=userID)
            intRandIntUserRole = randint(0,90)
            if intRandIntUserRole < 88 and userStateObj.UserRole=="Product_Manager":
                roleDemandInfoObj = RoleDemandInfo.objects.filter(Enabled="TRUE",Role="Product_Manager")
            else:
                roleDemandInfoObj = RoleDemandInfo.objects.exclude(Role="Product_Manager").filter(Enabled="TRUE")
            ###self.logger.info("tape 2")
            intNumberofRoles = roleDemandInfoObj.count()
            ###self.logger.info("something")
            ###self.logger.info(intNumberofRoles)
            #intRantInt = randint(0,intNumberofRoles-1)
            #dictContent = roleDemandInfoObj[intRantInt]
            strMessage = ""
            ######self.logger.info(str(dictContent))
            ###self.logger.info("tape 3")

            strMessageType = "Text"
            arrSkillList =[]
            dictSkillList={}
            intStartIndex = intStartPos
            intMax=intStartIndex+2
            intCount=0
            #----------------------------------------------------
            if UserSkillOnlyFlag==False:
                dictSkillList["Title"] = "Skills for Product Managers"
                dictSkillList["SubTitle"] = "Earn a 🏆 everytime your learn a skill, \r\n"
                dictSkillList["Image"] = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/bannerWithLogo.jpg"
            elif UserSkillOnlyFlag == True:
                dictSkillList["Title"] = "Skills you acquired"
                dictSkillList["SubTitle"] = ""
                dictSkillList["Image"] = self.configSettingsObj.webUrl + "/static/curiousWorkbench/images/bannerWithLogoProgress.jpg"

            dictButton ={}
            #dictbuttons.append(self.getButton(arrButtons["ButtonType"],arrButtons["ButtonTitle"], surl=arrButtons["ButtonLinkURL"], spayload=arrButtons["ButtonPostback"]))
            #dictButton["ButtonType"] = "postback"
            #dictButton["ButtonTitle"] = "Learn"
            #dictButton["ButtonLinkURL"] = ""
            #dictButton["ButtonPostback"] = "SHOW_RECO"
            #dictSkillList["Buttons"] = dictButton
            arrSkillList.append(dictSkillList)

            #----------------------------------------------------
            for roleDemandInfoSkill in roleDemandInfoObj:
                dictSkillList={}
                if intCount>=intStartIndex and intCount<=intMax:
                    dictSkillList["Title"]=""
                    dictContent = roleDemandInfoSkill
                    strSkilNameOld = dictContent.Skill
                    dictSkillName = strSkilNameOld.split(" ")
                    strSkillName = ""
                    skillProgressCredits =0
                    ###self.logger.info("tape 4")
                    try:
                        skillProgressObj = Progress.objects.get(userID=userID,SKILL_CODE=dictContent.Skill.strip().replace(" ","_"))
                        skillProgressCredits = skillProgressObj.Credits
                        ###self.logger.info("here aka1" + str(skillProgressCredits)+ userID + dictContent.Skill)
                    except Progress.DoesNotExist:
                        skillProgressCredits=0
                        ###self.logger.info("here aka2" + str(skillProgressCredits)+ userID + dictContent.Skill)



                    for word in dictSkillName:
                        strSkillName +=word[:1].upper() + word[1:] + " "
                    if int(dictContent.Percentage)>0:
                        dictSkillList["Title"] = strSkillName
                        dictSkillList["SubTitle"] = "Demand 🔥 :" + str(dictContent.Percentage) + "%  My Credits 🏆 : " + str(skillProgressCredits)
                    else:
                        dictSkillList["Title"] += "" + strSkillName
                        dictSkillList["SubTitle"] = "🔥 Common Skill My Credits 🏆 :" +  str(skillProgressCredits)
                    dictButton ={}
                    #dictbuttons.append(self.getButton(arrButtons["ButtonType"],arrButtons["ButtonTitle"], surl=arrButtons["ButtonLinkURL"], spayload=arrButtons["ButtonPostback"]))
                    dictButton["ButtonType"] = "postback"
                    dictButton["ButtonTitle"] = "Learn"
                    dictButton["ButtonLinkURL"] = ""
                    dictButton["ButtonPostback"] = "SHOW_RECO" + "-" + "SKILL_CODE" + "|" + dictContent.SKILL_CODE
                    ##self.logger.info(dictContent.SKILL_CODE)
                    dictSkillList["Buttons"] = dictButton
                    if UserSkillOnlyFlag == True and skillProgressCredits >0:
                        ##self.logger.info("here aaa")
                        arrSkillList.append(dictSkillList)
                        intListItems+=1
                    elif UserSkillOnlyFlag ==False:
                        ##self.logger.info("here bbb")
                        arrSkillList.append(dictSkillList)
                        intListItems+=1
                intCount+=1
            if intListItems ==0:
                dictSkillList["Title"] = "No Progress Yet"
                dictSkillList["SubTitle"] = " You earn 1 🏆 every time you learn a skill"
                dictButton ={}
                dictButton["ButtonType"] = "postback"
                dictButton["ButtonTitle"] = "Discover Skills"
                dictButton["ButtonLinkURL"] = ""
                dictButton["ButtonPostback"] = "SHOW_SKILLS"
                dictSkillList["Buttons"] = dictButton
                arrSkillList.append(dictSkillList)
            #---------------------------------------------

            dictButton ={}
            #dictbuttons.append(self.getButton(arrButtons["ButtonType"],arrButtons["ButtonTitle"], surl=arrButtons["ButtonLinkURL"], spayload=arrButtons["ButtonPostback"]))
            if UserSkillOnlyFlag == True:
                dictButton["type"] = "postback"
                dictButton["title"] = "View more"
                dictButton["payload"] = "CHECK_PROGRESS"+ "-" + "START_POSITION" + "|" + str(intStartPos + 3)
            elif UserSkillOnlyFlag == False:
                dictButton["type"] = "postback"
                dictButton["title"] = "View more"
                dictButton["payload"] = "SHOW_SKILLS"+ "-" + "START_POSITION" + "|" + str(intStartPos + 3)

            #dictSkillList["Buttons"] = dictButton
            strListButtons =  json.dumps([dictButton])

            #---------------------------------------------

            strSkillList= json.dumps(arrSkillList)

            ###self.logger.info("tape 5")
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
            # ######self.logger.info(str(roleInfo))
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
                        #######self.logger.info("I am still here -------")
                intCount +=1
            # strRoleInfoDesc += "I will keep looking for more. \r\n Select a code below to acquire a skill "
            #####self.logger.info(strQuickReplies)
            strSubTitleInfo = ""
            strImage=""
            strMessage =  strMessage[:295]
            strDictButtons = ""
            retArr=[]
            dictParams={}
            dictParams = self.getMessageDict("",strMessage, strImage, strSubTitleInfo, strImage, "",self.configSettingsObj.webUrl , strDictButtons,strQuickReplies,"REGULAR")
            retArr.append(dictParams)
            return retArr
        except Exception,e:
            self.logger.error('actionGetRoleDemandInfo' + str(e))



    def actionSaveContent(self,userID, recevied_message,strDictParams=""):
        try:

            strModuleID = self.getFromUserStateFromDict(userID, "EDITING_MODULE")
            strContentOrder = self.getFromUserStateFromDict(userID, "CONTENT_ORDER")
            ######self.logger.info("current module" + str(strModuleID))
            if strContentOrder == "":
                strContentOrder = 0
            intCurrentContentOrder = int(strContentOrder) + 1
            selectedContentLibrary = ContentLibrary()
            selectedContentLibrary.Module_ID = strModuleID
            selectedContentLibrary.Content_Order = intCurrentContentOrder
            selectedContentLibrary.Message_Type = "Text"
            selectedContentLibrary.Text = recevied_message.encode('ascii','replace')
            selectedContentLibrary.Title = "na"
            selectedContentLibrary.Subtitle = "na"
            selectedContentLibrary.ImageURL =  "na"
            selectedContentLibrary.LinkURL = "na"
            selectedContentLibrary.Embed_ID =  "na"
            selectedContentLibrary.Type = "Text"
            selectedContentLibrary.Skill = ""
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
            userStateObj = UserState.objects.get(UserID=userID)
            selectedModule = Module()
            selectedModule.Title = recevied_message
            selectedModule.UserID = userStateObj.UserID
            selectedModule.AuthorURL = configSettingsObj.webUrl + "static/curiousWorkbench/images/walnuty_small.png"
            selectedModule.Goal =  ""
            selectedModule.Author = userStateObj.UserName
            selectedModule.Units = 0
            selectedModule.save()
            #selectedModule.refresh_from_db()
            self.updateUserStateDict(userID, "EDITING_MODULE",selectedModule.ID)
            self.updateUserStateDict(userID, "CONTENT_ORDER","0")
            #####self.logger.info(selectedModule.ID)
        except KeyError,e:
            self.logger.error("actionSaveModuleTitle "+str(e))


    def actionEndContent(self,userID, recevied_message,strDictParams=""):
        try:
            self.updateUserStateDict(userID,"EDITING_MODULE","")
            self.updateUserStateDict(userID,"CONTENT_ORDER","0")

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
            strDict =  userStateObj.UserStateDict
            if strDict is None:
                strDict = ""
            strReturnValue = ""

            if strDict.strip() != "":
                dictUserState = json.loads(strDict)
                if key in dictUserState:
                    strReturnValue = dictUserState[key]
            return strReturnValue
        except KeyError,e:
            self.logger.error("getFromUserStateFromDict "+str(e))



    def actionSaveChallenge(self,userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            selectedChallenge = Challenge()
            selectedChallenge.Challenge_Text = recevied_message
            selectedChallenge.Correct_Answer = "A"
            selectedChallenge.UserID = userID
            selectedChallenge.save()
            #selectedModule.refresh_from_db()
            self.updateUserStateDict(userID, "EDITING_CHALLENGE",selectedChallenge.id)
            #self.updateUserStateDict(userID, "CONTENT_ORDER","0")
            #####self.logger.info(selectedModule.ID)
        except KeyError,e:
            self.logger.error("actionSaveChallenge "+str(e))


    def actionSaveChallengeQuestion(self,userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            strChallengeKey = self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            selectedChallenge = Challenge.objects.get(id = strChallengeKey)
            selectedChallenge.Question_Text = recevied_message
            selectedChallenge.save()
            #selectedModule.refresh_from_db()
            #self.updateUserStateDict(userID, "EDITING_CHALLENGE",selectedChallenge.ID)
            #self.updateUserStateDict(userID, "CONTENT_ORDER","0")
            #####self.logger.info(selectedModule.ID)
        except KeyError,e:
            self.logger.error("actionSaveChallengeRightOption "+str(e))


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
            #####self.logger.info(selectedModule.ID)
        except KeyError,e:
            self.logger.error("actionSaveChallengeRightOption "+str(e))

    def actionSaveChallengeWrongOption(self,userID, recevied_message,strDictParams=""):
        try:
            userStateObj = UserState.objects.get(UserID=userID)
            strChallengeKey = self.getFromUserStateFromDict(userID,"EDITING_CHALLENGE")
            selectedChallenge = Challenge.objects.get(id = strChallengeKey)
            if selectedChallenge.Option_B is None:
                selectedChallenge.Option_B = recevied_message
            elif selectedChallenge.Option_C is None:
                selectedChallenge.Option_C = recevied_message
            elif selectedChallenge.Option_D is None:
                selectedChallenge.Option_D = recevied_message
            elif selectedChallenge.Option_E is None:
                selectedChallenge.Option_E = recevied_message

            selectedChallenge.save()
            #selectedModule.refresh_from_db()
            #self.updateUserStateDict(userID, "EDITING_CHALLENGE",selectedChallenge.ID)
            #self.updateUserStateDict(userID, "CONTENT_ORDER","0")
            #####self.logger.info(selectedModule.ID)
        except KeyError,e:
            self.logger.error("actionSaveChallengeWrongOption "+str(e))
