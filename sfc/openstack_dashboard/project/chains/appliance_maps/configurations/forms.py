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


class BaseConfForm(forms.SelfHandlingForm):

    def __init__(self, request, *args, **kwargs):
        super(BaseConfForm, self).__init__(request, *args, **kwargs)
        config_handle_choices = [('', _("Select Config Handle"))]
        tenant_id = self.request.user.tenant_id
        for config_handle in api.sfc.config_handle_list_for_tenant(request, tenant_id):
            config_handle_choices.append(
                (config_handle.id, config_handle.name))
        self.fields['config_handle_id'].choices = config_handle_choices


class MapConf(BaseConfForm):
    chain_id = forms.CharField(label=_("Chain ID"),
                               widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    appliance_map_id = forms.CharField(label=_("Chain Image ID"),
                                       widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    config_handle_id = forms.ChoiceField(
        label=_("Configuration Handle"), required=True)

    def handle(self, request, data):
        try:
            netfun = api.sfc.config_handle_get(
                request, data['config_handle_id'])
            networkfunction_id = netfun.networkfunction_id
            sg = api.sfc.appliance_map_conf_create(request,
                                                   chain_map_id=data[
                                                       'appliance_map_id'],
                                                   networkfunction_id=networkfunction_id,
                                                   config_handle_id=data['config_handle_id'])

            # str1 = api.sfc.launch_chain(request,
            #                                 data['config_handle_id'])
            messages.success(request,
                             _('Successfully created Chain  Configuration Map: %s')
                             % data['config_handle_id'])
            return sg
        except:
            redirect = reverse(
                "horizon:project:chains:detail", args=[data['chain_id']])
            exceptions.handle(request,
                              _('Unable to Map Chain to image.'),
                              redirect=redirect)
