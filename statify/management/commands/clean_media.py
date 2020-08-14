# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Remove empty directories in media directory'

    def handle(self, *args, **options):
        removed_dirs = []
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for d in dirs:
                dir = os.path.join(root, d)
                if not os.listdir(dir):
                    self.stdout.write(self.style.NOTICE('Remove {}'.format(dir)))
                    os.rmdir(dir)
                    removed_dirs.append(dir)
        self.stdout.write(self.style.SUCCESS('Successfully removed {} directories'.format(len(removed_dirs))))
