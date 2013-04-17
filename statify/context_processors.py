# -*- coding: utf-8 -*-
#

# Project imports
import settings


def statify_root_static_url(request):
    return { 'STATIFY_ROOT_STATIC_URL': settings.STATIFY_ROOT_STATIC_URL }
