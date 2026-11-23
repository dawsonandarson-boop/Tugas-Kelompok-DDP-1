"""
WSGI config for laguhati project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laguhati.settings')
application = get_wsgi_application()
