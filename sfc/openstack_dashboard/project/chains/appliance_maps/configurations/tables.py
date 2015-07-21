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


class AssociateConf(tables.LinkAction):
    name = "mapconf"
    verbose_name = _("Associate Configuration")
    url = "horizon:project:chains:mapconf"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        appliance_map_id = self.table.kwargs['appliance_map_id']
        return reverse(self.url, args=(self.table.kwargs['chain_id'], appliance_map_id,))


class DissociateConf(tables.DeleteAction):
    data_type_singular = _("Chain Configuration")
    data_type_plural = _("Chain Configuration")

    def delete(self, request, appliance_map_conf_id):
        try:
            chain_id = self.table.kwargs['chain_id']
            api.sfc.appliance_map_conf_delete(request, appliance_map_conf_id)

            LOG.debug('Dissociated Configuration %s successfully' %
                      appliance_map_conf_id)
        except:
            chain_id = self.table.kwargs['chain_id']
            msg = _(
                'Failed to Dissociated configuration %s') % appliance_map_conf_id
            LOG.info(msg)
            appliance_map_id = self.table.kwargs['appliance_map_id']
            redirect = reverse('horizon:project:chains:appliance_maps:detail',
                               args=[chain_id, appliance_map_id])
            exceptions.handle(request, msg, redirect=redirect)


class ChainConfsTable(tables.DataTable):
    network_function_name = tables.Column("network_function_name",
                                          verbose_name=_("Network Function"))
    config_handle_name = tables.Column("config_handle_name",
                                       verbose_name=_("Configuration"))

    class Meta:
        name = "appliance_map_confs"
        verbose_name = _("Chain - Appliance - Configuration Map List")
        table_actions = (AssociateConf, DissociateConf, )
        row_actions = (DissociateConf, )
