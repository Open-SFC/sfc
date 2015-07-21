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


class ListChainSet(ListCommand):
    """List ChainSets that belong to a given tenant."""
    resource = 'chain_set'
    log = logging.getLogger(__name__ + '.ListChainSet')
    list_columns = ['id', 'name', 'type', 'admin_status']
    pagination_support = True
    sorting_support = True
    
class CreateChainSet(CreateCommand):
    """Create a ChainSet for a given tenant."""

    resource = 'chain_set'
    log = logging.getLogger(__name__ + '.CreateChainSet')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chainset_id',
            help='Chain Set ID')
        parser.add_argument(
            '--type',
            help='Chain Set Type Eg:l2/l3')
        parser.add_argument(
            '--admin_status',
            help='Eg:up/down')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of ChainSet to create')
        
    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.admin_status.lower() == 'true':
            admin_status = True
        else:
            admin_status = False
        body = {'chain_set':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.chainset_id,
                    'type':parsed_args.type,
                    'admin_status': admin_status
                }
            }
        if parsed_args.tenant_id:
            body['chain_set'].update({'tenant' : parsed_args.tenant_id})

        return body
    
class DeleteChainSet(DeleteCommand):
    """Delete ChainSet information."""

    log = logging.getLogger(__name__ + '.DeleteChainSet')
    resource = 'chain_set'
    
class ShowChainSet(ShowCommand):
    """Show information of a given NSRM ChainSet."""

    resource = 'chain_set'
    log = logging.getLogger(__name__ + '.ShowChainSet')
    
class UpdateChainSet(UpdateCommand):
    """Update ChainSet information."""

    log = logging.getLogger(__name__ + '.UpdateChainSet')
    resource = 'chain_set'
