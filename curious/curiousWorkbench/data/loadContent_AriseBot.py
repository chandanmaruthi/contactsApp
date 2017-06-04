import redis
import csv
import configSettings
import json

#-------------------- Clear Database ----------------------------
stateMachineAristBotFilePath = 'data/stateMachine_AriseBot.csv'
r_server =  redis.Redis(host="localhost",db="14")
r_server.flushdb()
#-------------------- Load Events --------------------------
with open(stateMachineAristBotFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for line in lineReader:
        if line['Event_Code'].strip() !='' :
            r_server.hset("KEY_EVENT_" +line['Event_Code'], line['SM_ID'],json.dumps(line))
            print json.dumps(line) , '------------------'

#---------------------Load Messages--------------------------------
messageStoreAriseBotFilePath = 'data/messageLibrary_AriseBot.csv'
with open(messageStoreAriseBotFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for line in lineReader:
        if line['Action'].strip() !='' :
            r_server.hset("KEY_ACTION_" + line['Action'], line['MsgOrder'],json.dumps(line))
            print json.dumps(line) , '------------------'
#--------------------Load Content-----------------------------------
contentCSVFilePath ="data/AriseBotContent.csv"
with open(contentCSVFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for line in lineReader:
        if line['Title'].strip() !='' :
            r_server.hset("KEY_CONTENT_" + line['ID'],"Msg", json.dumps(line))
            print line, '------------------'

#------------------Load Role Demand Info ---------------------
roleDemandInfoCSVFilePath ="data/RoleDemandInfo.csv"
with open(roleDemandInfoCSVFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for line in lineReader:
        if line['Role'].strip() !='' :
            r_server.hset("KEY_ROLE_" + line['Role'],line['Skill_ID'], json.dumps(line))
            print line, '------------------'
