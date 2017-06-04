import sys
import os
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

absRolesFolderPath = ""
rolesFile = "SoftSkills.csv"
filePath = absRolesFolderPath + rolesFile

file = open(filePath,'rb')
lineReader = csv.DictReader(file, delimiter = ",")
cur.execute("delete from curiousWorkbench_roledemandinfo where SKILL_CODE ='Soft_Skills'")
Percentage=0
for line in lineReader:
    #print (float(line['Demand_Count'])/int(line['World_Count']))
    if int(line['Demand_Count']) >0 and int(line['World_Count'])>0:
        Percentage = int((float(line['Demand_Count'])/int(line['World_Count']))*100)
    else:
        Percentage = 0
    print line
    strSQL = "Insert into curiousWorkbench_roledemandinfo"
    strSQL += "(Role,Location,CompanyClass,Skill,SKILL_CODE,Percentage,Enabled,Demand_Count,World_Count) "
    strSQL += "Values"
    strSQL +="('" + line['Role'] + "','SFO','1001','" + line['SKILL_CODE'].replace("_"," ") + "','" + line['SKILL_CODE'] + "'," + str(Percentage) + ",'TRUE'," + line['Demand_Count'] + "," + line['World_Count'] + ") ;"
    print strSQL
    cur.execute(strSQL)
    db.commit()

#Insert table curiousWorkbench_roledemandinfo('Role','Location','CompanyClass','Skill','SKILL_CODE','Percentage','Enabled','Demand_Count','World_Count') Values('Product_Manager','SFO','1001','product_line','product line',0,'TRUE',244,573) ;
