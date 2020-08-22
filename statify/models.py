# -*- coding: utf-8 -*-
#

# 3rd party imports
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _

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


class DeploymentHost(models.Model):
    TYPE_CHOICES = (
        (0, _('Local')),
        (1, _('FTP')),
        (2, _('SSH')),
    )

    AUTHTYPE_CHOICES = (
        (0, _('Password')),
        (1, _('Key')),
    )

    SCHEME_CHOICES = (
        ('http', 'http'),
        ('https', 'https'),
    )

    title = models.CharField(_('Title'), max_length=100)
    target_scheme = models.CharField(_('Target scheme'), max_length=255, choices=SCHEME_CHOICES)
    target_domain = models.CharField(_('Target domain'), max_length=255, help_text=_('e.g. www.example.com'))
    url = models.URLField(_('URL'), blank=True, help_text=_('URL to view the deployed result.'))
    type = models.IntegerField(_('Type'), choices=TYPE_CHOICES)
    host = models.CharField(_('Host'), max_length=80, blank=True, null=True, help_text=_('e.g. ssh.server.com'))
    chmod = models.CharField(_('chmod'), max_length=80, blank=True, null=True, help_text=_('e.g. u-rwx,o+rwx'))
    chown = models.CharField(_('chown'), max_length=80, blank=True, null=True, help_text=_('e.g. www-data:www-data'))
    user = models.CharField(_('User'), max_length=80, blank=True, null=True)
    path = models.CharField(_('Path'), max_length=255, help_text=u'Please specify the target directory.')
    authtype = models.IntegerField(_('Authentication type'), choices=AUTHTYPE_CHOICES, blank=True, null=True)
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
