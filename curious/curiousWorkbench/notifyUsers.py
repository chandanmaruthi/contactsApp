import sys
import os
import django
import sys
sys.path.append("/home/ubuntu/ebs1/dev/botrepo1/curious")
sys.path.append("/home/ubuntu/ebs1/dev/botrepo1/curious/curiousWorkbench")

settings.configure()
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# your imports, e.g. Django models

django.setup()

from models import UserState, UserSkillStatus
from models import StateMachine, MessageLibrary, ContentLibrary, Module, UserCertification
import urllib
from fbClientBotArise import fbClientBotArise

from configSettings import configSettings
import logging
import mixpanel
from mixpanel import Mixpanel
mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")


intCounter = 0
logger.info('entered reminder function')
#if passID == "4321":
post_message_url = configSettingsObj.facebookPostMessageURL%configSettingsObj.fbPageAccessTokenArise
fbCustBotObj = fbClientBotArise()
#userStateObjs = UserState.objects.filter(Notify_Subscription="TRUE")

configSettingsObj = configSettings()
db = MySQLdb.connect(host=configSettingsObj.dbHost ,    # your host, usually localhost
                     user=configSettingsObj.dbUser,         # your username
                     passwd=configSettingsObj.dbPassword,  # your password
                     db=configSettingsObj.dbName)        # name of the data base
cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
#-------------------- Load Events --------------------------

cur.execute("Select UserID from curiousWorkbench_userstate where Notify_Subscription='TRUE'")
rows =  cur.fetchall()

logger.info('in Reminder function')
for userStateRow in rows:
    userID = userStateRow["UserID"]
    mp.track(userStateRow["UserID"], "Reminder",{'strNextEvent':"",'strToState':"",'strCallFunction':""})

    #if userID == "1383980648297827":
    logger.info('matching user id')
    payload = "SHOW_RECO"
    response_msg = fbCustBotObj.processEvent(payload, userID, recevied_message='')
    logger.info(post_message_url)
    for response_msg_item in response_msg:
        logger.info(response_msg_item)
        if response_msg_item !='':
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg_item)
            intCounter +=1
            logger.info(status)
