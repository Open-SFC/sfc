# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import forms
from horizon import messages
from horizon import exceptions
##from horizon.utils import fields

LOG = logging.getLogger(__name__)


class BaseImageForm(forms.SelfHandlingForm):

    def __init__(self, request, *args, **kwargs):
        super(BaseImageForm, self).__init__(request, *args, **kwargs)
        # Populate image choices
        chains = [('', _("Select Chain"))]
        tenant_id = self.request.user.tenant_id
        for chain in api.sfc.chain_list_for_tenant(request, tenant_id):
            chains.append((chain.id, chain.name))
        self.fields['chain_id'].choices = chains


class Editrule(BaseImageForm):
    chainset_id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(label=_("Name"),
                           widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    chain_id = forms.ChoiceField(label=_("Select Chain"), required=True)
    rule_id = forms.CharField(label=_("ID"),
                              widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:project:chainsets:index'

    def handle(self, request, data):
        try:
            rule = api.sfc.rule_modify(request, data['chainset_id'],
                                       data['rule_id'],
                                       name=data['name'],
                                       chain_id=data['chain_id'])
            msg = _('Chain %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return rule
        except:
            msg = _('Failed to update Rule %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)


class Launchchain(forms.SelfHandlingForm):
    chainset_id = forms.CharField(widget=forms.HiddenInput())
    rule_id = forms.CharField(widget=forms.HiddenInput())
    failure_url = 'horizon:project:chainsets:index'

    def handle(self, request, data):
        try:
            launch = api.sfc.launch_chain(request,
                                          chainset_id=data['chainset_id'],
                                          rule_id=data['rule_id'])
            msg = _('Chain %s was successfully Launched.') % data['rule_id']
            LOG.debug(msg)
            messages.success(request, msg)
            return launch
        except:
            msg = _('Failed to Launch Chain %s') % data['rule_id']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
