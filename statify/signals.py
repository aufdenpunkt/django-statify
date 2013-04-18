# -*- coding: utf-8 -*-
#

# 3rd party imports
from django.db.models.signals import post_save, post_delete

# Project imports
from models import URL


EXCLUDED_MODELS = (
    u'Session',
    u'Group',
    u'User',
    u'LogEntry',
    u'Release',
    u'DeploymentHost',
    u'URL',
    u'ExternalURL',
)


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

    model = sender.__name__

    if not model in EXCLUDED_MODELS:
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


def delete_handler(sender, **kwargs):
    model = sender.__name__

    if not model in EXCLUDED_MODELS:
        try:
            urls = kwargs.get('instance').statify_urls()
            for url in urls:
                try:
                    URL.objects.get(url=url).delete()
                except:
                    pass
        except:
            pass

        try:
            url = kwargs.get('instance').statify_url()
            URL.objects.get(url=url).delete()
        except:
            pass

post_delete.connect(delete_handler)
