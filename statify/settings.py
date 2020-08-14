# -*- coding: utf-8 -*-
#

# Core imports
import os

# 3rd party imports
from django.conf import settings


STATIFY_BUILD_SETTINGS = getattr(settings, 'STATIFY_BUILD_SETTINGS', '')
STATIFY_USE_CMS = getattr(settings, 'STATIFY_USE_CMS', False)
STATIFY_IGNORE_MEDIA = getattr(settings, 'STATIFY_IGNORE_MEDIA', False)
STATIFY_IGNORE_STATIC = getattr(settings, 'STATIFY_IGNORE_MEDIA', False)
STATIFY_PROJECT_DIR = getattr(settings, 'STATIFY_PROJECT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
STATIFY_UPLOAD_PATH = getattr(settings, 'STATIFY_UPLOAD_PATH', 'statify/releases/')
STATIFY_EXCLUDED_STATIC = getattr(settings, 'STATIFY_EXCLUDED_STATIC', ['admin', 'statify', 'tmp', 'root'])
STATIFY_ROOT_FILES = getattr(settings, 'STATIFY_ROOT_FILES', os.path.join(settings.STATIC_ROOT, 'root'))
STATIFY_ROOT_FILES_URL = getattr(settings, 'STATIFY_ROOT_FILES_URL', settings.STATIC_URL + 'root/')
STATIFY_STATIC_DIR_NAME = 'statify_static'
