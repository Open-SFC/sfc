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
import netaddr
import re

from django.utils.text import normalize_newlines
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import workflows
##from horizon.utils import fields
from netaddr import IPNetwork


LOG = logging.getLogger(__name__)


class CreateGeneralAction(workflows.Action):

    def __init__(self, request, *args, **kwargs):
        super(CreateGeneralAction, self).__init__(request, *args, **kwargs)
        # Populate image choices
        chains = [('', _("Select Chain"))]
        tenant_id = self.request.user.tenant_id
        for chain in api.sfc.chain_list_for_tenant(request, tenant_id):
            chains.append((chain.id, chain.name))
        self.fields['chain_id'].choices = chains
    type = (
        ("", _("Select")),
        ("Any", _("Any")),
        ("Value", _("Value")),
    )
    chainset_id = forms.CharField(label=_("Chainset Id"),
                                  widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length=50, label=_("Name"),
                           required=True,
                           initial="")
    chain_id = forms.ChoiceField(label=_("Select Chain"), required=True)
    eth_type = forms.ChoiceField(label=_("Eth Type"),
                                 required=True,
                                 choices=type)
    eth_value = forms.CharField(label=_("Eth Value"),
                                help_text=_(
                                    "If Eth Type is 'Any' , Leave blank"),
                                required=False
                                )
    ip_protocol = forms.CharField(label=_("Protocol"))

    class Meta:
        name = ("Info")
        help_text = _("From here you can Add Rule General information.\n"
                      ""
                      "")


class CreateMacAction(workflows.Action):
    type = (
        ("", _("Select")),
        ("Any", _("Any")),
        ("Value", _("Value")),
    )
    src_mac_type = forms.ChoiceField(label=_("Source Mac. Type"),
                                     required=True,
                                     choices=type)
    src_mac = forms.CharField(label=_("Source Mac."),
                              help_text=_(
                                  "If Source Mac Type is 'Any' , Leave blank"),
                              required=False
                              )
    dest_mac_type = forms.ChoiceField(label=_("Destination Mac. Type"),
                                      required=True,
                                      choices=type)
    dest_mac = forms.CharField(label=_("Destination Mac."),
                               help_text=_(
                                   "If Destination Mac Type is 'Any' , Leave blank"),
                               required=False
                               )

    class Meta:
        name = ("Mac Address")
        help_text = _("Add Mac. Address Details.\n"
                      ""
                      "")


class CreateIpAction(workflows.Action):
    type = (
        ("", _("Select")),
        ("Any", _("Any")),
        ("Single", _("Single")),
        ("Subnet", _("Subnet")),
        ("Range", _("Range")),
    )
    sip_type = forms.ChoiceField(label=_("Source IP Type"),
                                 required=True,
                                 choices=type)
    sip = forms.CharField(label=_("Source IP"),
                          help_text=_("<li>If Source IP Type is 'Any', Leave blank. </li>"
                                      "<li>If Source IP Type is 'Single', add ip address (e.g. 192.168.10.10) </li>"
                                      "<li>If Source IP Type is 'Subnet', add Subnet (e.g. 192.168.0.0/24) </li>"
                                      "<li>If Source IP Type is 'Range', comma seperated ip address (e.g. 192.168.11.11,192.168.11.100) </li>"
                                      ),
                          required=False
                          )
    dip_type = forms.ChoiceField(label=_("Destination IP Type"),
                                 required=True,
                                 choices=type)
    dip = forms.CharField(label=_("Source IP"),
                          help_text=_("<li>If Destination IP Type is 'Any', Leave blank.</li> "
                                      "<li>If Destination IP Type is 'Single', add ip address (e.g. 192.168.10.10)</li> "
                                      "<li>If Destination IP Type is 'Subnet', add Subnet (e.g. 192.168.0.0/24)</li> "
                                      "<li>If Destination IP Type is 'Range', comma seperated ip address (e.g. 192.168.11.11,192.168.11.100)</li> "
                                      ),
                          required=False
                          )

    class Meta:
        name = ("IP Address ")
        help_text = _("Add IP Address Details.\n"
                      ""
                      "")


class CreatePortAction(workflows.Action):
    type = (
        ("", _("Select")),
        ("Any", _("Any")),
        ("Single", _("Single")),
        ("Range", _("Range")),
    )
    sp_type = forms.ChoiceField(label=_("Source Port Type"),
                                required=True,
                                choices=type)
    sp = forms.CharField(label=_("Source Port"),
                         help_text=_("<li>If Source Port Type is 'Any', Leave blank. </li>"
                                     "<li>If Source Port Type is 'Single', add port number (e.g. 8080) </li>"
                                     "<li>If Source Port Type is 'Range', comma seperated port numbers (e.g. 80,8080) </li>"
                                     ),
                         required=False
                         )
    dp_type = forms.ChoiceField(label=_("Destination Port Type"),
                                required=True,
                                choices=type)
    dp = forms.CharField(label=_("Destination Port"),
                         help_text=_("<li>If Destination Port Type is 'Any', Leave blank. </li>"
                                     "<li>If Destination Port Type is 'Single', add port number (e.g. 8080) </li>"
                                     "<li>If Destination Port Type is 'Range', comma seperated port numbers (e.g. 80,8080) </li>"
                                     ),
                         required=False
                         )

    class Meta:
        name = ("Port")
        help_text = _("Add Port Details.\n"
                      ""
                      "")


class CreateGeneral(workflows.Step):
    action_class = CreateGeneralAction
    contributes = (
        "chainset_id", "name", "chain_id", "eth_type", "eth_value", "ip_protocol",)


class CreateMac(workflows.Step):
    action_class = CreateMacAction
    contributes = ("src_mac_type", "src_mac", "dest_mac_type", "dest_mac",)


class CreateIp(workflows.Step):
    action_class = CreateIpAction
    contributes = ("sip_type", "sip", "dip_type", "dip",)


class CreatePort(workflows.Step):
    action_class = CreatePortAction
    contributes = ("sp_type", "sp", "dp_type", "dp",)


class AddRule(workflows.Workflow):
    slug = "create_rule"
    name = _("Create Rule")
    finalize_button_name = _("Create")
    success_message = _('Created Rule "%s".')
    failure_message = _('Unable to create Rule "%s".')
    success_url = 'horizon:project:chainsets:detail'
    default_steps = (CreateGeneral,
                     CreateMac,
                     CreateIp,
                     CreatePort,
                     )
    failure_url = 'horizon:project:chainsets:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.context.get('chainset_id'),))

    def format_status_message(self, message):
        name = self.context.get('name') or self.context.get('chainset_id', '')
        return message % name

    def handle(self, request, data):
        tenant_id = self.request.user.tenant_id

        try:
            src_mac = ''
            dest_mac = ''
            eth_value = ''
            if data['src_mac_type'] != 'Any':
                src_mac = data['src_mac']
            if data['dest_mac_type'] != 'Any':
                dest_mac = data['dest_mac']
            if data['eth_type'] != 'Any':
                eth_value = data['eth_value']

            sip_start = ''
            sip_end = ''
            dip_start = ''
            dip_end = ''

            if data['sip_type'] == 'Single':
                sip_start = data['sip']
                sip_end = ''
            if data['sip_type'] == 'Range':
                sip = data['sip']
                siparr = sip.split(',')
                sip_start = siparr[0]
                sip_end = siparr[1]
            if data['sip_type'] == 'Subnet':
                net = IPNetwork(data['sip'])
                sip_start = str(net.network)
                sip_end = str(net.netmask)

            if data['dip_type'] == 'Single':
                dip_start = data['dip']
                dip_end = ''
            if data['dip_type'] == 'Range':
                dip = data['dip']
                diparr = dip.split(',')
                dip_start = diparr[0]
                dip_end = diparr[1]
            if data['dip_type'] == 'Subnet':
                net = IPNetwork(data['dip'])
                dip_start = str(net.network)
                dip_end = str(net.netmask)

            sp_start = ''
            sp_end = ''
            dp_start = ''
            dp_end = ''

            if data['sp_type'] == 'Single':
                sp_start = data['sp']
                sp_end = ''
            if data['sp_type'] == 'Range':
                sp = data['sp']
                sparr = sp.split(',')
                sp_start = sparr[0]
                sp_end = sparr[1]
            if data['dp_type'] == 'Single':
                dp_start = data['dp']
                dp_end = ''
            if data['dp_type'] == 'Range':
                dp = data['dp']
                dparr = dp.split(',')
                dp_start = dparr[0]
                dp_end = dparr[1]

            sg = api.sfc.rule_create(request, data['chainset_id'],
                                     name=data['name'],
                                     chain_id=data['chain_id'],
                                     src_mac_type=data['src_mac_type'],
                                     dest_mac_type=data['dest_mac_type'],
                                     src_mac=src_mac,
                                     dest_mac=dest_mac,
                                     eth_type=data['eth_type'],
                                     eth_value=eth_value,
                                     sip_type=data['sip_type'],
                                     dip_type=data['dip_type'],
                                     sip_start=sip_start,
                                     sip_end=sip_end,
                                     dip_start=dip_start,
                                     dip_end=dip_end,
                                     sp_type=data['sp_type'],
                                     dp_type=data['dp_type'],
                                     sp_start=sp_start,
                                     sp_end=sp_end,
                                     dp_start=dp_start,
                                     dp_end=dp_end,
                                     ip_protocol=data['ip_protocol'],
                                     )

            return sg
        except:
            exceptions.handle(request)
            return False
