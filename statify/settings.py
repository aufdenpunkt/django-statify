# -*- coding: utf-8 -*-
#

# Core imports
import os

# 3rd party imports
from django.conf import settings


STATIFY_BUILD_SETTINGS = getattr(settings, u'STATIFY_BUILD_SETTINGS', '',)
STATIFY_USE_CMS = getattr(settings, u'STATIFY_USE_CMS', False,)
STATIFY_PROJECT_DIR = getattr(settings, u'STATIFY_PROJECT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'),)
STATIFY_UPLOAD_PATH = getattr(settings, u'STATIFY_UPLOAD_PATH', os.path.join(u'statify/releases/'),)
STATIFY_EXCLUDED_MEDIA = getattr(settings, u'STATIFY_EXCLUDED_MEDIA', [u'admin', u'statify', u'tmp', u'root'],)
STATIFY_ROOT_STATIC = getattr(settings, u'STATIFY_ROOT_STATIC', os.path.join(settings.MEDIA_ROOT, 'root'),)
STATIFY_ROOT_STATIC_URL = getattr(settings, u'STATIFY_ROOT_STATIC_URL', settings.STATIC_URL + 'root/',)
