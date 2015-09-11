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
from .forms import AddZone, Editzone

LOG = logging.getLogger(__name__)


class Addzoneview(forms.ModalFormView):
    form_class = AddZone
    template_name = 'project/chainsets/zones/addzone.html'
    success_url = 'horizon:project:chainsets:zones'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chainset_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                chainset_id = self.kwargs["chainset_id"]
                self._object = api.sfc.chainset_get(self.request,
                                                    chainset_id)
            except:
                redirect = reverse('horizon:project:chainsets:index')
                msg = _("Unable to retrieve Chainset.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(Addzoneview, self).get_context_data(**kwargs)
        context['chainset'] = self.get_object()
        return context

    def get_initial(self):
        chainset = self.get_object()
        return {"chainset_id": self.kwargs['chainset_id'],
                "chainset_name": chainset.name}


class EditzoneView(forms.ModalFormView):
    form_class = Editzone
    template_name = 'project/chainsets/zones/update.html'
    context_object_name = 'zone'
    success_url = 'horizon:project:chainsets:zones'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chainset_id'],))

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            zone_id = self.kwargs['zone_id']
            chainset = self.kwargs['chainset_id']
            try:
                self._object = api.sfc.zone_get(
                    self.request, chainset, zone_id)
            except:
                redirect = reverse('horizon:project:chainsets:index')
                msg = _('Unable to Zone')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        zone = self.get_object()
        context = super(EditzoneView, self).get_context_data(**kwargs)
        context["chainset_id"] = self.kwargs['chainset_id']
        context["zone_id"] = self.kwargs['zone_id']
        return context

    def get_initial(self):
        zone = self.get_object()
        return {'chainset_id': self.kwargs['chainset_id'],
                'zone_id': self.kwargs['zone_id'],
                'zone': zone['zone'],
                'direction': zone['direction']}