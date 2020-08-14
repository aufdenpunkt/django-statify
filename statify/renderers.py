# -*- coding: utf-8 -*-
#

# 3rd party imports
from django_medusa.renderers import DiskStaticSiteRenderer

# Project imports
from statify.models import URL


class UrlsRenderer(DiskStaticSiteRenderer):
    def get_paths(self):
        paths = []
        urls = URL.objects.filter(is_valid=True)
        for url in urls:
            paths.append(url.url)
        return paths

renderers = [UrlsRenderer,]
