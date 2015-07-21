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
Views for managing Crd Images.
"""
import logging

from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon import workflows
from .forms import UpdateImage
from .tables import ImagesTable
from .workflows import CreateImage
from .tabs import ImageDetailTabs

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ImagesTable
    template_name = 'project/appliances/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            appliances = api.sfc.appliance_list_for_tenant(self.request,
                                                           tenant_id)
            for appliance in appliances:
                glanceimage = ''
                image_id = appliance.image_id
                glanceimg = api.glance.image_get(self.request, str(image_id))
                glanceimage = glanceimg.name
                setattr(appliance, 'glanceimage', glanceimage)

        except:
            appliances = []
            msg = _('Image list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in appliances:
            n.set_id_as_name_if_empty()
        return appliances


class CreateImageView(workflows.WorkflowView):
    workflow_class = CreateImage
    template_name = 'project/appliances/create.html'

    def get_initial(self):
        pass


class UpdateImageView(forms.ModalFormView):
    form_class = UpdateImage
    template_name = 'project/appliances/update.html'
    context_object_name = 'appliance'
    success_url = reverse_lazy("horizon:project:appliances:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateImageView, self).get_context_data(**kwargs)
        appliance = self._get_object()
        context["appliance_id"] = self.kwargs['appliance_id']
        context["name"] = appliance['name']
        context["image_id"] = appliance['image_id'],
        context["category_id"] = appliance['category_id'],
        context["vendor_id"] = appliance['vendor_id'],
        context["flavor_id"] = appliance['flavor_id'],
        context["security_group_id"] = appliance['security_group_id'],
        context["form_factor_type"] = appliance['form_factor_type']
        context["type"] = appliance['type'],
        context["load_share_algorithm"] = appliance['load_share_algorithm'],
        context["high_threshold"] = appliance['high_threshold'],
        context["low_threshold"] = appliance['low_threshold']
        context["load_indication_type"] = appliance['load_indication_type']
        context["pkt_field_to_hash"] = appliance['pkt_field_to_hash']
        context["config_handle_id"] = appliance['config_handle_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            appliance_id = self.kwargs['appliance_id']
            try:
                self._object = api.sfc.appliance_get(self.request,
                                                     appliance_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve appliance details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_initial(self):
        appliance = self._get_object()
        return {'appliance_id': appliance['id'],
                'tenant_id': appliance['tenant_id'],
                'name': appliance['name'],
                'image_id': appliance['image_id'],
                'category_id': appliance['category_id'],
                'vendor_id': appliance['vendor_id'],
                'flavor_id': appliance['flavor_id'],
                'security_group_id': appliance['security_group_id'],
                'form_factor_type': appliance['form_factor_type'],
                'type': appliance['type'],
                'load_share_algorithm': appliance['load_share_algorithm'],
                'high_threshold': appliance['high_threshold'],
                'low_threshold': appliance['low_threshold'],
                'load_indication_type': appliance['load_indication_type'],
                'pkt_field_to_hash': appliance['pkt_field_to_hash'],
                'config_handle_id': appliance['config_handle_id'],}


class DetailImageView(tabs.TabView):
    tab_group_class = ImageDetailTabs
    template_name = 'project/appliances/detail.html'
