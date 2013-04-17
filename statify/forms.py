# -*- coding: utf-8 -*-
#

# 3rd party imports
from django import forms

# Project imports
from models import DeploymentHost


class DeployForm(forms.Form):
    deploymenthost = forms.ModelChoiceField(queryset=DeploymentHost.objects.all(), label=u'Host', required=True)
