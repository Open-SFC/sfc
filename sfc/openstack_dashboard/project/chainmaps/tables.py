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
from django.core.urlresolvers import reverse
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import tables


LOG = logging.getLogger(__name__)


class CreateChainmap(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Chain Map")
    url = "horizon:project:chainmaps:create"
    classes = ("ajax-modal", "btn-create")


class DeleteChainmap(tables.DeleteAction):
    data_type_singular = _("Chainmap")
    data_type_plural = _("Chainmaps")

    def delete(self, request, chainmap_id):
        try:
            api.sfc.chainmap_delete(request, chainmap_id)
            LOG.debug('Deleted chainmap %s successfully' % chainmap_id)
        except:
            msg = _('Failed to delete chainmap %s') % chainmap_id
            LOG.info(msg)
            redirect = reverse("horizon:project:chainmaps:index")
            exceptions.handle(request, msg, redirect=redirect)


class EditChainmap(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Chain Map")
    url = "horizon:project:chainmaps:update"
    classes = ("ajax-modal", "btn-edit")


def get_inbound_network_link(datum):
    view = "horizon:project:networks:detail"
    if datum.inbound_network_id:
        return reverse(view, args=(datum.inbound_network_id,))
    else:
        return None


def get_outbound_network_link(datum):
    view = "horizon:project:networks:detail"
    if datum.outbound_network_id:
        return reverse(view, args=(datum.outbound_network_id,))
    else:
        return None


class LaunchChain(tables.LinkAction):
    name = "launch"
    verbose_name = _("Launch")
    url = "horizon:project:chainmaps:launch"
    classes = ("ajax-modal", "btn-edit")


class ChainmapsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    in_net = tables.Column("in_net", verbose_name=_("Network"),
                           link=get_inbound_network_link)

    chainset_id = tables.Column("chainset_id",
                                verbose_name=_("Chainset"))

    class Meta:
        name = "chainmaps"
        verbose_name = _("Chainmap List")
        table_actions = (CreateChainmap, DeleteChainmap)
        row_actions = (EditChainmap, DeleteChainmap, LaunchChain)
