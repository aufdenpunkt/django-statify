# -*- coding: utf-8 -*-
#

# 3rd party imports
from django_medusa.renderers import StaticSiteRenderer

# Project imports
from models import URL


class UrlsRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = []
        urls = URL.objects.filter(is_valid=True)

        for url in urls:
            paths.append(url.url)

        return paths

renderers = [UrlsRenderer,]
