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
    create database contactsApp01;
    exit;
```

load data into database
```
    mysql -h localhost -u root -p contactApp01 < loadSQLScripts.sql 
```

Update the app setting file to read from our new database

```
    sudo nano curious/curiousWorkbench/appSettings.json
```

Change the following values
```
    "dbHost" : "localhost" ,
    "dbUser" : "root"    ,
    "dbPassword" : "<update with your db password>",
    "dbName" : "<update with name of the db you just created>"
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
