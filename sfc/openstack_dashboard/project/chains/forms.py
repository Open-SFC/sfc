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
from horizon import exceptions
from horizon import forms
from horizon import messages

LOG = logging.getLogger(__name__)


class CreateChain(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    auto_boot = forms.BooleanField(label=_("Auto Boot "),
                                   initial=False, required=False)

    def handle(self, request, data):
        try:
            sg = api.sfc.chain_create(request,
                                      name=data['name'],
                                      auto_boot=data['auto_boot'])

            messages.success(request,
                             _('Successfully created Chain: %s')
                             % data['name'])
            return sg
        except:
            redirect = reverse("horizon:project:chains:index")
            exceptions.handle(request,
                              _('Unable to create Chain.'),
                              redirect=redirect)


class UpdateChain(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    tenant_id = forms.CharField(widget=forms.HiddenInput)
    chain_id = forms.CharField(label=_("ID"),
                               widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:project:chains:index'

    def handle(self, request, data):
        try:
            chain = api.sfc.chain_modify(request, data['chain_id'],
                                         name=data['name'])
            msg = _('Chain %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return chain
        except:
            msg = _('Failed to update chain %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
