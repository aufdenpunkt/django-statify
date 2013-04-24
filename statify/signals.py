# -*- coding: utf-8 -*-
#

# 3rd party imports
from django.db.models.signals import post_save, post_delete
from django.contrib.sites.models import Site

# Project imports
from models import URL
from utils import url_is_valid
import settings as statify_settings


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

    current_site = Site.objects.get_current()
    model = sender.__name__

    # If the project is using django-cms
    # Add URL from translation on save
    if statify_settings.STATIFY_USE_CMS and model is 'Title':
        instance = kwargs.get('instance')

        if not instance.page.is_home():
            absolute_url = u'/%s/%s/' % (instance.language, instance.path)
        else:
            absolute_url = u'/%s/' % (instance.language)

        if url_is_valid(u'http://%s%s' % (current_site, absolute_url)):
            try:
                URL(url=absolute_url).save()
            except:
                pass


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

    # If the project is using django-cms
    # Delete URL from translation
    if statify_settings.STATIFY_USE_CMS and model is 'Title':
        instance = kwargs.get('instance')

        if instance.path:
            absolute_url = u'/%s/%s/' % (instance.language, instance.path)
        else:
            absolute_url = u'/%s/' % (instance.language)

        try:
            URL.objects.get(url=absolute_url).delete()
        except:
            pass


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
