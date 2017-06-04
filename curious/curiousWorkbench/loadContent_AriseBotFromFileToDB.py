import csv
import configSettings
from configSettings import configSettings
configSettingsObj = configSettings()
import json
import MySQLdb


db = MySQLdb.connect(host=configSettingsObj.dbHost ,    # your host, usually localhost
                     user=configSettingsObj.dbUser,         # your username
                     passwd=configSettingsObj.dbPassword,  # your password
                     db=configSettingsObj.dbName)        # name of the data base
cur = db.cursor()

#-------------------- Clear Database ----------------------------
stateMachineAristBotFilePath = 'data/stateMachine_AriseBot.csv'
#r_server =  redis.Redis(host="localhost",db="14")
#r_server.flushdb()
#-------------------- Load StateMachine --------------------------
with open(stateMachineAristBotFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    cur.execute("delete from curiousWorkbench_statemachine where Event_Code !=''")
    db.commit()
    for line in lineReader:
        if line['Event_Code'].strip() !='' :
            strSQL = "INSERT INTO curiousWorkbench_statemachine(Event_Code,SM_ID,ExpectedState,State,Expiry,Action,NextEvent,CallFunction,ParentSystem) values("
            strSQL += " '" + line['Event_Code'] +"',"
            strSQL += " '" + line['SM_ID'] +"',"
            strSQL += " '" + line['ExpectedState'] +"',"
            strSQL += " '" + line['State'] +"',"
            strSQL += " '" + line['Expiry'] +"',"
            strSQL += " '" + line['Action'] +"',"
            strSQL += " '" + line['NextEvent'] +"',"
            strSQL += " '" + line['CallFunction'] +"',"
            strSQL += " '" + line['ParentSystem'] +"'"
            strSQL += ")"
            print strSQL
            cur.execute(strSQL)
    db.commit()
#
#---------------------Load Messages--------------------------------
messageStoreAriseBotFilePath = 'data/messageLibrary_AriseBot.csv'
with open(messageStoreAriseBotFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    cur.execute("delete from curiousWorkbench_messagelibrary where Action !=''")
    db.commit()
    for line in lineReader:
        if line['Action'].strip() !='' :
            #Action,MsgOrder,MessageType,MessageText,MessageImage,MessageVideo,MessageButtons,MessageQuickReplies
            strSQL = "INSERT INTO curiousWorkbench_messagelibrary(ID,Action,MsgOrder,MessageType,MessageText,MessageImage,MessageVideo,MessageButtons,MessageQuickReplies) values("
            strSQL += " \"" + line['ID'] +"\","
            strSQL += " \"" + line['Action'] +"\","
            strSQL += " \"" + line['MsgOrder'] +"\","
            strSQL += " \"" + line['MessageType'] +"\","
            strSQL += " \"" + line['MessageText'].replace("\"","") +"\","
            strSQL += " \"" + line['MessageImage'] +"\","
            strSQL += " \"" + line['MessageVideo'] +"\","
            strSQL += " \"" + line['MessageButtons'] +"\","
            strSQL += " \"" + line['MessageQuickReplies'] + "\""
            strSQL += ")"
            print strSQL
            cur.execute(strSQL)
        db.commit()
#--------------------Load Content-----------------------------------
contentCSVFilePath ="data/AriseBotContent.csv"
with open(contentCSVFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    cur.execute("delete from curiousWorkbench_contentlibrary where ID !=''")
    db.commit()
    for line in lineReader:
        if line['ID'].strip() !='' :
            #ID,Title,Subtitle,ImageURL,LinkURL,Embed_ID,Type,Skill,Questions,AnswerOptions,RightAnswer
            strSQL = "INSERT INTO curiousWorkbench_contentlibrary(ID,Module_ID, Content_Order,Message_Type, Text, Title,Subtitle,ImageURL,LinkURL,Embed_ID,Type,Skill,Questions,AnswerOptions,RightAnswer,Right_Ans_Response,Wrong_Ans_Response) values("
            strSQL += " \"" + line['ID'] +"\","
            strSQL += " \"" + line['Module_ID'] +"\","
            strSQL += " \"" + line['Content_Order'] +"\","
            strSQL += " \"" + line['Message_Type'] +"\","
            strSQL += " \"" + line['Text'].replace("\"","") +"\","
            strSQL += " \"" + line['Title'].replace("\"","") +"\","
            strSQL += " \"" + line['Subtitle'].replace("\"","") +"\","
            strSQL += " \"" + line['ImageURL'] +"\","
            strSQL += " \"" + line['LinkURL'] +"\","
            strSQL += " \"" + line['Embed_ID'] +"\","
            strSQL += " \"" + line['Type'] +"\","
            strSQL += " \"" + line['Skill'] +"\","
            strSQL += " \"" + line['Questions'] +"\","
            strSQL += " \"" + line['AnswerOptions'] +"\","
            strSQL += " \"" + line['RightAnswer'] + "\","
            strSQL += " \"" + line['Right_Ans_Response'] +"\","
            strSQL += " \"" + line['Wrong_Ans_Response'] +"\""

            strSQL += ")"
            print strSQL
            cur.execute(strSQL)
            db.commit()

#------------------Load Role Demand Info ---------------------
roleDemandInfoCSVFilePath ="data/RoleDemandInfo.csv"
with open(roleDemandInfoCSVFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    cur.execute("delete from curiousWorkbench_roledemandinfo where ID !=''")
    db.commit()
    for line in lineReader:
        if line['Role'].strip() !='' :
            strSQL = "INSERT INTO curiousWorkbench_roledemandinfo(ID,Role, Location,CompanyClass, Skill, SKILL_CODE,Percentage,Enabled) values("
            strSQL += " \"" + line['Skill_ID'] +"\","
            strSQL += " \"" + line['Role'] +"\","
            strSQL += " \"" + line['Location'] +"\","
            strSQL += " \"" + line['CompanyClass'] +"\","
            strSQL += " \"" + line['Skill'] +"\","
            strSQL += " \"" + line['SKILL_CODE'] +"\","
            strSQL += " \"" + line['Percentage'] +"\","
            strSQL += " \"" + line['Enabled'] +"\""
            strSQL += ")"
            print strSQL
            cur.execute(strSQL)
            db.commit()
db.close()

#
# objFile = open(configSettingsObj.appFolderPath + "Content.csv","r")
# lines = objFile.readlines()
# for strLine in lines:
#     line = strLine.split(",")
#     if len(line) ==4:
#         logger.info('added 1')
#         strTitle = line[0]
#         strSubTitle = line[1]
#         strImageURl = line[2]
#         strLinkURL = line[3]
#         arrContentDict.append({"Title":strTitle,"SubTitle":strSubTitle,"ImageURL": strImageURl,"LinkURL":strLinkURL})
# logger.info('EndLoaadingContent')
