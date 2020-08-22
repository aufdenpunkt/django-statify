# -*- coding: utf-8 -*-
#

import ftplib
import os
import re
import shutil
import tarfile
import time
from pathlib import Path
from subprocess import call

import paramiko
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.urls import reverse
from django.utils.translation import ugettext as _

import statify.settings as statify_settings
from statify.forms import DeployForm
from statify.models import DeploymentHost, ExternalURL, Release


CURRENT_SITE = Site.objects.get_current()


@login_required()
def make_release(request):
    from django.core.management import call_command

    timestamp = '%s' % (time.time())
    htdocs = 'htdocs.%s.tar.gz' % (timestamp)
    upload_path = statify_settings.STATIFY_UPLOAD_PATH
    absolute_path = os.path.join(settings.MEDIA_ROOT, statify_settings.STATIFY_UPLOAD_PATH)
    external_url_list = ExternalURL.objects.filter(is_valid=True)

    # If htdocs already exists, remove
    if os.path.isdir(settings.MEDUSA_DEPLOY_DIR):
        shutil.rmtree(settings.MEDUSA_DEPLOY_DIR, ignore_errors=True)
        os.makedirs(settings.MEDUSA_DEPLOY_DIR)
    else:
        os.makedirs(settings.MEDUSA_DEPLOY_DIR)

    version_file = open(os.path.join(settings.MEDUSA_DEPLOY_DIR, 'version.txt'), 'w')
    version_file.write(str(timestamp))
    version_file.close()

    # Call command to run medusa and statify all registered urls
    call([
        'python',
        'manage.py',
        'staticsitegen',
        statify_settings.STATIFY_BUILD_SETTINGS
    ])

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

    # Copy root files to builded htdocs
    if os.path.isdir(statify_settings.STATIFY_ROOT_FILES):
        files = os.listdir(statify_settings.STATIFY_ROOT_FILES)
        for file in files:
            filepath = os.path.join(statify_settings.STATIFY_ROOT_FILES, file)
            shutil.copy(filepath, settings.MEDUSA_DEPLOY_DIR)

    # Copy static files to builded htdocs
    if not statify_settings.STATIFY_IGNORE_STATIC:
        shutil.copytree(
            os.path.join(statify_settings.STATIFY_PROJECT_DIR, 'static'),
            os.path.join(settings.MEDUSA_DEPLOY_DIR, 'static'),
            ignore=shutil.ignore_patterns(*statify_settings.STATIFY_EXCLUDED_STATIC),
            dirs_exist_ok=True,
        )

    # Copy media files to builded htdocs
    if not statify_settings.STATIFY_IGNORE_MEDIA:
        shutil.copytree(
            os.path.join(settings.STATIFY_PROJECT_DIR, 'media'),
            os.path.join(settings.MEDUSA_DEPLOY_DIR, 'media'),
            ignore=shutil.ignore_patterns('statify'),
            dirs_exist_ok=True,
        )

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
    # shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'tmp'))

    # Save new release object
    release = Release(user=request.user, timestamp=timestamp)
    release.archive = u'%s%s' % (upload_path, htdocs)
    release.save()
    messages.success(request, _('Release %s has been created successfully.') % (release.date_created))
    return HttpResponseRedirect(reverse('admin:statify_release_change', args=(release.pk,)))


@login_required()
def deploy_select_release(request, release_id):
    if request.POST:
        form = DeployForm(request.POST)
        if form.is_valid():
            form.cleaned_data
            host = request.POST['deploymenthost']
            return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/%s/' % (release_id, host))
    else:
        form = DeployForm()

    return render(
        request=request,
        template_name = 'admin/statify/release/deploy_form.html',
        context = {
            'form': form,
            'release_id': release_id
        }
    )


@login_required()
def deploy_release(request, release_id, deploymenthost_id):
    release = get_object_or_404(Release, pk=release_id)
    deploymenthost = get_object_or_404(DeploymentHost, pk=deploymenthost_id)
    archive = os.path.join(settings.MEDIA_ROOT, u'%s' % release.archive)
    directory = deploymenthost.path.split('/')[-1]
    tmp_path = os.path.join(settings.MEDUSA_DEPLOY_DIR, '..', 'deploy', release.timestamp)

    if not os.path.isdir(tmp_path):
        os.makedirs(tmp_path)
    else:
        shutil.rmtree(tmp_path, ignore_errors=True)
        os.makedirs(tmp_path)
    call(['tar', 'xfz', archive, '-C', tmp_path])

    # Replace hostnames
    path_of_tmp_path = Path(tmp_path)
    html_files = [item for item in path_of_tmp_path.glob('**/*.html') if item.is_file()]
    xml_files = [item for item in path_of_tmp_path.glob('**/*.xml') if item.is_file()]
    json_files = [item for item in path_of_tmp_path.glob('**/*.json') if item.is_file()]
    css_files = [item for item in path_of_tmp_path.glob('**/*.css') if item.is_file()]
    txt_files = [item for item in path_of_tmp_path.glob('**/*.txt') if item.is_file()]
    all_files = html_files + xml_files + json_files + css_files + txt_files
    for file in all_files:
        fin = open(file, "rt")
        data = fin.read()
        data = re.sub(r'(http|https):\/\/({})'.format(CURRENT_SITE.domain), '{}://{}'.format(deploymenthost.target_scheme, deploymenthost.target_domain), data)
        data = re.sub(r'{}'.format(CURRENT_SITE.domain), deploymenthost.target_domain, data)
        fin.close()
        fin = open(file, "wt")
        fin.write(data)
        fin.close()

    # Local deployment
    if deploymenthost.type == 0:
        if not os.path.isdir(deploymenthost.path):
            os.makedirs(deploymenthost.path)
        else:
            shutil.rmtree(deploymenthost.path, ignore_errors=True)
            os.makedirs(deploymenthost.path)
        files = os.listdir(tmp_path)
        for file in files:
            shutil.move(os.path.join(tmp_path, file), deploymenthost.path)

    # FTP deployment
    elif deploymenthost.type == 1:
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

        # Upload all
        paths = os.listdir(tmp_path)
        for path in paths:
            src_dir = os.path.join(tmp_path, path)
            call(['ncftpput', '-R',
                  '-u', deploymenthost.user, '-p', deploymenthost.password,
                  deploymenthost.host, deploymenthost.path,
                  src_dir])

        # Remove after upload is finished
        shutil.rmtree(tmp_path, ignore_errors=True)

    # SSH deployment
    elif deploymenthost.type == 2:
        # Check if host is available
        # try:
        # client = paramiko.SSHClient()
        # client.load_system_host_keys()
        # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # key = paramiko.RSAKey.from_private_key_file("path", password='xxx')
        # client.connect(
        #     hostname=deploymenthost.host,
        #     username=deploymenthost.user,
        #     pkey=key
        # )
        # channel = client.get_transport()
        # scp = paramiko.SFTPClient.from_transport(channel)
        # # except:
        #     # messages.error(request,
        #     #     _('Deployment host "%s" is not available.') % (deploymenthost.host))
        #     # return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/select/' % (release.id))

        # # Check if directory exists
        # try:
        #     scp.stat(deploymenthost.path)
        # except:
        #     messages.error(request,
        #         _('The target path "%s" does not exist.') % (deploymenthost.path))
        #     return HttpResponseRedirect(u'/admin/statify/release/%s/deploy/select/' % (release.id))

        src = tmp_path + '/'
        destination = '{}@{}:{}'.format(deploymenthost.user, deploymenthost.host, deploymenthost.path)
        rsync_args = ['rsync', '-av', '--update', '--delete']
        if deploymenthost.ssh_key_path:
            rsync_args.append('-e "ssh -i {}"'.format(deploymenthost.ssh_key_path))
        if deploymenthost.chmod:
            rsync_args.append('--chmod={}'.format(deploymenthost.chmod))
        if deploymenthost.chown:
            owner = deploymenthost.chown.split(':')[0]
            group = deploymenthost.chown.split(':')[1]
            rsync_args.append('--usermap=*:{}'.format(owner))
            rsync_args.append('--groupmap=*:{}'.format(group))
        rsync_command = rsync_args + [src, destination]
        call(rsync_command)

    # Remove trash
    shutil.rmtree(tmp_path, ignore_errors=True)
    shutil.rmtree(settings.MEDUSA_DEPLOY_DIR, ignore_errors=True)

    messages.success(request,
        _('Release "%s" was deployed successfully.') % (release.timestamp))

    return HttpResponseRedirect(u'/admin/statify/release/')
