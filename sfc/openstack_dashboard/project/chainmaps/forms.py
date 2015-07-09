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


class BaseNetworkForm(forms.SelfHandlingForm):

    def __init__(self, request, *args, **kwargs):
        super(BaseNetworkForm, self).__init__(request, *args, **kwargs)
        # Populate Categoryfunctions choices
        networks = []
        tenant_id = self.request.user.tenant_id
        chainmaps = api.sfc.chainmap_list(request)
        for network in api.neutron.network_list_for_tenant(request, tenant_id):
            net_found = False
            for chmap in chainmaps:
                if chmap.inbound_network_id == network.id:
                    net_found = True
                    break
            if not net_found:
                networks.append((network.id, network.name))
        self.fields['inbound_network_id'].choices = networks

        chainsets = []
        for chainset in api.sfc.chainset_list_for_tenant(request, tenant_id):
            chainsets.append((chainset.id, chainset.name))
        self.fields['chainset_id'].choices = chainsets


class CreateChainmap(BaseNetworkForm):
    name = forms.CharField(label=_("Name"))
    inbound_network_id = forms.ChoiceField(label=_("Network"))
    chainset_id = forms.ChoiceField(label=_("Chainset"))

    def handle(self, request, data):
        try:
            sg = api.sfc.chainmap_create(request,
                                         name=data['name'],
                                         inbound_network_id=data[
                                             'inbound_network_id'],
                                         chainset_id=data['chainset_id'])

            messages.success(request,
                             _('Successfully created Chain Map: %s')
                             % data['name'])
            return sg
        except:
            redirect = reverse("horizon:project:chainmaps:index")
            exceptions.handle(request,
                              _('Unable to create Chain Map.'),
                              redirect=redirect)


class UpdateChainmap(BaseNetworkForm):
    name = forms.CharField(label=_("Name"),
                           widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    inbound_network_id = forms.ChoiceField(label=_("Inbound Network"))
    chainset_id = forms.ChoiceField(label=_("Chainset"))
    chainmap_id = forms.CharField(label=_("ID"),
                                  widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))

    failure_url = 'horizon:project:chainmaps:index'

    def handle(self, request, data):
        try:
            chain = api.sfc.chainmap_modify(request, data['chainmap_id'],
                                            name=data['name'],
                                            inbound_network_id=data[
                                                'inbound_network_id'],
                                            chainset_id=data['chainset_id'])
            msg = _('Chain %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return chain
        except:
            msg = _('Failed to update chainmap %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)


class BaseRulesForm(forms.SelfHandlingForm):

    def __init__(self, request, *args, **kwargs):
        super(BaseRulesForm, self).__init__(request, *args, **kwargs)
        sel_rules = [('', _("Select Selection Rule"))]
        tenant_id = self.request.user.tenant_id
        chainset_id = kwargs['initial']['chainset_id']
        rules = api.sfc.rule_list(request, chainset_id)
        for rule in rules:
            sel_rules.append((rule.id, rule.name))
        self.fields['rule_id'].choices = sel_rules


class Launchchain(BaseRulesForm):
    chainset_id = forms.CharField(widget=forms.HiddenInput())
    chainmap_id = forms.CharField(widget=forms.HiddenInput())
    rule_id = forms.ChoiceField(label=_("Select Rule"), required=True)
    failure_url = 'horizon:project:chainmaps:index'

    def handle(self, request, data):
        try:
            launch = api.sfc.launch_chain(request,
                                            chainset_id=data['chainset_id'],
                                            chainmap_id=data['chainmap_id'],
                                            rule_id=data['rule_id'])
            msg = _(
                'Chain Map %s was successfully Launched.') % data['chainmap_id']
            LOG.debug(msg)
            messages.success(request, msg)
            return launch
        except:
            msg = _('Failed to Launch Chain Map %s') % data['chainmap_id']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
