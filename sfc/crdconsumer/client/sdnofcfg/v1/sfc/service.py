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


class ListService(ListCommand):
    """List Services that belong to a given tenant."""
    resource = 'service'
    log = logging.getLogger(__name__ + '.ListService')
    list_columns = ['id', 'name', 'form_factor_type', 'admin_status']
    pagination_support = True
    sorting_support = True
    
class CreateService(CreateCommand):
    """Create a Service for a given tenant."""

    resource = 'service'
    log = logging.getLogger(__name__ + '.CreateService')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--service_id',
            help='Service ID')
        parser.add_argument(
            '--form_factor_type',
            help='Form Factor Type Eg:vm/physical')
        parser.add_argument(
            '--admin_status',
            help='Eg:up/down')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of Service to create')
        
    def args2body(self, parsed_args):
        print str(parsed_args)
        if parsed_args.admin_status.lower() == 'true':
            admin_status = True
        else:
            admin_status = False
        body = {'service':
                {
                    'name': parsed_args.name,
                    'id': parsed_args.service_id,
                    'form_factor_type':parsed_args.form_factor_type,
                    'admin_status': admin_status
                }
            }
        if parsed_args.tenant_id:
            body['service'].update({'tenant' : parsed_args.tenant_id})

        return body
    
class DeleteService(DeleteCommand):
    """Delete Service information."""

    log = logging.getLogger(__name__ + '.DeleteService')
    resource = 'service'
    
class ShowService(ShowCommand):
    """Show information of a given NSRM Service."""

    resource = 'service'
    log = logging.getLogger(__name__ + '.ShowService')
    
class UpdateService(UpdateCommand):
    """Update Service information."""

    log = logging.getLogger(__name__ + '.UpdateService')
    resource = 'service'
