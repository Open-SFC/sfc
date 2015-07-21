# Copyright 2012 OpenStack LLC.
# All Rights Reserved
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
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse
import logging

from nscs.crd_consumer.client.common import utils
from nscs.crd_consumer.client.sdnofcfg.v1 import CreateCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import DeleteCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import ListCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import ShowCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import UpdateCommand


class ListSelectionRule(ListCommand):
    """List SelectionRules that belong to a given tenant."""
    resource = 'chain_selection_rule'
    log = logging.getLogger(__name__ + '.ListSelectionRule')
    list_columns = ['id', 'name', 'chain_id', 'chain_set_id', 'protocol', 'admin_status']
    pagination_support = True
    sorting_support = True
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_set_id',
            help='Chain Set ID')
    
class CreateSelectionRule(CreateCommand):
    """Create a SelectionRule for a given tenant."""

    resource = 'chain_selection_rule'
    log = logging.getLogger(__name__ + '.CreateSelectionRule')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--selection_rule_id',
            help='Selection Rule ID')
        parser.add_argument(
            '--chain_id',
            help='Chain ID')
        parser.add_argument(
            '--chain_set_id',
            help='Chain Set ID')
        parser.add_argument(
            '--src_mac_type',
            help='Source MAC Address Type')
        parser.add_argument(
            '--dst_mac_type',
            help='Source MAC Address Type')
        parser.add_argument(
            '--src_mac',
            help='Source MAC Addres')
        parser.add_argument(
            '--dst_mac',
            help='Destination MAC Address')
        parser.add_argument(
            '--eth_type',
            help='Ethernet Type')
        parser.add_argument(
            '--eth_value',
            help='Ethernet Value')
        parser.add_argument(
            '--sip_type',
            help='Source IP Type')
        parser.add_argument(
            '--dip_type',
            help='Destination IP Type')
        parser.add_argument(
            '--sip_start',
            help='Source IP Start')
        parser.add_argument(
            '--sip_end',
            help='Source IP End')
        parser.add_argument(
            '--dip_start',
            help='Destination IP Start')
        parser.add_argument(
            '--dip_end',
            help='Destination IP End')
        parser.add_argument(
            '--sp_type',
            help='Source Port Type')
        parser.add_argument(
            '--dp_type',
            help='Destination Port Type')
        parser.add_argument(
            '--sp_start',
            help='Source Port Start')
        parser.add_argument(
            '--sp_end',
            help='Source Port End')
        parser.add_argument(
            '--dp_start',
            help='Destination Port Start')
        parser.add_argument(
            '--dp_end',
            help='Destination Port End')
        parser.add_argument(
            '--protocol',
            help='IP Protocol')
        parser.add_argument(
            '--admin_status',
            help='Eg:true/false')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Selection Rule to create')
        
    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.admin_status.lower() == 'true':
            admin_status = True
        else:
            admin_status = False
        body = {'chain_selection_rule':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.selection_rule_id,
                    'chain_id': parsed_args.chain_id,
                    'chain_set_id': parsed_args.chain_set_id,
                    'protocol':parsed_args.protocol,
                    'admin_status': admin_status
                }
            }

        if parsed_args.tenant_id:
            body['chain_selection_rule'].update({'tenant' : parsed_args.tenant_id})

        if parsed_args.eth_type.lower() == 'single':
            body['chain_selection_rule'].update({'eth_value' : parsed_args.eth_value,
                'eth_type':parsed_args.eth_type})
        else:
            body['chain_selection_rule'].update({'eth_type':'any'})

        if parsed_args.src_mac_type.lower() == 'single':
            body['chain_selection_rule'].update({'src_mac':parsed_args.src_mac,
                'src_mac_type':parsed_args.src_mac_type})
        else:
            body['chain_selection_rule'].update({'src_mac_type': 'any'})

        if parsed_args.dst_mac_type.lower() == 'single':
            body['chain_selection_rule'].update({'dst_mac':parsed_args.dst_mac,
                'dst_mac_type':parsed_args.dst_mac_type})
        else:
            body['chain_selection_rule'].update({'dst_mac_type': 'any'})

        ### SIP ####
        if parsed_args.sip_type.lower() == 'single':
            body['chain_selection_rule'].update({'sip_type':parsed_args.sip_type,
                'sip_start': parsed_args.sip_start,
                'sip_end':parsed_args.sip_start})
        elif parsed_args.sip_type.lower() in ['range', 'subnet']:
            body['chain_selection_rule'].update({'sip_type':parsed_args.sip_type,
                'sip_start': parsed_args.sip_start,
                'sip_end':parsed_args.sip_end})
        else:
            body['chain_selection_rule'].update({'sip_type':'any'})

        ### DIP ####
        if parsed_args.dip_type.lower() == 'single':
            body['chain_selection_rule'].update({'dip_type':parsed_args.dip_type,
                'dip_start': parsed_args.dip_start,
                'dip_end':parsed_args.dip_start})
        elif parsed_args.dip_type.lower() in ['range', 'subnet']:
            body['chain_selection_rule'].update({'dip_type':parsed_args.dip_type,
                'dip_start': parsed_args.dip_start,
                'dip_end':parsed_args.dip_end})
        else:
            body['chain_selection_rule'].update({'dip_type':'any'})

        ### SP ###
        if parsed_args.sp_type.lower() == 'single':
            body['chain_selection_rule'].update({'sp_type':parsed_args.sp_type,
                'sp_start':parsed_args.sp_start,
                'sp_end':parsed_args.sp_start})
        elif parsed_args.sp_type.lower() == 'range':
            body['chain_selection_rule'].update({'sp_type':parsed_args.sp_type,
                'sp_start':parsed_args.sp_start,
                'sp_end':parsed_args.sp_end})
        else:
            body['chain_selection_rule'].update({'sp_type':'any'})
        
        ### DP ###
        if parsed_args.dp_type.lower() == 'single':
            body['chain_selection_rule'].update({'dp_type':parsed_args.dp_type,
                'dp_start':parsed_args.dp_start,
                'dp_end':parsed_args.dp_start})
        elif parsed_args.dp_type.lower() == 'range':
            body['chain_selection_rule'].update({'dp_type':parsed_args.dp_type,
                'dp_start':parsed_args.dp_start,
                'dp_end':parsed_args.dp_end})
        else:
            body['chain_selection_rule'].update({'dp_type':'any'})

        return body
    
class DeleteSelectionRule(DeleteCommand):
    """Delete SelectionRule information."""

    log = logging.getLogger(__name__ + '.DeleteSelectionRule')
    resource = 'chain_selection_rule'
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_set_id',
            help='Chain Set ID')
    
class ShowSelectionRule(ShowCommand):
    """Show information of a given NSRM SelectionRule."""

    resource = 'chain_selection_rule'
    log = logging.getLogger(__name__ + '.ShowSelectionRule')
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_set_id',
            help='Chain Set ID')
    
class UpdateSelectionRule(UpdateCommand):
    """Update SelectionRule information."""

    log = logging.getLogger(__name__ + '.UpdateSelectionRule')
    resource = 'chain_selection_rule'
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_set_id',
            help='Chain Set ID')
