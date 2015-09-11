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
##from horizon.utils import fields

LOG = logging.getLogger(__name__)


class AddZone(forms.SelfHandlingForm):
    DIRECTIONS = (
            ("", _("Select")),
            ("1", _("Zoneless")),
            ("2", _("Left")),
            ("3", _("Right")),
            )
    chainset_id = forms.CharField(label=_("Chainset ID"),
                               widget=forms.TextInput(
                                attrs={'readonly': 'readonly'}))
    zone = forms.CharField(label=_("Zone"))
    direction = forms.ChoiceField(label=_("Direction"),
                                       required=True,
                                       choices=DIRECTIONS)

    def handle(self, request, data):
        try:
            sg = api.sfc.zone_create(request, data['chainset_id'],
                                       zone=data['zone'],
                                       direction=data['direction'])

            messages.success(request,
                             _('Successfully created Zone: %s')
                             % data['zone'])
            return sg
        except:
            redirect = reverse("horizon:project:chainsets:zones")
            exceptions.handle(request,
                              _('Unable to create Zone.'),
                              redirect=redirect)

class Editzone(forms.SelfHandlingForm):
    DIRECTIONS = (
            ("", _("Select")),
            ("1", _("Zoneless")),
            ("2", _("Left")),
            ("3", _("Right")),
            )
    chainset_id = forms.CharField(widget=forms.HiddenInput())
    zone = forms.CharField(label=_("Zone"),
                           widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    direction = forms.ChoiceField(label=_("Direction"),
                                       required=True,
                                       choices=DIRECTIONS)
    failure_url = 'horizon:project:chainsets:zones'

    def handle(self, request, data):
        try:
            zone = api.sfc.zone_modify(request, data['chainset_id'],
                                       data['zone_id'],
                                       zone=data['zone'],
                                       direction=data['direction'])
            msg = _('Zone %s was successfully updated.') % data['zone']
            LOG.debug(msg)
            messages.success(request, msg)
            return zone
        except:
            msg = _('Failed to update Zone %s') % data['zone']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
