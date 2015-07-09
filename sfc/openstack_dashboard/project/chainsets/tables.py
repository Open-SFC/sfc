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


class CreateChainset(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Chainset")
    url = "horizon:project:chainsets:create"
    classes = ("ajax-modal", "btn-create")


class DeleteChainset(tables.DeleteAction):
    data_type_singular = _("Chainset")
    data_type_plural = _("Chainsets")

    def delete(self, request, chainset_id):
        try:
            api.sfc.chainset_delete(request, chainset_id)
            LOG.debug('Deleted chainset %s successfully' % chainset_id)
        except:
            msg = _('Failed to delete chainset %s') % chainset_id
            LOG.info(msg)
            redirect = reverse("horizon:project:chainsets:index")
            exceptions.handle(request, msg, redirect=redirect)


class EditChainset(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Chainset")
    url = "horizon:project:chainsets:update"
    classes = ("ajax-modal", "btn-edit")


class ChainsetsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:chainsets:detail')

    class Meta:
        name = "chainsets"
        verbose_name = _("Chainset List")
        table_actions = (CreateChainset, DeleteChainset)
        row_actions = (DeleteChainset, )
