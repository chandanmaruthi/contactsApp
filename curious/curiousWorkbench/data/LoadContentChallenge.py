import csv
import os
import sys
import random
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../")
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

filePath = "Content_WithQuestions_1.csv"
#-------------------- Load Events --------------------------
with open(filePath, 'rb') as csvfile:

    cur.execute("delete from curiousWorkbench_contentlibrary where Message_Type ='UGC'")
    cur.execute("delete from curiousWorkbench_challenge")
    db.commit()

    lineReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for line in lineReader:
        strInsertContent = ""
        strInsertChallenge =""
        if line['Content'].strip() !='' :
            strContent = line['Content'].strip()
            strContent = strContent.replace("'","")
            strContent = strContent.replace('"','')
            strTags =  line['Tag'].strip()

            strInsertContent = "INSERT INTO curiousWorkbench_contentlibrary(Text,Type,Message_Type,Rating,Tags) Values("
            strInsertContent += "'" + strContent + "','Text','UGC',50,'" + strTags + "');"

            print strInsertContent
            cur.execute(strInsertContent)
            strContentID = cur.lastrowid


            strChallengeText = line['Question'].strip()
            strRightAns= line['Right_Ans'].strip()
            arrWrongAns = line['Wrong_Ans'].strip().split(",")
            strAnsA =""
            strAnsB =""
            strAnsC =""
            strAnsD =""
            strAnsE =""
            intChoices = len(arrWrongAns)+1
            if intChoices <= 2:
                arrList=['A','B']
            if intChoices == 3:
                arrList=['A','B','C']
            if intChoices == 4:
                arrList=['A','B','C','D']
            if intChoices >= 5:
                arrList=['A','B','C','D','E']

            selectedChoice=random.choice(arrList)
            strCorrectAns = selectedChoice

            if selectedChoice == "A":
                strAnsA = strRightAns
                if len(arrWrongAns) >= 1:
                    strAnsB = arrWrongAns[0]
                if len(arrWrongAns) >= 2:
                    strAnsC = arrWrongAns[1]
                if len(arrWrongAns) >= 3:
                    strAnsD = arrWrongAns[2]
                if len(arrWrongAns) >= 4:
                    strAnsE = arrWrongAns[3]

            if selectedChoice == "B":
                strAnsB = strRightAns
                if len(arrWrongAns) >= 1:
                    strAnsA = arrWrongAns[0]
                if len(arrWrongAns) >= 2:
                    strAnsC = arrWrongAns[1]
                if len(arrWrongAns) >= 3:
                    strAnsD = arrWrongAns[2]
                if len(arrWrongAns) >= 4:
                    strAnsE = arrWrongAns[3]

            if selectedChoice == "C":
                strAnsC = strRightAns
                if len(arrWrongAns) >= 1:
                    strAnsA = arrWrongAns[0]
                if len(arrWrongAns) >= 2:
                    strAnsB = arrWrongAns[1]
                if len(arrWrongAns) >= 3:
                    strAnsD = arrWrongAns[2]
                if len(arrWrongAns) >= 4:
                    strAnsE = arrWrongAns[3]

            if selectedChoice == "D":
                strAnsD = strRightAns
                if len(arrWrongAns) >= 1:
                    strAnsA = arrWrongAns[0]
                if len(arrWrongAns) >= 2:
                    strAnsB = arrWrongAns[1]
                if len(arrWrongAns) >= 3:
                    strAnsC = arrWrongAns[2]
                if len(arrWrongAns) >= 4:
                    strAnsE = arrWrongAns[3]

            if selectedChoice == "E":
                strAnsE = strRightAns
                if len(arrWrongAns) >= 1:
                    strAnsA = arrWrongAns[0]
                if len(arrWrongAns) >= 2:
                    strAnsB = arrWrongAns[1]
                if len(arrWrongAns) >= 3:
                    strAnsC = arrWrongAns[2]
                if len(arrWrongAns) >= 4:
                    strAnsD = arrWrongAns[3]


            strInsertChallenge = "INSERT INTO curiousWorkbench_challenge(UserID,Content_ID,Question_Text,Correct_Answer,Option_A,Option_B,Option_C,Option_D,Option_E) VALUES("
            strInsertChallenge +=  "'SYS'," +str(strContentID) + ",'" + strChallengeText + "', '"+selectedChoice +"', '" + strAnsA +"', '" + strAnsB  +"', '" + strAnsC  +"', '" + strAnsD +"', '" + strAnsE +"');"
            print strInsertChallenge
            cur.execute(strInsertChallenge)
            db.commit()
