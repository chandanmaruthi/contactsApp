import urllib
import json
import csv
import csv
import configSettings
from configSettings import configSettings
import MySQLdb.cursors
#filePath = "skill_list.csv"
apiKey ="AIzaSyCIYz3kUm2SH8wkGJkYbZ9itJT2tEbPicc"
skillContentFilePath = "skillContentURLs.csv"
dictContentList = []
#with open(filePath, 'rb') as csvfile:
#	lineReader = csv.DictReader(csvfile, delimiter=',')
configSettingsObj = configSettings()
db = MySQLdb.connect(host=configSettingsObj.dbHost ,    # your host, usually localhost
					 user=configSettingsObj.dbUser,         # your username
					 passwd=configSettingsObj.dbPassword,  # your password
					 db=configSettingsObj.dbName)        # name of the data base
cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
#-------------------- Load Events --------------------------

role='Product'

cur.execute("Select Role,Skill from curiousWorkbench_roledemandinfo")
rows =  cur.fetchall()

for line in rows:
	strRole = line["Role"]
	searchWord=line["Skill"]
	searchWordFormated = "how to  " +searchWord
	url = "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=15&videoDuration=short&type=video&q="+ searchWordFormated + "&key="+ apiKey

	feed = urllib.urlopen(url)
	feed = feed.read()
	feed_json = json.loads(feed)

	for feed in feed_json['items']:
		dictContent = {}
		dictContent["Video_title"] = feed['snippet']['title'].encode('utf-8')
		dictContent["Video_ID"] = feed['id']['videoId'].encode('utf-8')
		dictContent["Video_Image"]  = feed['snippet']['thumbnails']['medium']['url'].encode('utf-8')
		dictContent["Video_Author"]  = feed['snippet']['channelTitle'].encode('utf-8')
		dictContent["Video_Skill"] = searchWord.replace(" ", "_")
		dictContentList.append(dictContent)

keys = dictContentList[0].keys()

with open(skillContentFilePath, 'w') as mycsvfileWrite:
    dict_writer = csv.DictWriter(mycsvfileWrite, keys, quotechar='"')
    dict_writer.writeheader()
    dict_writer.writerows(dictContentList)
