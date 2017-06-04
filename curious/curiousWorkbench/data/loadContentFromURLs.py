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

contentCSVFilePath ="skillContentURLs.csv"
with open(contentCSVFilePath, 'rb') as csvfile:
    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    cur.execute("delete from curiousWorkbench_contentlibrary where ID !='' and Message_Type='External_Content'")
    db.commit()
    for line in lineReader:
        print 'a'
        #ID,Title,Subtitle,ImageURL,LinkURL,Embed_ID,Type,Skill,Questions,AnswerOptions,RightAnswer
        strSQL = "INSERT INTO curiousWorkbench_contentlibrary(Module_ID, Content_Order,Message_Type, Text, Title,Subtitle,ImageURL,LinkURL,Embed_ID,Type,Skill,Questions,AnswerOptions,RightAnswer,Right_Ans_Response,Wrong_Ans_Response) values("
        strSQL += " \"" + "0" +"\","
        strSQL += " \"" + "0" +"\","
        strSQL += " \"" + "External_Content" +"\","
        strSQL += " \"" + "" +"\","
        strSQL += " \"" + line['Video_title'].replace("\"","") +"\","
        strSQL += " \"" + line['Video_Author'].replace("\"","") +"\","
        strSQL += " \"" + line['Video_Image'] +"\","
        strSQL += " \"" + "https://www.youtube.com/watch?v=" + str(line['Video_ID'])  +"\","
        strSQL += " \"" + str(line['Video_ID']) +"\","
        strSQL += " \"" + "YouTube" +"\","
        strSQL += " \"" + line['Video_Skill'] +"\","
        strSQL += " \"" + "" +"\","
        strSQL += " \"" + "" +"\","
        strSQL += " \"" + "" + "\","
        strSQL += " \"" + "" +"\","
        strSQL += " \"" + "" +"\""

        strSQL += ")"
        print strSQL
        cur.execute(strSQL)
        db.commit()
