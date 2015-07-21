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

import logging

from nscs.crd_consumer.client.sdnofcfg.v1 import CreateCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import DeleteCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import ListCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import ShowCommand
from nscs.crd_consumer.client.sdnofcfg.v1 import UpdateCommand


class ListChainNetworkMap(ListCommand):
    """List ChainNetworkMaps that belong to a given tenant."""
    resource = 'chain_network'
    log = logging.getLogger(__name__ + '.ListChainNetworkMap')
    list_columns = ['id', 'name', 'type', 'chain_selection_id',
                    'inbound_network', 'outbound_network', 'admin_status']
    pagination_support = True
    sorting_support = True


class CreateChainNetworkMap(CreateCommand):
    """Create a ChainNetworkMap for a given tenant."""

    resource = 'chain_network'
    log = logging.getLogger(__name__ + '.CreateChainNetworkMap')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--chain_network_id',
            help='Chain Network Map ID')
        parser.add_argument(
            '--chain_set_id',
            help='Chain Set ID')
        parser.add_argument(
            '--type',
            help='Chain Network Type. l2/l3')
        parser.add_argument(
            '--inbound_network',
            help='Inbound Network')
        parser.add_argument(
            '--outbound_network',
            help='Outbound Network')
        parser.add_argument(
            '--admin_status',
            help='Eg:true/false')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of ChainNetworkMap to create')
        
    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.admin_status.lower() == 'true':
            admin_status = True
        else:
            admin_status = False
        body = {'chain_network':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.chain_network_id,
                    'type': parsed_args.type.lower(),
                    'chain_set_id': parsed_args.chain_set_id,
                    'inbound_network': parsed_args.inbound_network,
                    'outbound_network': parsed_args.outbound_network,
                    'admin_status': admin_status
                }
            }
        if parsed_args.tenant_id:
            body['chain_network'].update({'tenant' : parsed_args.tenant_id})

        if parsed_args.type.lower() == 'l2':
            body['chain_network'].update(
                {'outbound_network': parsed_args.inbound_network})

        return body


class DeleteChainNetworkMap(DeleteCommand):
    """Delete ChainNetworkMap information."""

    log = logging.getLogger(__name__ + '.DeleteChainNetworkMap')
    resource = 'chain_network'


class ShowChainNetworkMap(ShowCommand):
    """Show information of a given NSRM ChainNetworkMap."""

    resource = 'chain_network'
    log = logging.getLogger(__name__ + '.ShowChainNetworkMap')


class UpdateChainNetworkMap(UpdateCommand):
    """Update ChainNetworkMap information."""

    log = logging.getLogger(__name__ + '.UpdateChainNetworkMap')
    resource = 'chain_network'
