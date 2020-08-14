# -*- coding: utf-8 -*-
#

# Project imports
from statify import settings


def statify_root_static_url(request):
    return { 'STATIFY_ROOT_FILES_URL': settings.STATIFY_ROOT_FILES_URL }
