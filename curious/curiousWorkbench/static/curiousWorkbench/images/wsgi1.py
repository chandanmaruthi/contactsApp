import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
from environmentVariables import environmentVariables
from environmentVariables import *

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
