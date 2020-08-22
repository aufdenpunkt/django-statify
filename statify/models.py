# -*- coding: utf-8 -*-
#
import re

# 3rd party imports
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _
from django.http.request import host_validation_re

# Project imports
from statify import settings


class Release(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'), null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(_('Created on'), auto_now_add=True)
    timestamp = models.CharField(_('Timestamp'), max_length=32)
    archive = models.FileField(_('Archive'), upload_to=settings.STATIFY_UPLOAD_PATH, blank=True)

    class Meta:
        app_label = _('statify')
        verbose_name = _('Release')
        verbose_name_plural = _('Releases')

    def __unicode__(self):
        return u'%s' % (self.date_created)

    def __str__(self):
        return '%s' % (self.date_created)

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

class DeploymentTypes(models.IntegerChoices):
    LOCAL = 0, _('Local')
    FTP = 1, _('FTP')
    SSH = 2, _('SSH')

class Schemes(models.TextChoices):
    HTTP = 'http', 'http'
    HTTPS = 'https', 'https'

class AuthTypes(models.IntegerChoices):
    PASSWORD = 0, _('Password')
    KEY = 1, _('Key')

class DeploymentHost(models.Model):
    title = models.CharField(_('Title'), max_length=100)
    target_scheme = models.CharField(_('Target scheme'), max_length=255, choices=Schemes.choices, default=Schemes.HTTP)
    target_domain = models.CharField(
        _('Target domain'),
        max_length=255,
        help_text=_('e.g. www.example.com'),
        validators=[
            RegexValidator(host_validation_re, _('The domain name provided is not valid according to RFC 1034/1035.'))
        ]
    )
    type = models.IntegerField(_('Type'), choices=DeploymentTypes.choices)
    host = models.CharField(_('Host'), max_length=80, blank=True, null=True, help_text=_('e.g. ssh.server.com'))
    chmod = models.CharField(_('chmod'), max_length=80, blank=True, null=True, help_text=_('e.g. u-rwx,o+rwx'))
    chown = models.CharField(_('chown'), max_length=80, blank=True, null=True, help_text=_('e.g. www-data:www-data'))
    user = models.CharField(_('User'), max_length=80, blank=True, null=True)
    path = models.CharField(_('Path'), max_length=255, help_text=u'Please specify the target directory.')
    authtype = models.IntegerField(_('Authentication type'), choices=AuthTypes.choices, blank=True, null=True)
    password = models.CharField(_('Password'), max_length=255, blank=True, null=True)
    ssh_key_path = models.CharField(_('SSH key path'), max_length=255, blank=True, null=True, help_text=_('e.g. /home/user/.ssh/id_rsa'))

    class Meta:
        app_label = u'statify'
        verbose_name = _('Deployment host')
        verbose_name_plural = _('Deployment hosts')

    def __unicode__(self):
        return u'%s: %s' % (self.get_type_display(), self.title,)

    def __str__(self):
        return '%s: %s' % (self.get_type_display(), self.title,)

    @property
    def masked_user(self):
        if not self.user:
            return None
        return re.sub(r'(?<!^).(?!$)', '*', self.user)


class URL(models.Model):
    is_valid = models.BooleanField(
        _('Valid'),
        default=False,
    )
    url = models.CharField(
        _('URL'),
        max_length=255,
        unique=True,
        validators=[RegexValidator('(^\/[A-Za-z0-9\-\_\%\?\&\=]+)', _('URL must start with a leading slash (e.g. /en/)'))],
    )
    date_added = models.DateTimeField(
        _('Date added'),
        auto_now_add=True
    )
    date_modified = models.DateTimeField(
        _('Date modified'),
        auto_now=True
    )

    class Meta:
        app_label = u'statify'
        verbose_name = _('URL')
        verbose_name_plural = _('URLs')

    def __unicode__(self):
        return u'%s' % (self.url)

    def __str__(self):
        return self.url


class ExternalURL(models.Model):
    is_valid = models.BooleanField(_('Valid'), default=True)
    url = models.URLField(_('URL'))
    path = models.CharField(_('Target path'), max_length=255, unique=True, help_text=_('Please specify the target path.'))

    class Meta:
        app_label = u'statify'
        verbose_name = _('External URL')
        verbose_name_plural = _('External URLs')

    def __unicode__(self):
        return u'%s' % (self.url)
