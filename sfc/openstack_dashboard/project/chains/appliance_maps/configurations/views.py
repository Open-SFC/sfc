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
from .forms import MapConf

LOG = logging.getLogger(__name__)


class MapconfView(forms.ModalFormView):
    form_class = MapConf
    template_name = 'project/chains/appliance_maps/configurations/mapconf.html'
    success_url = 'horizon:project:chains:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chain_id'], self.kwargs['appliance_map_id']))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                chain_id = self.kwargs["chain_id"]
                appliance_map_id = self.kwargs["appliance_map_id"]
                self._object = api.sfc.appliance_map_get(self.request,
                                                         chain_id,
                                                         appliance_map_id)
            except:
                redirect = reverse('horizon:project:chains:index')
                msg = _("Unable to retrieve data.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(MapconfView, self).get_context_data(**kwargs)
        context['appliance_map'] = self.get_object()
        context['chain_id'] = self.kwargs['chain_id']
        return context

    def get_initial(self):
        appliance_map = self.get_object()
        return {"appliance_map_id": self.kwargs['appliance_map_id'],
                "appliance_map_name": appliance_map.name,
                "chain_id": self.kwargs['chain_id']}
