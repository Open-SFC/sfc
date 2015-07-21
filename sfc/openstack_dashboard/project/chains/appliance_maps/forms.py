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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import forms
from horizon import messages
from horizon import exceptions
#from horizon.utils import fields

LOG = logging.getLogger(__name__)


class BaseImageForm(forms.SelfHandlingForm):

    def __init__(self, request, *args, **kwargs):
        super(BaseImageForm, self).__init__(request, *args, **kwargs)
        # Populate image choices
        appliance_choices = [('', _("Select an Appliance"))]
        tenant_id = self.request.user.tenant_id
        for appliance in api.sfc.appliance_list_for_tenant(request, tenant_id):
            appliance_choices.append((appliance.id, appliance.name))
        self.fields['appliance_id'].choices = appliance_choices

class MapImage(BaseImageForm):
    chain_id = forms.CharField(label=_("Chain ID"),
                               widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Name"))
    appliance_id = forms.ChoiceField(label=_("Appliance"), required=True)
    sequence_number = forms.IntegerField(label=_("Boot order"),
                                         min_value=1,
                                         initial=1)
    
    def handle(self, request, data):
        try:
            sg = api.sfc.appliance_map_create(request, data['chain_id'],
                                              name=data['name'],
                                              appliance_id=data['appliance_id'],
                                              sequence_number=data['sequence_number'])
            messages.success(request,
                             _('Successfully created Chain  Image Map: %s')
                             % data['name'])
            return sg
        except:
            redirect = reverse("horizon:project:chains:detail")
            exceptions.handle(request,
                              _('Unable to Map Chain to appliance.'),
                              redirect=redirect)


class UpdateChain_image(forms.SelfHandlingForm):
    chain_id = forms.CharField(widget=forms.HiddenInput())
    appliance_map_id = forms.CharField(label=_("ID"),
                                       widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    #instance_uuid = forms.CharField(widget=forms.HiddenInput(), required=False)

    name = forms.CharField(max_length=255,
                           label=_("Name"),
                           required=False)
    sequence_number = forms.IntegerField(label=_("Boot order"),
                                         min_value=1,
                                         initial=1)
    failure_url = 'horizon:project:chains:detail'

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            appliance_map = api.sfc.appliance_map_modify(request, data['chain_id'],
                                                         data['appliance_map_id'],
                                                         name=data['name'],
                                                         sequence_number=data['sequence_number'])
            msg = _('Chain Image Map %s was successfully updated.') % data[
                'name']
            LOG.debug(msg)
            messages.success(request, msg)
            return appliance_map
        except Exception:
            msg = _('Failed to update chain image map %s') % data[
                'appliance_map_id']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['chain_id']])
            exceptions.handle(request, msg, redirect=redirect)