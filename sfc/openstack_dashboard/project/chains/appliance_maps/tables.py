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

from django import template
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import tables


LOG = logging.getLogger(__name__)


class AssociateImage(tables.LinkAction):
    name = "mapimg"
    verbose_name = _("Associate Appliance")
    url = "horizon:project:chains:mapimg"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id,))


class DissociateImage(tables.DeleteAction):
    data_type_singular = _("Chain Appliance")
    data_type_plural = _("Chain Appliances")

    def delete(self, request, appliance_map_id):
        try:
            chain_id = self.table.kwargs['chain_id']
            appliance_maps = api.sfc.appliance_map_list_for_chain(request,
                                                                  chain_id)
            for appliance_map in appliance_maps:
                if appliance_map.id == appliance_map_id:
                    appliance_id = appliance_map.appliance_id
                    break
            api.sfc.appliance_map_delete(request, chain_id, appliance_id)
            LOG.debug('Dissociated Chain Appliance %s successfully' %
                      appliance_map_id)
        except:
            msg = _(
                'Failed to Dissociated Chain Appliance %s') % appliance_map_id
            LOG.info(msg)
            chain_id = self.table.kwargs['chain_id']
            redirect = reverse('horizon:project:chains:detail',
                               args=[chain_id])
            exceptions.handle(request, msg, redirect=redirect)


class EditChainMap(tables.LinkAction):
    name = "editchainimg"
    verbose_name = _("Edit Chain Appliance")
    url = "horizon:project:chains:editchainimg"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, appliance_map):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id, appliance_map.id))


class DetailView(tables.LinkAction):
    name = "detail"
    verbose_name = _(" Chain Details")
    url = "horizon:project:chains:detail"
    classes = ("btn-edit")

    def get_link_url(self, appliance_map):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id, appliance_map.id))


def get_appliance_map(appliance_map):
    context = appliance_map.chain_appliance
    return context


class AssociateConfiguration(tables.LinkAction):
    name = "mapconf"
    verbose_name = _("Associate Configuration")
    url = "horizon:project:chains:mapconf"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, appliance_map):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id, appliance_map.id))


def get_appliance_link(datum):
    view = "horizon:project:appliances:detail"
    if datum.appliance_id:
        return reverse(view, args=(datum.appliance_id,))
    else:
        return None


def get_instance_link(datum):
    view = "horizon:project:instances:detail"
    if datum.instance_uuid:
        return reverse(view, args=(datum.instance_uuid,))
    else:
        return None

def get_network_link(datum):
    view = "horizon:project:networks:detail"
    if datum.network_id:
        return reverse(view, args=(datum.network_id,))
    else:
        return None

class ListInstances(tables.LinkAction):
    name = "listinstances"
    verbose_name = _("List Instances")
    url = "horizon:project:chains:listinstances"

    def get_link_url(self, appliance_map):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id, appliance_map.appliance_id))

class ChainImagesTable(tables.DataTable):
    id = tables.Column("id",
                       verbose_name=_("Id"))
    name = tables.Column("name",
                         verbose_name=_("Name"))
    image = tables.Column(get_appliance_map,
                          verbose_name=_("Image"),
                          link=get_appliance_link)
    sequence_number = tables.Column(
        "sequence_number", verbose_name=_("Sequence Number"))
    #instance_uuid = tables.Column("instance_uuid", verbose_name=_("Instance"),
    #                              link=get_instance_link)

    class Meta:
        name = "appliance_maps"
        verbose_name = _("Chain - Appliance List")
        table_actions = (AssociateImage, DissociateImage, )
        row_actions = (ListInstances, DissociateImage)
        
class ListInstancesTable(tables.DataTable):
    id = tables.Column("id",verbose_name=_("Id"))
    instance_name = tables.Column("instance_name", verbose_name=_("Instance"),
                                  link=get_instance_link)
    network_name = tables.Column("network_name", verbose_name=_("Network"),
                                 link=get_network_link)
    vlan_in = tables.Column("vlan_in", verbose_name=_("VLAN In"))
    vlan_out = tables.Column("vlan_out", verbose_name=_("VLAN Out"))
    
    class Meta:
        name = "chain_appliance_instances"
        verbose_name = _("Chain - Appliance - Instance List")
        