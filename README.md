# README #

Welcome to Contacts App

### Key objectives ###

* Build a app that resembles Mac contacts

### What does it do  ###
*  Able to import Google address book from csv
*  Load data into db/Elastic search and make it available for a user to access
*  Fast response with Ajax/Elastic that prevent screen refresh , trying to keep close to the Mac contacts experience

### Design Considerations  ###

*  Data Model design [Mysql] - Completed
*  Data import mechanism from google contacts [Python scripts]- Completed
*  Data Search backend [Elastic Search]- Completed
*  API  [Java Spring] - Completed
*  Web App [Django Ajax]- Completed
*  Clean Up -[Pending]
*  Upload to Git [Pending]

### Can I install and use it myself ###

* Possible , however very little time had been spent on packaging, total time spent 2 days
* Constraints, Learning curve involved for 1 technology [Java Spring]

### What has not been done  ###
* Security
* Clean install from git
* Export data, edit data

###Things that could go wrong###
* Will update shortly

###Project-Related Intellectual Property###
* Enjoy






###Lets Create a Virtual Env to intall our code###
pip install virtualenv virtualenvwrapper
vitural env contactsApp
cd contactsApp
source bin/activate

###Lets Install LAMP, Django and other Dependencies###
sudo apachectl start
brew install mysql
pip install MySQL-python
pip install mod_wsgi
sudo pip install Django django-sslserver   django-registration djangorestframework MySQL-python requests python-magic

###Get the code from Git###
git clone https://github.com/chandanmaruthi/contactsApp.git
Create a data base
create database contactsApp01;
load data into database
mysql -h localhost -u root -p contactList < loadSQLScripts.sql 

Update the app setting file to read from our new database
sudo nano curious/curiousWorkbench/appSettings.json
Change the following values
  "dbHost" : "localhost" ,
    "dbUser" : "root"    ,
    "dbPassword" : "testchandan123",
    "dbName" : "contactsApp1"
    
 install the war file in apache tomcat
 copy war file to tomcat web apps folder [under the apache tomcap source folder]
Test the api
localhost:8080/contacts-app-0.0.1-SNAPSHOT/contactses

visit the website
http://127.0.0.1:8000/

 
lets start django server  
python manage.py runserver  
