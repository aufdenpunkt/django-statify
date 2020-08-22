# -*- coding: utf-8 -*-

# 3rd party imports
from django import forms
from django.utils.translation import ugettext as _

# Project imports
from statify.models import DeploymentHost


class DeployForm(forms.Form):
    deploymenthost = forms.ModelChoiceField(queryset=DeploymentHost.objects.all(), label='Host', required=True)


class DeploymentHostForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = DeploymentHost
        fields = '__all__'
        labels = {
            'target_scheme': _('Scheme'),
            'target_domain': _('Domain'),
        }
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }
