# -*- coding: utf-8 -*-
#

# 3rd party imports
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

# Project imports
import settings


class Release(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'))
    date_created = models.DateTimeField(_('Created on'), auto_now_add=True)
    timestamp = models.CharField(_('Timestamp'), max_length=32)
    archive = models.FileField(_('Archive'), upload_to=settings.STATIFY_UPLOAD_PATH, blank=True)

    class Meta:
        app_label = _('statify')
        verbose_name = _('Release')
        verbose_name_plural = _('Releases')

    def __unicode__(self):
        return u'%s' % (self.date_created)

    def delete(self, *args, **kwargs):
        try:
            storage, path = self.archive.storage, self.archive.path
        except:
            pass

        super(Release, self).delete(*args, **kwargs)

        try:
            storage.delete(path)
        except:
            pass


class DeploymentHost(models.Model):
    TYPE_CHOICES = (
        (0, _('Local')),
        (1, _('FTP')),
        (2, _('SSH')),
    )

    AUTHTYPE_CHOICES = (
        (0, _('Password')),
        (1, _('Public Key')),
    )

    title = models.CharField(_('Title'), max_length=100)
    url = models.URLField(_('URL'), blank=True, help_text=_('URL to view the deployed result.'))
    type = models.IntegerField(_('Type'), choices=TYPE_CHOICES)
    host = models.CharField(_('Host'), max_length=80, blank=True, help_text=_('E.g. ssh.server.com'))
    user = models.CharField(_('User'), max_length=80, blank=True)
    path = models.CharField(_('Path'), max_length=255, help_text=u'Please specify the target directory.')
    authtype = models.IntegerField(_('Authentication type'), choices=AUTHTYPE_CHOICES, blank=True, null=True)
    password = models.CharField(_('Password'), max_length=80, blank=True)

    class Meta:
        app_label = u'statify'
        verbose_name = _('Deployment host')
        verbose_name_plural = _('Deployment hosts')

    def __unicode__(self):
        return u'%s: %s' % (self.get_type_display(), self.title,)


class URL(models.Model):
    is_valid = models.BooleanField(_('Valid'), default=True)
    url = models.CharField(_('URL'), max_length=255, default='/', unique=True)

    class Meta:
        app_label = u'statify'
        verbose_name = _('URL')
        verbose_name_plural = _('URLs')

    def __unicode__(self):
        return u'%s' % (self.url)


class ExternalURL(models.Model):
    is_valid = models.BooleanField(_('Valid'), default=True)
    url = models.URLField(_('URL'))
    path = models.CharField(_('Path'), max_length=255, unique=True, help_text=_('Please specify the target directory.'))

    class Meta:
        app_label = u'statify'
        verbose_name = _('External URL')
        verbose_name_plural = _('External URLs')

    def __unicode__(self):
        return u'%s' % (self.url)
