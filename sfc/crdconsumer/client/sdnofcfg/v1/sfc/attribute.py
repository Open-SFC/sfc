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


class ListAttribute(ListCommand):
    """List Attributes that belong to a given tenant."""
    resource = 'attribute'
    log = logging.getLogger(__name__ + '.ListAttribute')
    list_columns = ['id', 'table_name', 'table_id', 'name', 'value']
    pagination_support = True
    sorting_support = True
    
class CreateAttribute(CreateCommand):
    """Create a Attribute for a given tenant."""

    resource = 'attribute'
    log = logging.getLogger(__name__ + '.CreateAttribute')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--table_name',
            help='Table Name')
        parser.add_argument(
            '--table_id',
            help='Table ID')
        parser.add_argument(
            '--name',
            help='Attibute Name')
        parser.add_argument(
            '--value',
            help='Attribute Value')
        
    def args2body(self, parsed_args):
        body = {'attribute':
                {
                    'table_name': parsed_args.table_name,
                    'table_id':parsed_args.table_id,
                    'name':parsed_args.name,
                    'value':parsed_args.value
                }
            }
        return body
    
class DeleteAttribute(DeleteCommand):
    """Delete Attribute information."""

    log = logging.getLogger(__name__ + '.DeleteAttribute')
    resource = 'attribute'
    
class ShowAttribute(ShowCommand):
    """Show information of a given NSRM Attribute."""

    resource = 'attribute'
    log = logging.getLogger(__name__ + '.ShowAttribute')
    
class UpdateAttribute(UpdateCommand):
    """Update Attribute information."""

    log = logging.getLogger(__name__ + '.UpdateAttribute')
    resource = 'attribute'
