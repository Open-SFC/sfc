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
Views for managing Crd Chainmaps.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from .tables import ChainmapsTable
from .forms import CreateChainmap, UpdateChainmap, Launchchain

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ChainmapsTable
    template_name = 'project/chainmaps/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            chainmaps = api.sfc.chainmap_list_for_tenant(self.request,
                                                         tenant_id)
            for chainmap in chainmaps:
                inbound_network_id = chainmap.inbound_network_id
                try:
                    in_net = api.neutron.network_get(
                        self.request, inbound_network_id)
                    setattr(chainmap, 'in_net', in_net.name)
                except:
                    msg = _('Unable to retrieve details for Network "%s".') \
                        % (inbound_network_id)
                    setattr(chainmap, 'in_net', '')
        except:
            chainmaps = []
            msg = _('Chainmap list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in chainmaps:
            n.set_id_as_name_if_empty()
        return chainmaps


class CreateChainmapView(forms.ModalFormView):
    form_class = CreateChainmap
    template_name = 'project/chainmaps/create.html'
    success_url = reverse_lazy('horizon:project:chainmaps:index')


class UpdateChainmapView(forms.ModalFormView):
    form_class = UpdateChainmap
    template_name = 'project/chainmaps/update.html'
    context_object_name = 'chainmap'
    success_url = reverse_lazy("horizon:project:chainmaps:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateChainmapView, self).get_context_data(**kwargs)
        context["chainmap_id"] = self.kwargs['chainmap_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            chainmap_id = self.kwargs['chainmap_id']
            try:
                self._object = api.sfc.chainmap_get(self.request,
                                                    chainmap_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve chainmap details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_initial(self):
        chainmap = self._get_object()
        return {'chainmap_id': chainmap['id'],
                'tenant_id': chainmap['tenant_id'],
                'name': chainmap['name'],
                'inbound_network_id': chainmap['inbound_network_id'],
                'outbound_network_id': chainmap['outbound_network_id'],
                'chainset_id': chainmap['chainset_id']}


class LaunchChainView(forms.ModalFormView):
    form_class = Launchchain
    template_name = 'project/chainmaps/launch.html'
    context_object_name = 'chainmap'
    success_url = reverse_lazy('horizon:project:instances:index')

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            chainmap_id = self.kwargs['chainmap_id']
            try:
                self._object = api.sfc.chainmap_get(self.request, chainmap_id)
            except:
                redirect = reverse('horizon:project:chainmaps:index')
                msg = _('Unable to get Chain Map')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        chainmap = self.get_object()
        context = super(LaunchChainView, self).get_context_data(**kwargs)
        context["chainmap_id"] = self.kwargs['chainmap_id']
        context["chainset_id"] = chainmap.chainset_id
        return context

    def get_initial(self):
        chainmap = self.get_object()
        return {'chainmap_id': self.kwargs['chainmap_id'],
                'chainset_id': chainmap.chainset_id}
