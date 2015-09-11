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


class AddZone(tables.LinkAction):
    name = "addzone"
    verbose_name = _("Add Zone")
    url = "horizon:project:chainsets:addzone"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        chainset_id = self.table.kwargs['chainset_id']
        return reverse(self.url, args=(chainset_id,))


class DeleteZone(tables.DeleteAction):
    data_type_singular = _("Zone")
    data_type_plural = _("Zones")

    def delete(self, request, zone_id):
        try:
            chainset_id = self.table.kwargs['chainset_id']
            api.sfc.zone_delete(request, chainset_id, zone_id)
            LOG.debug('Delete Zone %s successfully' % zone_id)
        except:
            msg = _('Failed to Delete Zone %s') % zone_id
            LOG.info(msg)
            chainset_id = self.table.kwargs['chainset_id']
            redirect = reverse('horizon:project:chainsets:zones',
                               args=[chainset_id])
            exceptions.handle(request, msg, redirect=redirect)


class EditZone(tables.LinkAction):
    name = "editzone"
    verbose_name = _("Edit Zone")
    url = "horizon:project:chainsets:editzone"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, zone):
        chainset_id = self.table.kwargs['chainset_id']
        return reverse(self.url, args=(chainset_id, zone.id))


class SFCZonesTable(tables.DataTable):
    zone = tables.Column("zone",
                         verbose_name=_("Zone"))
    dir = tables.Column("dir",
                         verbose_name=_("Direction"))

    class Meta:
        name = "zones"
        verbose_name = _("SFC Zones")
        table_actions = (AddZone, DeleteZone)
        row_actions = (EditZone, DeleteZone)
