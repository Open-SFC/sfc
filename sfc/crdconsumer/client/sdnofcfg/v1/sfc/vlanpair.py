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


class ListVlanPair(ListCommand):
    """List VlanPairs that belong to a given tenant."""
    resource = 'vlan_pair'
    log = logging.getLogger(__name__ + '.ListVlanPair')
    list_columns = ['id', 'instance_id', 'network_id', 'vlan_id', 'direction']
    pagination_support = True
    sorting_support = True
    
class CreateVlanPair(CreateCommand):
    """Create a VlanPair for a given tenant."""

    resource = 'vlan_pair'
    log = logging.getLogger(__name__ + '.CreateVlanPair')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--vlan_pair_id',
            help='Vlan Pair ID')
        parser.add_argument(
            '--instance_id',
            help='Instance ID')
        parser.add_argument(
            '--network_id',
            help='Network ID')
        parser.add_argument(
            '--vlan_id',
            help='VLAN ID')
        parser.add_argument(
            '--direction',
            help='Direction Eg:ingress/egress')
        
    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.admin_status.lower() == 'true':
            admin_status = True
        else:
            admin_status = False
        body = {'vlan_pair':
                {
                    'id': parsed_args.vlan_pair_id,
                    'instance_id':parsed_args.instance_id,
                    'network_id':parsed_args.network_id,
                    'vlan_id':parsed_args.vlan_id,
                    'direction':parsed_args.direction
                }
            }
        if parsed_args.tenant_id:
            body['vlan_pair'].update({'tenant' : parsed_args.tenant_id})

        return body
    
class DeleteVlanPair(DeleteCommand):
    """Delete VlanPair information."""

    log = logging.getLogger(__name__ + '.DeleteVlanPair')
    resource = 'vlan_pair'
    
class ShowVlanPair(ShowCommand):
    """Show information of a given NSRM VlanPair."""

    resource = 'vlan_pair'
    log = logging.getLogger(__name__ + '.ShowVlanPair')
    
class UpdateVlanPair(UpdateCommand):
    """Update VlanPair information."""

    log = logging.getLogger(__name__ + '.UpdateVlanPair')
    resource = 'vlan_pair'
