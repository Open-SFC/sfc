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
Views for managing Crd Chainsets.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from .tables import ChainsetsTable 
from .forms import CreateChainset, UpdateChainset
from .rules.tables import ChainrulesTable
from .zones.tables import SFCZonesTable

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ChainsetsTable
    template_name = 'project/chainsets/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            chainsets = api.sfc.chainset_list_for_tenant(self.request,
                                                         tenant_id)
            
            directions = {'1': 'Zoneless',
                          '2': 'Left',
                          '3': 'Right'}
            for cs in chainsets:
                direction = cs.direction
                direction = directions[direction]
                setattr(cs, 'dir', direction)
        except:
            chainsets = []
            msg = _('Chainset list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in chainsets:
            n.set_id_as_name_if_empty()
        return chainsets


class CreateChainsetView(forms.ModalFormView):
    form_class = CreateChainset
    template_name = 'project/chainsets/create.html'
    success_url = reverse_lazy('horizon:project:chainsets:index')


class UpdateChainsetView(forms.ModalFormView):
    form_class = UpdateChainset
    template_name = 'project/chainsets/update.html'
    context_object_name = 'chainset'
    success_url = reverse_lazy("horizon:project:chainsets:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateChainsetView, self).get_context_data(**kwargs)
        context["chainset_id"] = self.kwargs['chainset_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            chainset_id = self.kwargs['chainset_id']
            try:
                self._object = api.sfc.chainset_get(self.request,
                                                    chainset_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve chainset details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_initial(self):
        chainset = self._get_object()
        return {'chainset_id': chainset['id'],
                'tenant_id': chainset['tenant_id'],
                'name': chainset['name'],
                'zonefull': chainset['zonefull'],
                'direction': chainset['direction'],}


class DetailChainsetView(tables.DataTableView):
    table_class = ChainrulesTable
    template_name = 'project/chainsets/detail.html'
    failure_url = reverse_lazy('horizon:project:chainsets:index')

    def get_data(self):
        try:
            chainset = self._get_data()
            chainrules = api.sfc.rule_list_for_chainset(self.request,
                                                        chainset.id)
        except:
            chainrules = []
            msg = _('Rule list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in chainrules:
            s.set_id_as_name_if_empty()
        return chainrules

    def _get_data(self):
        if not hasattr(self, "_chainset"):
            try:
                chainset_id = self.kwargs['chainset_id']
                chainset = api.sfc.chainset_get(self.request, chainset_id)
                chainset.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for Chainset "%s".') \
                    % (chainset_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._chainset = chainset
        return self._chainset

    def get_context_data(self, **kwargs):
        context = super(DetailChainsetView, self).get_context_data(**kwargs)
        context["chainset"] = self._get_data()
        return context

class SFCZonesView(tables.DataTableView):
    table_class = SFCZonesTable
    template_name = 'project/chainsets/zones.html'
    failure_url = reverse_lazy('horizon:project:chainsets:index')

    def get_data(self):
        try:
            chainset = self._get_data()
            zones = api.sfc.zone_list_for_chainset(self.request,
                                                        chainset.id)
            directions = {'1': 'Zoneless',
                          '2': 'Left',
                          '3': 'Right'}
            for zone in zones:
                direction = zone.direction
                direction = directions[direction]
                setattr(zone, 'dir', direction)
            
        except:
            zones = []
            msg = _('Rule list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in zones:
            s.set_id_as_name_if_empty()
        return zones

    def _get_data(self):
        if not hasattr(self, "_chainset"):
            try:
                chainset_id = self.kwargs['chainset_id']
                chainset = api.sfc.chainset_get(self.request, chainset_id)
                chainset.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for Chainset "%s".') \
                    % (chainset_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._chainset = chainset
        return self._chainset

    def get_context_data(self, **kwargs):
        context = super(SFCZonesView, self).get_context_data(**kwargs)
        context["chainset"] = self._get_data()
        return context