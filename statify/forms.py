# -*- coding: utf-8 -*-

# 3rd party imports
from django import forms

# Project imports
from statify.models import DeploymentHost


class DeployForm(forms.Form):
    deploymenthost = forms.ModelChoiceField(queryset=DeploymentHost.objects.all(), label='Host', required=True)
