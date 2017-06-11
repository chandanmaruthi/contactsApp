import sys
server = "DEV"
#server = "PROD"
baseDevDirPath="/Users/chandannm/Documents/chandanWorkspace/workspace/dev/moonshotRepo/curious"
baseProdDirPath="/Users/chandannm/Documents/chandanWorkspace/workspace/dev/moonshotRepo/curious"

if server=="DEV":
    sys.path.append(baseDevDirPath + '/curious')
    sys.path.append(baseDevDirPath)
    appSettingsPath= baseDevDirPath + "/curiousWorkbench/appSettings.json"
    rootDir = baseDevDirPath
    appDir = baseDevDirPath + "/curiousWorkbench"
    webURLRoot = "https://test.walnutai.com"
if server == "PROD":
    sys.path.append(baseProdDirPath + 'curious')
    sys.path.append(baseProdDirPath)
    appSettingsPath= baseProdDirPath + "/curiousWorkbench/appSettings.json"
    rootDir = baseProdDirPath
    appDir = baseProdDirPath + "/curiousWorkbench"
    webURLRoot = "https://test.walnutai.com"

class environmentVariables():
    def __init__():
        print 'a'
