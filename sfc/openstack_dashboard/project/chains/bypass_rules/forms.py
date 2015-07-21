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


class Editl2rule(forms.SelfHandlingForm):
    chain_id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(label=_("Name"))
    rule_id = forms.CharField(label=_("ID"),
                              widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:project:chains:index'

    def handle(self, request, data):
        try:
            rule = api.sfc.bypass_rule_modify(request, data['chain_id'],
                                                data['rule_id'],
                                                name=data['name'])
            msg = _('Chain %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return rule
        except:
            msg = _('Failed to update L2 Rule %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)