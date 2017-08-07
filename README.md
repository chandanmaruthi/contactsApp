# README #

Welcome to Contacts App

### Key objectives ###

* Build a app that resembles Mac contacts

### What does it do  ###
*  Allow user to login to a web app
*  Allow user to search contacts with fast response with Ajax and Elastic Search
*  Import Google Contacts, This has been done but load interface not open to user, note 2 days of dev/test/documentation time spent

### Design Considerations  ###

*  Data Model design [Mysql]
*  Data import mechanism from google contacts [Python scripts]
*  Data Search backend [Elastic Search]
*  API  [Java Spring] 
*  Web App [Django Ajax]
*  Clean Up 
*  Upload to Git

### Can I install and use it myself ###

* Please follow the instructions below

### What has not been implemented  ###
* Security
* Export data, edit data
* Edit contacts


## Installation instructions ##

###Lets Create a Virtual Env to intall our code###
```
    pip install virtualenv virtualenvwrapper
    vitural env contactsApp
    cd contactsApp
    source bin/activate
```

###Lets Install LAMP, Django and other Dependencies###
```
    sudo apachectl start
    brew install mysql
    pip install MySQL-python
    pip install mod_wsgi
    sudo pip install Django django-sslserver   django-registration djangorestframework MySQL-python requests python-magic
```

###Get the code from Git###
```
git clone https://github.com/chandanmaruthi/contactsApp.git
```

Create a data base
```
    mysql -u root -p
    <enter password>
    create database <enter database name>;
    exit;
```

load data into database
```
    mysql -h localhost -u root -p <enter database name> < loadSQLScripts.sql 
```

Update the app setting file to read from our new database

```
    sudo nano curious/curiousWorkbench/appSettings.json
```
find current working directory
```
pwd
<prints the present working directory >
```
Copy the parent directory that contains the curious folder

Change the following values of appsettings at curious/curiousWorkbench/appSettings.json
```
    "dbHost" : "localhost" ,
    "dbUser" : "root"    ,
    "dbPassword" : "<update with your db password>",
    "dbName" : "<enter database name>"
    "basePath":"<update the output form pwd statement>/curious",
```    


Install the war file in apache tomcat
```
    cp contacts-app-0.0.1-SNAPSHOT.war <inter web apps folder location  of your tomcap installation>

```
Test the api
```
    localhost:8080/contacts-app-0.0.1-SNAPSHOT/contactses
```
you must see a json output from the api

Create a logs directory under contactsApp folder

```
mkdir curious/curiousWorkbench/logs
```
Lets Test the app, Visit this url [when ]



```
    python manage.py runserver  
```

```
System check identified 4 issues (0 silenced).
August 05, 2017 - 16:20:54
Django version 1.9, using settings 'curious.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Lets test the app
    http://127.0.0.1:8000/login/#

You mu
