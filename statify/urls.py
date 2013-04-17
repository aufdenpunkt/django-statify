# -*- coding: utf-8 -*-
#

# 3rd party imports
from django.conf.urls import patterns, url


urlpatterns = patterns('statify.views',
    # Admin URLs
    url(r'^admin/statify/release/make/$', 'make_release', name='statify_release_make_release'),
    url(r'^admin/statify/release/(?P<release_id>\d+)/deploy/(?P<deploymenthost_id>\d+)/$', 'deploy_release', name='statify_release_deploy_release'),
    url(r'^admin/statify/release/(?P<release_id>\d+)/deploy/select/$', 'deploy_select_release', name='statify_release_deploy_select_release'),
)
