import redis
import csv
import configSettings
from configSettings import configSettings
import MySQLdb.cursors
import json

class BotState():

    def refreshBot(self):
        #-------------------- Clear Database ----------------------------
        stateMachineAristBotFilePath = 'data/stateMachine_AriseBot.csv'
        r_server =  redis.Redis(host="localhost",db="14")
        r_server.flushdb()

        configSettingsObj = configSettings()
        db = MySQLdb.connect(host=configSettingsObj.dbHost ,    # your host, usually localhost
                             user=configSettingsObj.dbUser,         # your username
                             passwd=configSettingsObj.dbPassword,  # your password
                             db=configSettingsObj.dbName)        # name of the data base
        cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        #-------------------- Load Events --------------------------

        cur.execute("Select Event_Code, SM_ID, ExpectedState, State, Expiry, Action_old, NextEvent, CallFunction, ParentSystem, MessageID_old from curiousWorkbench_statemachine")
        rows =  cur.fetchall()
        for line in rows:
            if line['Event_Code'].strip() !='' :
                r_server.hset("KEY_EVENT_" +line['Event_Code'], line['SM_ID'],json.dumps(line))
                print json.dumps(line) , '------------------'

        #---------------------Load Messages--------------------------------
        cur.execute("Select Action_old, MsgOrder, MessageType, MessageText, MessageImage, MessageVideo, MessageButtons, MessageQuickReplies, ID, EventID from curiousWorkbench_messagelibrary")
        rows =  cur.fetchall()
        for line in rows:
                if line['EventID'] !='' :
                    r_server.hset("KEY_ACTION_" + str(line['EventID']), line['MsgOrder'],json.dumps(line))
                    print json.dumps(line) , '------------------'
        #--------------------Load Content-----------------------------------
        cur.execute("Select ID, Title, Subtitle, ImageURL, LinkURL, Embed_ID, Type, Content_Order, Module_ID, Text, Message_Type, Rating, Tags from curiousWorkbench_contentlibrary")
        rows =  cur.fetchall()
        for line in rows:
                if line['ID'] !='' :
                    r_server.hset("KEY_CONTENT_" + str(line['ID']),"Msg", json.dumps(line))
                    print line, '------------------'

        # #------------------Load Role Demand Info ---------------------
        # cur.execute("Select * from curiousWorkbench_roledemandinfo")
        # rows =  cur.fetchall()
        # for line in rows:
        #     if line['Role'].strip() !='' :
        #         r_server.hset("KEY_ROLE_" + line['Role'],line['ID'], json.dumps(line))
        #         print line, '------------------'
        #------------------Load Module ---------------------
        # cur.execute("Select * from curiousWorkbench_module")
        # rows =  cur.fetchall()
        # for line in rows:
        #     if line['Title'].strip() !='' :
        #         r_server.hset("KEY_MODULE_" + str(line['ID']),'ID', json.dumps(line))
        #         print line, '------------------'
