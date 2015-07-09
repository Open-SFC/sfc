# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
from horizon import exceptions
from horizon import forms
from horizon import messages


LOG = logging.getLogger(__name__)


class UpdateConfig(forms.SelfHandlingForm):
    CONFIG_SLUG_CHOICES = (
        ("", _("Select Slug")),
        ("firewall", _("Firewall")),
        ("loadbalancer", _("Loadbalancer")),
        ("vpn", _("VPN")),
        ("snort", _("SNORT")),	
    )
    
    config_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Configuration Name"),
                                  required=True,
                                  initial="",
                                  help_text=_("Name of the Configuration"))
    slug = forms.ChoiceField(label=_("Slug"),
                                    choices=CONFIG_SLUG_CHOICES,
                                    required=True)
    tenant_id = forms.CharField(widget=forms.HiddenInput)
        
    failure_url = 'horizon:project:configurations:index'

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            #params = {'name': data['name']}
            #params['gateway_ip'] = data['gateway_ip']
            config = api.sfc.config_handle_modify(request, data['config_id'],
                                               name=data['name'],
                                               slug=data['slug'])
            msg = _('Configuration %s was successfully updated.') % data['config_id']
            LOG.debug(msg)
            messages.success(request, msg)
            return config
        except Exception:
            msg = _('Failed to update Configuration %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)