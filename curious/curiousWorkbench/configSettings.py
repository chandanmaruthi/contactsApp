import json
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

class configSettings:
    appSettingsPath = dir_path + "/appSettings.json"
    fileAppSetttings = open(appSettingsPath,'rb')
    jsonSettings = json.load(fileAppSetttings)
    serverName =  jsonSettings['Server']
    basePath =""
    if serverName == "DEV":
        basePath = jsonSettings[serverName]['basePath']
    elif serverName == "PROD":
        basePath =  jsonSettings[serverName]['basePath']

    #------------DB Credentials ------------------------------------------------------------------------------
    _dbHost = jsonSettings[serverName]['dbHost']
    _dbUser = jsonSettings[serverName]['dbUser']
    _dbPassword = jsonSettings[serverName]['dbPassword']
    _dbName = jsonSettings[serverName]['dbName']
    _inMemDbPort = jsonSettings[serverName]['inMemDbPort']

    _inMemDbHost = jsonSettings[serverName]['inMemDbHost']
    _inMemDataDbName = jsonSettings[serverName]['inMemDataDbName']
    _inMemStateDbName = jsonSettings[serverName]['inMemStateDbName']
    #-----------Server Folder locations---------------------------------------------------------------------------------------------

    _appFolderPath = basePath + jsonSettings[serverName]['appFolderPath']
    _helpFilePath = basePath + jsonSettings[serverName]['helpFilePath']
    _absFileLocation = basePath + jsonSettings[serverName]['absFileLocation']
    _logFolderPath = basePath + jsonSettings[serverName]['logFolderPath']
    #--------------WIT Credentials------------------------------------------------------------------------------------------
    _witToken = jsonSettings[serverName]['witToken']
    #--------------FB Credentials------------------------------------------------------------------------------------------
    _webUrl = jsonSettings[serverName]['webUrl']
    _facebookAuthURL = jsonSettings[serverName]['facebookAuthURL']
    _fbPageAccessTokenArise = jsonSettings[serverName]['fbPageAccessTokenArise']
    _facebookPostMessageURL = jsonSettings[serverName]['facebookPostMessageURL']
    _facebookGraphAPIURL = jsonSettings[serverName]['facebookGraphAPIURL']
    _fbVerifyToken = jsonSettings[serverName]['fbVerifyToken']
    #---------------Slack Credtials-----------------------------------------------------------------------------------------
    _slackWalnutClientID = jsonSettings[serverName]['slackWalnutClientID']
    _slackClientSecret = jsonSettings[serverName]['slackClientSecret']
    _slackVerificationToken = jsonSettings[serverName]['slackVerificationToken']
    _slackOAuthAccessToken = jsonSettings[serverName]['slackOAuthAccessToken']

    @property
    def helpFilePath(self):
        return self._helpFilePath
    @property
    def absFileLocation(self):
        return self._absFileLocation
    @property
    def appFolderPath(self):
        return self._appFolderPath
    @property
    def logFolderPath(self):
        return self._logFolderPath

    @property
    def witToken(self):
        return self._witToken
    @property
    def facebookAuthURL(self):
        return self._facebookAuthURL
    @property
    def dbHost(self):
        return self._dbHost
    @property
    def dbUser(self):
        return self._dbUser
    @property
    def dbPassword(self):
        return self._dbPassword
    @property
    def dbName(self):
        return self._dbName

    @property
    def inMemDbHost(self):
        return self._inMemDbHost
    @property
    def inMemDataDbName(self):
        return self._inMemDataDbName
    @property
    def inMemStateDbName(self):
        return self._inMemStateDbName
    @property
    def inMemDbPort(self):
        return self._inMemDbPort



    @property
    def webUrl(self):
        return self._webUrl

    @property
    def fbPageAccessTokenArise(self):
        return self._fbPageAccessTokenArise

    @property
    def facebookPostMessageURL(self):
        return self._facebookPostMessageURL

    @property
    def facebookGraphAPIURL(self):
        return self._facebookGraphAPIURL

    @property
    def fbVerifyToken(self):
        return self._fbVerifyToken

    @property
    def slackWalnutClientID(self):
        return self._slackWalnutClientID

    @property
    def slackClientSecret(self):
        return self._slackClientSecret

    @property
    def slackVerifyToken(self):
        return self._slackVerifyToken

    @property
    def slackOAuthAccessToken(self):
        return self._slackOAuthAccessToken
