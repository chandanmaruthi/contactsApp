
from django.conf.urls import url
from django.conf import settings
from django.views.generic import TemplateView

from django.views import generic
import logging
import mixpanel
from mixpanel import Mixpanel
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/..")
from django.http import Http404, HttpResponse

from configSettings import configSettings
from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator


class slackClientWalnutBotView(generic.View):
    mp = Mixpanel("7a2ae593d77b3bd1b818d79ce75b69ff")
    configSettingsObj = configSettings()
    #----------------Logging ------------------
    logger = logging.getLogger('views')
    hdlr = logging.FileHandler( configSettingsObj.logFolderPath + 'slackViews.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.info('logging log folder path')
    logger.info(configSettingsObj.logFolderPath)
    #----------------Logging ------------------

    def get(self, request, *args, **kwargs):
        #print 'in get'
        try:
            ####self.logger.info(str('i am here 1'))
            #print configSettingsObj.fbVerifyToken , request.GET['hub.verify_token']
            if request.GET['token'] == configSettingsObj.slackVerifyToken:
                return HttpResponse(self.request.GET['challenge'])
                ####self.logger.info(str('i am here 2'))
            else:
                return HttpResponse('Error, invalwewid token111')
        except KeyError,e:
            # Redisplay the question voting form.
            self.logger.error(str('i am here 3'))
            self.logger.error(str(e))
            return HttpResponse('Error, invalid token1234')

            #print str(e)


    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        #print 'in dispatch'
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        try:

            ###self.logger.info(str(request.body.decode('utf-8')))
            strBody = request.body.decode('utf-8')
            jsonBody = json.loads(strBody)
            strToken= jsonBody["token"]
            strChallenge = jsonBody["challenge"]
            if strToken == configSettingsObj.slackVerifyToken:
                return HttpResponse(strChallenge)
                ####self.logger.info(str('i am here 2'))
            else:
                return HttpResponse('Error, invalwewid token111')
        except KeyError,e:
            #return HttpResponse('uvuPXncnG0CNBNYX5nhMLqYanbQLZwIbTseZLOWhDmMsKwb9zclM')
            self.logger.error('Views.py post handler Error')
            self.logger.error(str(e))
