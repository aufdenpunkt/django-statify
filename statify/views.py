# -*- coding: utf-8 -*-
#

# Core imports
import os
import tarfile
import shutil
import time
import requests
from subprocess import call

# 3rd party imports
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

# Project imports
from models import Release, ExternalURL


@login_required()
def make_release(request):
    from django.core.management import call_command
    import settings as app_settings

    timestamp = u'%s' % (time.time())
    htdocs = u'htdocs.%s.tar.gz' % (timestamp)
    upload_path = app_settings.STATIFY_UPLOAD_PATH
    absolute_path = os.path.join(settings.MEDIA_ROOT, app_settings.STATIFY_UPLOAD_PATH)
    external_url_list = ExternalURL.objects.filter(is_valid=True)
    static_root = app_settings.STATIFY_ROOT_STATIC

    release = Release(user=request.user, timestamp=timestamp)

    # If htdocs already exists, remove
    if os.path.isdir(settings.MEDUSA_DEPLOY_DIR):
        shutil.rmtree(settings.MEDUSA_DEPLOY_DIR, ignore_errors=True)
        os.makedirs(settings.MEDUSA_DEPLOY_DIR)
    else:
        os.makedirs(settings.MEDUSA_DEPLOY_DIR)

    # Call command to run medusa and statify all registered urls
    call(['python', 'manage.py', 'staticsitegen', '--settings=conf.build'])

    # Create files from external urls
    for external_url in external_url_list:
        path = os.path.join(settings.MEDUSA_DEPLOY_DIR, '/'.join(external_url.path[1:].split('/')[:-1]))
        filepath = os.path.join(settings.MEDUSA_DEPLOY_DIR, external_url.path[1:])

        # If path does not exists, create it
        if not os.path.isdir(path):
            os.makedirs(path)

        # If file extists, remove it (need to be sure the file is clean)
        if os.path.exists(filepath):
            os.remove(filepath)

        # Make request and get content
        r = requests.get(external_url.url)
        content = r.content

        # Write content to file and save
        filename = open(filepath, 'w+')
        filename.write(content)
        filename.close()

    # Call to collect all media to static
    call_command('collectstatic', interactive=False, ignore_patterns=app_settings.STATIFY_EXCLUDED_MEDIA,)

    # Copy static root files to release
    if os.path.isdir(static_root):
        root_files = os.listdir(static_root)
        for f in root_files:
            filepath = os.path.join(static_root, f)
            shutil.copy(filepath, settings.MEDUSA_DEPLOY_DIR)

    # Move media to builded htdocs
    shutil.move(os.path.join(app_settings.STATIFY_PROJECT_DIR, 'static'),
        os.path.join(settings.MEDUSA_DEPLOY_DIR, 'static'))
    shutil.rmtree(os.path.join(app_settings.STATIFY_PROJECT_DIR, 'static'),
        ignore_errors=True,)

    # Create tar.gz from htdocs and move it to media folder
    dirlist = os.listdir(settings.MEDUSA_DEPLOY_DIR)
    archive = tarfile.open(htdocs, 'w:gz')

    for obj in dirlist:
        path = os.path.join(settings.MEDUSA_DEPLOY_DIR, obj)
        archive.add(path, arcname=obj)
    archive.close()

    if not os.path.isdir(absolute_path):
        os.makedirs(absolute_path)

    shutil.move(os.path.join(settings.STATIFY_PROJECT_DIR, htdocs), os.path.join(absolute_path, htdocs))

    # Remove htdocs and tmp dir
    shutil.rmtree(settings.MEDUSA_DEPLOY_DIR, ignore_errors=True,)
    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'tmp'))

    # Update release object and save the model
    release.archive = u'%s%s' % (upload_path, htdocs)
    release.save()

    messages.success(request, _('Release %s has been created successfully.') % (release.date_created))

    return HttpResponseRedirect(u'/admin/statify/release/')


@login_required()
def deploy_select_release(request, release_id):
    from forms import DeployForm

    if request.POST:
        form = DeployForm(request.POST)

        if form.is_valid():
            form.cleaned_data
            host = request.POST['deploymenthost']

            return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/%s/' % (release_id, host))
    else:
        form = DeployForm()

    return render_to_response(
        'admin/statify/release/deploy_form.html',
        { 'form': form, 'release_id': release_id },
        context_instance=RequestContext(request))


@login_required()
def deploy_release(request, release_id, deploymenthost_id):
    import ftplib
    from paramiko import SSHClient, SFTPClient
    from models import DeploymentHost

    release = get_object_or_404(Release, pk=release_id)
    deploymenthost = get_object_or_404(DeploymentHost, pk=deploymenthost_id)
    archive = os.path.join(settings.MEDIA_ROOT, u'%s' % release.archive)
    directory = deploymenthost.path.split('/')[-1]
    tmp_path = os.path.join(settings.MEDUSA_DEPLOY_DIR, '..', 'deploy', release.timestamp)

    # Local deployment
    if deploymenthost.type is 0:
        if not os.path.isdir(deploymenthost.path):
            os.makedirs(deploymenthost.path)
        else:
            shutil.rmtree(deploymenthost.path, ignore_errors=True)
            os.makedirs(deploymenthost.path)
        call(['tar', 'xfvz', archive, '-C', deploymenthost.path])

    # FTP deployment
    elif deploymenthost.type is 1:
        # Check if host is available
        try:
            ftp = ftplib.FTP(deploymenthost.host)
        except:
            messages.error(request,
                _('Deployment host "%s" is not available.') % (deploymenthost.host))
            return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/select/' % (release.id))

        try:
            ftp.login(deploymenthost.user, deploymenthost.password)
        except:
            messages.error(request,
                _('Your login information to %s is not correct.') % (deploymenthost.host))
            return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/select/' % (release.id))

        # Check if directory exists
        filelist = []
        directory_exist = False
        ftp.retrlines('LIST', filelist.append)

        for f in filelist:
            if directory in f.split()[-1]:
                directory_exist = True

        # If not, mkdir it
        if not directory_exist:
            messages.error(request,
                _('The target path "%s" does not exist.') % (deploymenthost.path))
            return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/select/' % (release.id))

        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)
        else:
            shutil.rmtree(tmp_path, ignore_errors=True)
            os.makedirs(tmp_path)

        # Extract archive to temporaly path
        call(['tar', 'xzfv', archive, '-C', tmp_path])
        paths = os.listdir(tmp_path)

        # Upload all
        for path in paths:
            src_dir = os.path.join(tmp_path, path)
            call(['ncftpput', '-R',
                  '-u', deploymenthost.user, '-p', deploymenthost.password,
                  deploymenthost.host, deploymenthost.path,
                  src_dir])

        # Remove after upload is finished
        shutil.rmtree(tmp_path, ignore_errors=True)

    # SSH deployment
    elif deploymenthost.type is 2:
        # Check if host is available
        try:
            client = SSHClient()
            client.load_system_host_keys()
            client.connect(hostname=deploymenthost.host, username=deploymenthost.user)
            channel = client.get_transport()
            scp = SFTPClient.from_transport(channel)
        except:
            messages.error(request,
                _('Deployment host "%s" is not available.') % (deploymenthost.host))
            return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/select/' % (release.id))

        # Check if directory exists
        try:
            scp.stat(deploymenthost.path)
        except:
            messages.error(request,
                _('The target path "%s" does not exist.') % (deploymenthost.path))
            return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/select/' % (release.id))

        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)
        else:
            shutil.rmtree(tmp_path, ignore_errors=True)
            os.makedirs(tmp_path)

        call(['tar', 'xzfv', archive, '-C', tmp_path])
        paths = os.listdir(tmp_path)

        for path in paths:
            src_dir = os.path.join(tmp_path, path)
            call(['scp', '-r', src_dir, deploymenthost.path])

    # Remove trash
    shutil.rmtree(tmp_path, ignore_errors=True)
    shutil.rmtree(settings.MEDUSA_DEPLOY_DIR, ignore_errors=True)

    messages.success(request,
        _('Release "%s" was deployed successfully.') % (release.timestamp))

    return HttpResponseRedirect(u'/admin/statify/release/')
