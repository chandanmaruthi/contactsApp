import sys
import os
baseDevDirPath = os.environ['BASE_DEV_DIR_PATH']
baseProdDirPath = os.environ['BASE_PROD_DIR_PATH']

sys.path.append(baseDevDirPath + '/curious')
sys.path.append(baseDevDirPath)

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
