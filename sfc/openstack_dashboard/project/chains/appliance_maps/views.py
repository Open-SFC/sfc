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

from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import workflows
from .forms import MapImage, UpdateChain_image
from .configurations.tables import ChainConfsTable
from .workflows import UpdateChainApplianceMap
from .tables import ListInstancesTable


LOG = logging.getLogger(__name__)


class MapimgView(forms.ModalFormView):
    form_class = MapImage
    template_name = 'project/chains/appliance_maps/mapimg.html'
    success_url = 'horizon:project:chains:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chain_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                chain_id = self.kwargs["chain_id"]
                self._object = api.sfc.chain_get(self.request,
                                                 chain_id)
            except:
                redirect = reverse('horizon:project:chains:index')
                msg = _("Unable to retrieve Chain.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(MapimgView, self).get_context_data(**kwargs)
        context['chain'] = self.get_object()
        return context

    def get_initial(self):
        chain = self.get_object()
        return {"chain_id": self.kwargs['chain_id'],
                "chain_name": chain.name}

class EditChain_imageView(workflows.WorkflowView):
    workflow_class = UpdateChainApplianceMap
    template_name = 'project/chains/appliance_maps/update.html'
    success_url = reverse_lazy("horizon:project:chains:detail")

    def get_context_data(self, **kwargs):
        appliance_map = self.get_object()
        context = super(EditChain_imageView, self).get_context_data(**kwargs)
        context["chain_id"] = self.kwargs['chain_id']
        context["appliance_map_id"] = self.kwargs['appliance_map_id']
        #context["appliance_map_confs"] = appliance_map['appliance_map_confs']
        return context

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            appliance_map_id = self.kwargs['appliance_map_id']
            chain = self.kwargs['chain_id']
            try:
                self._object = api.sfc.appliance_map_get(
                    self.request, chain, appliance_map_id)
            except:
                redirect = reverse("horizon:project:chains:index")
                msg = _('Unable to retrieve chain image details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_initial(self):
        appliance_map = self.get_object()
        initial = super(EditChain_imageView, self).get_initial()
        initial.update({'chain_id': self.kwargs['chain_id'],
                        'appliance_map_id': self.kwargs['appliance_map_id'],
                        'name': appliance_map['name'],
                        'appliance_id': appliance_map['appliance_id'],
                        'sequence_number': appliance_map['sequence_number'],
                        'appliance_map_confs': appliance_map['appliance_map_confs']})
        return initial


class DetailChainImageView(tables.DataTableView):
    table_class = ChainConfsTable
    template_name = 'project/chains/appliance_maps/detail.html'
    failure_url = reverse_lazy('horizon:project:chains:index')

    def get_data(self):
        try:
            appliance_map = self._get_data()
            appliance_map_confs = api.sfc.appliance_map_conf_list_for_chain(self.request,
                                                                            chain_map_id=appliance_map.id)
            for appliance_map_conf in appliance_map_confs:
                networkfunction_id = appliance_map_conf.networkfunction_id
                config_handle_id = appliance_map_conf.config_handle_id
                config_handle_name = ''
                network_function_name = ''
                if networkfunction_id != '':
                    network_function = api.sfc.networkfunction_get(
                        self.request, networkfunction_id)
                    network_function_name = network_function.name
                if config_handle_id != '':
                    config_handle = api.sfc.config_handle_get(
                        self.request, config_handle_id)
                    config_handle_name = config_handle.name

                setattr(
                    appliance_map_conf, 'config_handle_name', config_handle_name)
                setattr(
                    appliance_map_conf, 'network_function_name', network_function_name)

        except:
            appliance_map_confs = []
            msg = _('Configuration list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in appliance_map_confs:
            s.set_id_as_name_if_empty()

        return appliance_map_confs

    def _get_data(self):
        if not hasattr(self, "_appliance_map"):
            try:
                appliance_map_id = self.kwargs['appliance_map_id']
                chain_id = self.kwargs['appliance_map_id']
                appliance_map = api.sfc.appliance_map_get(
                    self.request, chain_id, appliance_map_id)
                appliance_map.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for chain image "%s".') \
                    % (appliance_map_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._appliance_map = appliance_map
        return self._appliance_map

    def get_context_data(self, **kwargs):
        context = super(DetailChainImageView, self).get_context_data(**kwargs)
        context["appliance_map"] = self._get_data()
        return context
    
    
class ListInstancesView(tables.DataTableView):
    table_class = ListInstancesTable
    template_name = 'project/chains/appliance_maps/instances.html'
    failure_url = reverse_lazy('horizon:project:chains:index')

    def get_data(self):
        try:
            appliance_map = self._get_data()
            appliance_map_instances = api.sfc.appliance_map_instance_list_for_chain(self.request,
                                                                            appliance_map.chain_id, appliance_map.appliance_id)
            for appliance_map_instance in appliance_map_instances:
                appliance_map_id = appliance_map_instance.appliance_map_id
                instance_uuid = appliance_map_instance.instance_uuid
                network_id = appliance_map_instance.network_id
                vlan_in = appliance_map_instance.vlan_in
                vlan_out = appliance_map_instance.vlan_out
                if network_id != '':
                    network = api.neutron.network_get(
                        self.request, network_id)
                    network_name = network.name
                if instance_uuid != '':
                    instance = api.nova.server_get(
                        self.request, instance_uuid)
                    instance_name = instance.name
                
                setattr(
                    appliance_map_instance, 'network_name', network_name)
                setattr(
                    appliance_map_instance, 'instance_name', instance_name)

        except:
            appliance_map_instances = []
            msg = _('Chain Appliance Map Instances list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in appliance_map_instances:
            s.set_id_as_name_if_empty()

        return appliance_map_instances

    def _get_data(self):
        if not hasattr(self, "_appliance_map_instance"):
            try:
                appliance_map_id = self.kwargs['appliance_map_id']
                chain_id = self.kwargs['chain_id']
                appliance_map = api.sfc.appliance_map_get(
                    self.request, chain_id, appliance_map_id)
                appliance_map.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for chain appliance map "%s".') \
                    % (appliance_map_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._appliance_map = appliance_map
        return self._appliance_map

    def get_context_data(self, **kwargs):
        context = super(ListInstancesView, self).get_context_data(**kwargs)
        context["appliance_map"] = self._get_data()
        return context    