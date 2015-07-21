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


class ListChain(ListCommand):
    """List Chains that belong to a given tenant."""
    resource = 'chain'
    log = logging.getLogger(__name__ + '.ListChain')
    list_columns = ['id', 'name', 'type', 'load_share_algorithm', 'high_threshold', 'low_threshold', 'admin_status']
    pagination_support = True
    sorting_support = True
    
class CreateChain(CreateCommand):
    """Create a Chain for a given tenant."""

    resource = 'chain'
    log = logging.getLogger(__name__ + '.CreateChain')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_id',
            help='Chain ID')
        parser.add_argument(
            '--type',
            help='Chain Type Eg:l2/l3')
        parser.add_argument(
            '--load_share_algorithm',
            help='Load Share Algorithm')
        parser.add_argument(
            '--high_threshold',
            help='High Threshold')
        parser.add_argument(
            '--low_threshold',
            help='Low Threshold')
        parser.add_argument(
            '--pkt_field_to_hash',
            help='Packet Field To Hash')
        parser.add_argument(
            '--load_indication_type',
            help='Load Indication Type')
        parser.add_argument(
            '--admin_status',
            help='Eg:true/false')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Chain to create')
        
    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.admin_status.lower() == 'true':
            admin_status = True
        else:
            admin_status = False
        body = {'chain':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.chain_id,
                    'type':parsed_args.type,
                    'load_share_algorithm':parsed_args.load_share_algorithm,
                    'high_threshold':parsed_args.high_threshold,
                    'low_threshold':parsed_args.low_threshold,
                    'pkt_field_to_hash':parsed_args.pkt_field_to_hash,
                    'load_indication_type':parsed_args.load_indication_type,
                    'admin_status': admin_status
                }
            }
        if parsed_args.tenant_id:
            body['chain'].update({'tenant' : parsed_args.tenant_id})

        return body
    
class DeleteChain(DeleteCommand):
    """Delete Chain information."""

    log = logging.getLogger(__name__ + '.DeleteChain')
    resource = 'chain'
    
class ShowChain(ShowCommand):
    """Show information of a given NSRM Chain."""

    resource = 'chain'
    log = logging.getLogger(__name__ + '.ShowChain')
    
class UpdateChain(UpdateCommand):
    """Update Chain information."""

    log = logging.getLogger(__name__ + '.UpdateChain')
    resource = 'chain'
    """
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_id',
            help='Chain ID')
        parser.add_argument(
            '--tenant_id',
            help='Tenant ID')
        parser.add_argument(
            '--type',
            help='Chain Type Eg:l2/l3')
        parser.add_argument(
            '--load_share_algorithm',
            help='Load Share Algorithm')
        parser.add_argument(
            '--high_threshold',
            help='High Threshold')
        parser.add_argument(
            '--low_threshold',
            help='Low Threshold')
        parser.add_argument(
            '--pkt_field_to_hash',
            help='Packet Field To Hash')
        parser.add_argument(
            '--load_indication_type',
            help='Load Indication Type')
        parser.add_argument(
            '--admin_status',
            help='Eg:up/down')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Chain to update')

    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.admin_status.lower() == 'true':
            admin_status = True
        else:
            admin_status = False
        body = {'chain':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.chain_id,
                    'type':parsed_args.type,
                    'load_share_algorithm':parsed_args.load_share_algorithm,
                    'high_threshold':parsed_args.high_threshold,
                    'low_threshold':parsed_args.low_threshold,
                    'pkt_field_to_hash':parsed_args.pkt_field_to_hash,
                    'load_indication_type':parsed_args.load_indication_type,
                    'admin_status': admin_status
                }
            }
        if parsed_args.tenant_id:
            body['chain'].update({'tenant' : parsed_args.tenant_id})

        return body
    """
