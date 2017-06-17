import sys
import os

"""
WSGI config for curious project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "curious.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

env_variables_to_pass = ['BASE_DEV_DIR_PATH', 'BASE_PROD_DIR_PATH', ]
def application(environ, start_response):
    # pass the WSGI environment variables on through to os.environ
    for var in env_variables_to_pass:
        os.environ[var] = environ.get(var, '')
    return _application(environ, start_response)

baseDevDirPath = os.environ['BASE_DEV_DIR_PATH']
baseProdDirPath = os.environ['BASE_PROD_DIR_PATH']

sys.path.append(baseDevDirPath + '/curious')
sys.path.append(baseDevDirPath)
