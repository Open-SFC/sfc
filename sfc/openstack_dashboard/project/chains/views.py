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

"""
Views for managing Crd Chains.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from .forms import CreateChain, UpdateChain
from .tables import ChainsTable
from .appliance_maps.tables import ChainImagesTable
from .bypass_rules.tables import ChainBypassTable


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = (ChainsTable)
    template_name = 'project/chains/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            chains = api.sfc.chain_list_for_tenant(self.request,
                                                   tenant_id)
        except:
            chains = []
            msg = _('Chain list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in chains:
            n.set_id_as_name_if_empty()
        return chains


class CreateChainView(forms.ModalFormView):
    form_class = CreateChain
    template_name = 'project/chains/create.html'
    success_url = reverse_lazy('horizon:project:chains:index')


class UpdateChainView(forms.ModalFormView):
    form_class = UpdateChain
    template_name = 'project/chains/update.html'
    context_object_name = 'chain'
    success_url = reverse_lazy("horizon:project:chains:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateChainView, self).get_context_data(**kwargs)
        context["chain_id"] = self.kwargs['chain_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            chain_id = self.kwargs['chain_id']
            try:
                self._object = api.sfc.chain_get(self.request,
                                                 chain_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve chain details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_initial(self):
        chain = self._get_object()
        return {'chain_id': chain['id'],
                'tenant_id': chain['tenant_id'],
                'name': chain['name']}


class DetailChainView(tables.MultiTableView):
    table_classes = (ChainImagesTable, )
    template_name = 'project/chains/detail.html'
    failure_url = reverse_lazy('horizon:project:chains:index')

    def get_appliance_maps_data(self):
        try:
            chain = self._get_data()
            appliance_maps = api.sfc.appliance_map_list_for_chain(self.request,
                                                                  chain.id)
            #for appliance_map in appliance_maps:
            #    chain_map_id = appliance_map.id
            #    instance_id = appliance_map.instance_uuid
            #    try:
            #        instance = api.nova.server_get(self.request, instance_id)
            #        setattr(appliance_map, 'instance_uuid', instance.id)
            #    except:
            #        msg = _('Unable to retrieve details for instance "%s".') \
            #            % (instance_id)
            #        setattr(appliance_map, 'instance_uuid', '')
        except:
            appliance_maps = []
            msg = _('Appliance list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in appliance_maps:
            s.set_id_as_name_if_empty()
        return appliance_maps

    def _get_data(self):
        if not hasattr(self, "_chain"):
            try:
                chain_id = self.kwargs['chain_id']
                chain = api.sfc.chain_get(self.request, chain_id)
                chain.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for chain "%s".') \
                    % (chain_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._chain = chain
        return self._chain

    def get_context_data(self, **kwargs):
        context = super(DetailChainView, self).get_context_data(**kwargs)
        context["chain"] = self._get_data()
        return context


class BypassChainView(tables.MultiTableView):
    table_classes = (ChainBypassTable, )
    template_name = 'project/chains/bypassdetail.html'
    failure_url = reverse_lazy('horizon:project:chains:index')

    def get_bypassrules_data(self):
        try:
            chain = self._get_data()
            bypass_rules = api.sfc.bypass_rule_list_for_chain(self.request,
                                                                chain.id)
        except:
            bypass_rules = []
            msg = _('Bypass Rules list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in bypass_rules:
            s.set_id_as_name_if_empty()
        return bypass_rules

    def _get_data(self):
        if not hasattr(self, "_chain"):
            try:
                chain_id = self.kwargs['chain_id']
                chain = api.sfc.chain_get(self.request, chain_id)
                chain.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for chain "%s".') \
                    % (chain_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._chain = chain
        return self._chain

    def get_context_data(self, **kwargs):
        context = super(BypassChainView, self).get_context_data(**kwargs)
        context["chain"] = self._get_data()
        return context
