# -*- coding: utf-8 -*-

import tarfile
from cms.models import Title
from cms.utils import get_current_site
from cms.utils.i18n import get_public_languages
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.sites.models import Site
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.defaultfilters import filesizeformat
from django.urls import path, reverse
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

# Project imports
from statify.models import URL, DeploymentHost, ExternalURL, Release
from statify.utils import url_is_valid
from statify.views import deploy_release, deploy_select_release, make_release
from statify.forms import DeploymentHostForm

# Global variables
CURRENT_SITE = Site.objects.get_current()

def delete_releases(modeladmin, request, queryset):
    for release in queryset:
        release.delete()
    messages.success(request, _('Selected Releases were deleted successfully.'))
delete_releases.short_description = _("Delete selected releases.")

class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'timestamp', 'user', 'archive_size', 'download', 'deploy',)
    list_filter = ('date_created', 'user',)
    ordering = ('-date_created',)
    exclude = ('user',)
    readonly_fields = ('user', 'timestamp', 'date_created', 'archive',)
    actions = (delete_releases,)
    change_form_template = 'admin/statify/release/change_form.html'

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        additional_urls = [
            path('make/', self.admin_site.admin_view(make_release), name='statify_release_make_release'),
            path('<int:release_id>/deploy/select/', self.admin_site.admin_view(deploy_select_release), name='statify_release_deploy_select_release'),
            path('<int:release_id>/deploy/<int:deploymenthost_id>/', self.admin_site.admin_view(deploy_release), name='statify_release_deploy_release'),
        ]
        return additional_urls + urls

    @mark_safe
    def download(self, instance):
        return '<a href="{}">{}</a>'.format(
            instance.archive.url,
            _('Download')
        )
    download.short_description = _('Archive')
    download.allow_tags = True

    @mark_safe
    def deploy(self, instance):
        return '<a href="{}">{}</a>'.format(
            reverse('admin:statify_release_deploy_select_release', args=(instance.pk,)),
            _('Deploy')
        )
    deploy.short_description = _('Deployment')
    deploy.allow_tags = True

    def archive_size(self, instance):
        return filesizeformat(instance.archive.size)
    archive_size.short_description = _('Archive size')

    # Remove default query delete
    def get_actions(self, request):
        actions = super(ReleaseAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def change_view(self, request, object_id, form_url='', extra_context=None):
        release = Release.objects.get(pk=object_id)
        tar = tarfile.open(release.archive.path)
        files = [file.path for file in tar.getmembers() if file.isfile()]
        extra_context = extra_context or {}
        extra_context['files'] = files
        return super(ReleaseAdmin, self).change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

admin.site.register(Release, ReleaseAdmin)


class DeploymentHostAdmin(admin.ModelAdmin):
    list_display = ('_title', 'server', 'path', 'target')
    list_filter = ('type',)
    form = DeploymentHostForm
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'type',
                # 'url',
            ),
        }),
        (_('Target'), {
            'fields': (
                'target_scheme',
                'target_domain',
            ),
            'description': '<div class="help">{}</div>'.format(
                _('Will be used to replace domains including schemes (e.g. https://cms.example.com will become https://www.example.com)')
            ),
        }),
        (_('Server settings'), {
            'fields': (
                'host',
            ),
        }),
        (_('Authentication'), {
            'fields': (
                'user',
                'authtype',
                'password',
                'ssh_key_path',
            ),
            # 'classes': ('wide',)
        }),
        (_('Path'), {
            'fields': (
                'path',
                'chown',
                'chmod',
            )
        })
    )

    def _title(self, instance):
        return '{}: {}'.format(instance.get_type_display(), instance.title)

    def target(self, instance):
        url = '{}://{}'.format(instance.target_scheme, instance.target_domain)
        return mark_safe('<a href="{}" target="_blank">{}</a>'.format(url, url))
    target.short_description = _('Target')
    target.allow_tags = True

    def server(self, instance):
        if instance.type == 0:
            return None
        if instance.user:
            user = instance.masked_user + '@'
        else:
            user = ''
        return '{}{}'.format(user, instance.host)
    server.short_description = _('Server')

admin.site.register(DeploymentHost, DeploymentHostAdmin)


class URLForm(forms.ModelForm):
    class Meta:
        model = URL
        fields = '__all__'

    def clean(self):
        # Check if url is entered
        if not 'url' in self.cleaned_data or self.cleaned_data['url'] == '':
            raise forms.ValidationError(_('The URL field must be filled.'))

        cleaned_url = self.cleaned_data['url']
        url = u'http://%s%s' % (CURRENT_SITE, cleaned_url)

        # Check if url is entered
        if len(URL.objects.filter(url=cleaned_url).exclude(pk=self.instance.pk)) > 0:
            raise forms.ValidationError(_('The URL you entered already exists.'))

        # Check if url starts with a slash
        if not cleaned_url.startswith('/'):
            raise forms.ValidationError(_('The URL you entered must begin with "/".'))

        # Check if url exists and
        if url_is_valid(url):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_('Please enter a valid URL. The URL %s is not available.') % (url))


def validate_urls(modeladmin, request, queryset):
    for u in queryset:
        url = u'http://%s%s' % (CURRENT_SITE, u)
        if url_is_valid(url):
            u.is_valid = True
        else:
            u.is_valid = False
        u.save()
validate_urls.short_description = _('Check selected URLs')


class URLAdmin(admin.ModelAdmin):
    exclude = ('is_valid',)
    list_display = ('url', 'date_added', 'is_valid', 'preview_url',)
    list_filter = ('is_valid', 'date_added')
    actions = [validate_urls]
    readonly_fields = ('date_added', 'date_modified')
    ordering = ('url',)

    @mark_safe
    def preview_url(self, instance):
        return '<a href="//{}" target="_blank" rel="nofollow">{}</a>'.format(
            CURRENT_SITE.domain + instance.url,
            _('Preview')
        )
    preview_url.short_description = _('Preview')
    preview_url.allow_tags = True

    def _get_cms_titles(self):
        languages = get_public_languages(site_id=CURRENT_SITE.pk)
        items = Title.objects.public().filter(
            Q(redirect='') | Q(redirect__isnull=True),
            language__in=languages,
            page__login_required=False,
            page__node__site=CURRENT_SITE,
        ).order_by('page__node__path')
        return items

    def crawl_cms_urls(self, request):
        if settings.STATIFY_USE_CMS and 'cms' in settings.INSTALLED_APPS:
            existing_urls = URL.objects.all().values_list('url', flat=True)
            titles = self._get_cms_titles()
            scheme = request.is_secure() and 'https' or 'http'
            for title in titles:
                translation.activate(title.language)
                url = title.page.get_absolute_url(title.language)
                absolute_url = '%s://%s%s' % (scheme, CURRENT_SITE, url)
                translation.deactivate()
                if not url_is_valid(absolute_url) or url in existing_urls:
                    continue
                URL(url=url, is_valid=True).save()
        return HttpResponseRedirect(reverse('admin:statify_url_changelist'))

    def get_urls(self):
        urls = super().get_urls()
        additional_urls = [
            path('crawl-cms-urls/', self.crawl_cms_urls, name='statify_url_crawl_cms_urls'),
        ]
        return additional_urls + urls

admin.site.register(URL, URLAdmin)


def validate_external_urls(modeladmin, request, queryset):
    for u in queryset:
        if url_is_valid(u.url):
            u.is_valid = True
        else:
            u.is_valid = False
        u.save()
validate_external_urls.short_description = _('Check selected external URLs')


class ExternalURLForm(forms.ModelForm):
    class Meta:
        model = ExternalURL
        fields = '__all__'

    def clean(self):
        # Check if url is entered
        if not 'url' in self.cleaned_data or self.cleaned_data['url'] == '':
            raise forms.ValidationError(_('The URL field must be filled.'))

        cleaned_url = self.cleaned_data['url']
        url = u'%s' % (cleaned_url)

        # Check if url already exists
        if len(URL.objects.filter(url=cleaned_url).exclude(pk=self.instance.pk)) > 0:
            raise forms.ValidationError(_('The URL you entered already exists.'))

        # Check if url exists and
        if url_is_valid(url):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_('Please enter a valid URL. The URL %s is not available.') % (url))


class ExternalURLAdmin(admin.ModelAdmin):
    exclude = ('is_valid',)
    list_display = ('url', 'path', 'is_valid', 'preview_url',)
    list_filter = ('is_valid',)
    form = ExternalURLForm
    actions = [validate_external_urls]

    def preview_url(self, instance):
        return '<a href="{}" target="_blank" rel="nofollow">{}</a>'.format(
            instance.url,
            _('Preview')
        )
    preview_url.short_description = u''
    preview_url.allow_tags = True

admin.site.register(ExternalURL, ExternalURLAdmin)
