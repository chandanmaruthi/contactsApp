import sys
server = "DEV"
#server = "PROD"


if server=="DEV":
    sys.path.append('/home/ubuntu/ebs1/serverCode/dev/botrepo1/curious/curious')
    sys.path.append('/home/ubuntu/ebs1/serverCode/dev/botrepo1/curious')
    appSettingsPath= "/home/ubuntu/ebs1/serverCode/dev/botrepo1/curious/curiousWorkbench/appSettings.json"
    rootDir = '/home/ubuntu/ebs1/serverCode/dev/botrepo1/curious'
    appDir = "/home/ubuntu/ebs1/serverCode/dev/botrepo1/curious/curiousWorkbench"
    webURLRoot = "test.walnutai.com"
if server == "PROD":
    sys.path.append('/home/ubuntu/ebs1/serverCode/prod/curious/curious')
    sys.path.append('/home/ubuntu/ebs1/serverCode/prod/curious')
    appSettingsPath= "/home/ubuntu/ebs1/serverCode/prod/curious/curiousWorkbench/appSettings.json"
    rootDir = '/home/ubuntu/ebs1/serverCode/prod/curious'
    appDir = "/home/ubuntu/ebs1/serverCode/prod/curious/curiousWorkbench"
    webURLRoot = "test.walnutai.com"

class environmentVariables():
    def __init__():
        print 'a'
