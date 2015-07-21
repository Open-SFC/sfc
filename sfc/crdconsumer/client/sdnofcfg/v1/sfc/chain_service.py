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


class ListChainService(ListCommand):
    """List ChainServices that belong to a given tenant."""
    resource = 'chain_service'
    log = logging.getLogger(__name__ + '.ListChainService')
    list_columns = ['id', 'chain_id', 'service_id', 'sequence_number']
    pagination_support = True
    sorting_support = True
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_id',
            help='Chain ID')
    
class CreateChainService(CreateCommand):
    """Create a ChainService for a given tenant."""

    resource = 'chain_service'
    log = logging.getLogger(__name__ + '.CreateChainService')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_service_id',
            help='Chain Service ID')
        parser.add_argument(
            '--chain_id',
            help='Chain ID')
        parser.add_argument(
            '--service_id',
            help='Service ID')
        parser.add_argument(
            '--sequence_number',
            help='Sequence Number')
        
    def args2body(self, parsed_args):
        body = {'chain_service':
                {
                    'id': parsed_args.chain_service_id,
                    'service_id':parsed_args.service_id,
                    'sequence_number':parsed_args.sequence_number,
                }
            }
        return body
    
class DeleteChainService(DeleteCommand):
    """Delete ChainService information."""

    log = logging.getLogger(__name__ + '.DeleteChainService')
    resource = 'chain_service'
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_id',
            help='Chain ID')

    
class ShowChainService(ShowCommand):
    """Show information of a given NSRM ChainService."""

    resource = 'chain_service'
    log = logging.getLogger(__name__ + '.ShowChainService')
    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_id',
            help='Chain ID')
    
class UpdateChainService(UpdateCommand):
    """Update ChainService information."""

    log = logging.getLogger(__name__ + '.UpdateChainService')
    resource = 'chain_service'
    def add_known_arguments(self, parser):
        parser.add_argument(
                '--chain_id',
                help='Chain ID')
