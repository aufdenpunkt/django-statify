# -*- coding: utf-8 -*-

from django.apps import AppConfig

class StatifyConfig(AppConfig):
    name = 'statify'
    verbose_name = 'Statify'

    def ready(self):
        from . import signals
