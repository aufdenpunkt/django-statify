# -*- coding: utf-8 -*-
#

# 3rd party imports
from django.db import models
from django.contrib.auth.models import User

# Project imports
import settings


class Release(models.Model):
    user = models.ForeignKey(User, verbose_name=u'Benutzer')
    date_created = models.DateTimeField(u'Erstellt am', auto_now_add=True)
    timestamp = models.CharField(u'Timestamp', max_length=32)
    archive = models.FileField(u'Archiv', upload_to=settings.STATIFY_UPLOAD_PATH, blank=True)

    class Meta:
        app_label = u'statify'
        verbose_name = u'Release'
        verbose_name_plural = u'Releases'

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
        (0, u'Lokal'),
        (1, u'FTP'),
        (2, u'SSH'),
    )

    AUTHTYPE_CHOICES = (
        (0, u'Passwort'),
        (1, u'Public Key'),
    )

    title = models.CharField(u'Bezeichnung', max_length=100)
    url = models.URLField(u'URL', blank=True, help_text=u'URL to view the deployed result.')
    type = models.IntegerField(u'Typ', choices=TYPE_CHOICES)
    host = models.CharField(u'Server', max_length=80, blank=True, help_text=u'Bsp.: ssh.server.com')
    user = models.CharField(u'Benutzer', max_length=80, blank=True)
    path = models.CharField(u'Pfad', max_length=255, help_text=u'Bitte geben Sie das Zielverzeichnis an.')
    authtype = models.IntegerField(u'Authenticationtyp', choices=AUTHTYPE_CHOICES, blank=True, null=True)
    password = models.CharField(u'Password', max_length=80, blank=True)

    class Meta:
        app_label = u'statify'
        verbose_name = u'Deploymenthost'
        verbose_name_plural = u'Deploymenthosts'

    def __unicode__(self):
        return u'%s: %s' % (self.get_type_display(), self.title,)


class URL(models.Model):
    is_valid = models.BooleanField(u'Gültig', default=True)
    url = models.CharField(u'URL', max_length=255, default='/', unique=True)

    class Meta:
        app_label = u'statify'
        verbose_name = u'URL'
        verbose_name_plural = u'URLs'

    def __unicode__(self):
        return u'%s' % (self.url)


class ExternalURL(models.Model):
    is_valid = models.BooleanField(u'Gültig', default=True)
    url = models.URLField(u'URL')
    path = models.CharField(u'Zielpfad', max_length=255, unique=True, help_text=u'Bitte geben Sie den Zielpfad an, wo die Datei  werden soll.')

    class Meta:
        app_label = u'statify'
        verbose_name = u'External URL'
        verbose_name_plural = u'External URLs'

    def __unicode__(self):
        return u'%s' % (self.url)
