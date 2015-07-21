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


class DeleteAppliance(tables.DeleteAction):
    data_type_singular = _("Appliance")
    data_type_plural = _("Appliances")

    def delete(self, request, appliance_id):
        try:
            api.sfc.appliance_delete(request, appliance_id)
            LOG.debug('Deleted appliance %s successfully' % appliance_id)
        except:
            msg = _('Failed to delete appliance %s') % appliance_id
            LOG.info(msg)
            redirect = reverse("horizon:project:appliances:index")
            exceptions.handle(request, msg, redirect=redirect)


class CreateAppliance(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Appliance")
    url = "horizon:project:appliances:create"
    classes = ("ajax-modal", "btn-create")


class EditAppliance(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Appliance")
    url = "horizon:project:appliances:update"
    classes = ("ajax-modal", "btn-edit")


def get_category(appliance):
    context = appliance.appliance_categories
    return context


def get_vendor(appliance):
    context = appliance.appliance_vendors
    return context


def get_image_link(datum):
    view = "horizon:project:images:images:detail"
    if datum.image_id:
        return reverse(view, args=(datum.image_id,))
    else:
        return None

class ImagesTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:appliances:detail')
    glanceimage = tables.Column("glanceimage",
                                verbose_name=_("Glance Image"),
                                link=get_image_link)
    category = tables.Column(get_category,
                             verbose_name=_("Category"))
    vendor = tables.Column(get_vendor,
                           verbose_name=_("Vendor"))

    class Meta:
        name = "appliances"
        verbose_name = _("Appliances")
        table_actions = (CreateAppliance, DeleteAppliance)
        row_actions = (
            EditAppliance, DeleteAppliance,)
