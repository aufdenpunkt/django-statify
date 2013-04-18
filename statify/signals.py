# -*- coding: utf-8 -*-
#

# 3rd party imports
from django.db.models.signals import post_save

# Project imports
from models import URL


def save_handler(sender, **kwargs):
    '''
    Example class methods:

    Use the following example method for multiple urls:
    def statify_urls(self):
        url_list = list()
        url_list.append('/%s/' % self.locale)

        return url_list

    Use the following example method for a single url:
    def statify_url(self):
        return u'/%s/' % self.locale
    '''

    excluded_models = (
        u'Session',
        u'Group',
        u'User',
        u'LogEntry',
        u'Release',
        u'DeploymentHost',
        u'URL',
        u'ExternalURL',
    )
    model = sender.__name__

    if not model in excluded_models:
        try:
            urls = kwargs.get('instance').statify_urls()
            for url in urls:
                try:
                    URL(url=url).save()
                except:
                    pass
        except:
            pass

        try:
            url = kwargs.get('instance').statify_url()
            URL(url=url).save()
        except:
            pass

post_save.connect(save_handler)
