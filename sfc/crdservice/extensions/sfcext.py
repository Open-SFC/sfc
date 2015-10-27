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
import netaddr
import abc

from nscs.crdservice.api import extensions
from nscs.crdservice.api.v2 import attributes as attr
from nscs.crdservice.api.v2 import base
from nscs.crdservice.common import exceptions as qexception
from nscs.crdservice import manager
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.plugins.services.service_base import ServicePluginBase
#from nscs.crdservice.plugins.common import constants
from sfc.crdservice.common import constants
from nscs.crdservice.openstack.common import uuidutils

LOG = logging.getLogger(__name__)

ATTR_NOT_SPECIFIED = object()

SFC_PLURALS = {
    'networkfunctions': 'networkfunction',
    'categories': 'category',
    'vendors': 'vendor',
    'appliances': 'appliance',
    'chains': 'chain',
    'chainsets': 'chainset',
    'chainmaps': 'chainmap',
    'config_handles': 'config_handle',
    'launchs': 'launch',
    'vlanquotas': 'vlanquota',
    'nsdeltas': 'nsdelta',
    'vmscaleouts': 'vmscaleout',
}

SFC_SUB_PLURALS = {
    'appliances': 'appliance',
    'nf_maps': 'nf_map',
    'bypass_rules': 'bypass_rule',
    'rules': 'rule',
    'instances': 'instance',
    'zones': 'zone',
}

RESOURCE_ATTRIBUTE_MAP = {
    'networkfunctions': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        attr.SHARED: {'allow_post': True,
                      'allow_put': True,
                      'default': False,
                      'convert_to': attr.convert_to_boolean,
                      'is_visible': True,
                      'required_by_policy': True,
                      'enforce_policy': True},
    },
    'categories': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        attr.SHARED: {'allow_post': True,
                      'allow_put': True,
                      'default': False,
                      'convert_to': attr.convert_to_boolean,
                      'is_visible': True,
                      'required_by_policy': True,
                      'enforce_policy': True},
        'category_networkfunctions': {'allow_post': True, 'allow_put': False,
                                      'default': [],
                                      'is_visible': True},
    },
    'vendors': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        attr.SHARED: {'allow_post': True,
                      'allow_put': True,
                      'default': False,
                      'convert_to': attr.convert_to_boolean,
                      'is_visible': True,
                      'required_by_policy': True,
                      'enforce_policy': True},
    },
    'appliances': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'category_id': {'allow_post': True, 'allow_put': True,
                        'required_by_policy': True,
                        'validate': {'type:regex': attr.UUID_PATTERN},
                        'is_visible': True},
        'appliance_categories': {'allow_post': False, 'allow_put': False,
                                 'default': [],
                                 'is_visible': True},
        'vendor_id': {'allow_post': True, 'allow_put': True,
                      'required_by_policy': True,
                      'validate': {'type:regex': attr.UUID_PATTERN},
                      'is_visible': True},
        'appliance_vendors': {'allow_post': False, 'allow_put': False,
                              'default': [],
                              'is_visible': True},
        'image_id': {'allow_post': True, 'allow_put': True,
                     'required_by_policy': True,
                     'validate': {'type:regex': attr.UUID_PATTERN},
                     'is_visible': True},
        'flavor_id': {'allow_post': True, 'allow_put': True,
                      'required_by_policy': True,
                      'is_visible': True},
        'security_group_id': {'allow_post': True, 'allow_put': True,
                              'required_by_policy': True,
                              'validate': {'type:regex': attr.UUID_PATTERN},
                              'is_visible': True},
        'form_factor_type': {'allow_post': True, 'allow_put': True,
                             'required_by_policy': True,
                             'is_visible': True},
        'type': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'load_share_algorithm': {'allow_post': True, 'allow_put': True,
                                 'required_by_policy': True,
                                 'is_visible': True},
        'high_threshold': {'allow_post': True, 'allow_put': True,
                           'required_by_policy': True,
                           'is_visible': True},
        'low_threshold': {'allow_post': True, 'allow_put': True,
                          'required_by_policy': True,
                          'is_visible': True},
        'pkt_field_to_hash': {'allow_post': True, 'allow_put': True,
                              'required_by_policy': True,
                              'is_visible': True},
        'load_indication_type': {'allow_post': True, 'allow_put': True,
                                 'required_by_policy': True,
                                 'is_visible': True},
        'config_handle_id': {'allow_post': True, 'allow_put': True,
                             'required_by_policy': True,
                             'validate': {'type:regex': attr.UUID_PATTERN},
                             'is_visible': True},
    },
    'chains': {
        'id': {'allow_post': True, 'allow_put': False,
               'default': None,
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'auto_boot': {'allow_post': True, 'allow_put': True,
                      'required_by_policy': True,
                      'is_visible': True},
        'extras': {'allow_post': True, 'allow_put': True,
                   'default': '',
                   'is_visible': True},
    },
    'config_handles': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'status': {'allow_post': True, 'allow_put': True,
                   'default': True, 'is_visible': True},
        'slug': {'allow_post': True, 'allow_put': True,
                 'default': '', 'is_visible': True},
        'config_mode': {'allow_post': True, 'allow_put': True,
                        'default': '', 'is_visible': True},
    },
    'chainsets': {
        'id': {'allow_post': True, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'default': uuidutils.generate_uuid(),
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'type': {'allow_post': False, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '-Mode', 'is_visible': True},
        'zonefull': {'allow_post': True,
                     'allow_put': True,
                     'default': True,
                     'convert_to': attr.convert_to_boolean,
                     'is_visible': True},
        'direction': {'allow_post': True,
                     'allow_put': True,
                     'default': '2',
                     'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
    },
    'chainmaps': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'type': {'allow_post': False, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '-Mode', 'is_visible': True},
        'inbound_network_id': {'allow_post': True, 'allow_put': True,
                               'validate': {'type:string': None},
                               'default': '', 'is_visible': True},
        'outbound_network_id': {'allow_post': True, 'allow_put': True,
                                'validate': {'type:string': None},
                                'default': '', 'is_visible': True},
        'chainset_id': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
    },
    'launchs': {
        'rule_id': {'allow_post': True, 'allow_put': False,
                    'validate': {'type:regex': attr.UUID_PATTERN},
                    'is_visible': True},
        'chainset_id': {'allow_post': True, 'allow_put': False,
                        'validate': {'type:regex': attr.UUID_PATTERN},
                        'is_visible': True},
        'chainmap_id': {'allow_post': True, 'allow_put': False,
                        'validate': {'type:regex': attr.UUID_PATTERN},
                        'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'is_visible': False},
    },
    'vlanquotas': {
        'vlan_start': {'allow_post': True, 'allow_put': True,
                       'default': '', 'is_visible': True},
        'vlan_end': {'allow_post': True, 'allow_put': True,
                     'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'is_visible': False},
        'id': {'allow_post': False, 'allow_put': False, 'default': '',
               'validate': {'type:string': None},
               'is_visible': True},

    },
    'nsdeltas': {
        'keyword': {'allow_post': False, 'allow_put': False, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'delta': {'allow_post': False, 'allow_put': False, 'default': '',
                 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'is_visible': False},
        'id': {'allow_post': False, 'allow_put': False, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},

    },
    'vmscaleouts': {
        'instance_id': {'allow_post': True, 'allow_put': False,
                        'validate': {'type:regex': attr.UUID_PATTERN},
                        'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'is_visible': False},
    },
}

SUB_RESOURCE_ATTRIBUTE_MAP = {
    'appliances': {
        'parent': {
            'collection_name': 'chains',
            'member_name': 'chain'
        },
        'parameters': {
            'id': {'allow_post': True, 'allow_put': False,
                   'default': None, 'is_visible': True},
            'name': {'allow_post': True, 'allow_put': True,
                     'validate': {'type:string': None},
                     'default': '', 'is_visible': True},
            'chain_id': {'allow_post': False, 'allow_put': True,
                         'validate': {'type:string': None},
                         'is_visible': True},
            'appliance_id': {'allow_post': True, 'allow_put': True,
                             'validate': {'type:string': None},
                             'required_by_policy': True,
                             'is_visible': True},
            'chain_appliance': {'allow_post': False, 'allow_put': True,
                                'default': [],
                                'is_visible': True},
            'sequence_number': {'allow_post': True, 'allow_put': True,
                                'required_by_policy': True,
                                'is_visible': True},
            'tenant_id': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},
        }
    },
    'nf_maps': {
        'parent': {
            'collection_name': 'categories',
            'member_name': 'category'
        },
        'parameters': {
            'id': {'allow_post': False, 'allow_put': False,
                   'validate': {'type:regex': attr.UUID_PATTERN},
                   'is_visible': True},
            'networkfunction_id': {'allow_post': True, 'allow_put': False,
                                   'validate': {'type:string': None},
                                   'required_by_policy': True,
                                   'is_visible': True},
            'networkfunctions': {'allow_post': False, 'allow_put': False,
                                 'default': [],
                                 'is_visible': True},
            'tenant_id': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},
        }
    },
    'bypass_rules': {
        'parent': {
            'collection_name': 'chains',
            'member_name': 'chain'
        },
        'parameters': {
            'id': {'allow_post': False, 'allow_put': False,
                   'validate': {'type:regex': attr.UUID_PATTERN},
                   'is_visible': True},
            'name': {'allow_post': True, 'allow_put': True,
                     'validate': {'type:string': None},
                     'default': '', 'is_visible': True},
            'chain_id': {'allow_post': False, 'allow_put': False,
                         'validate': {'type:string': None},
                         'required_by_policy': True,
                         'is_visible': True},
            'src_mac_type': {'allow_post': True, 'allow_put': True,
                             'validate': {'type:string': None},
                             'default': 'any', 'is_visible': True},
            'dest_mac_type': {'allow_post': True, 'allow_put': True,
                              'validate': {'type:string': None},
                              'default': 'any', 'is_visible': True},
            'src_mac': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
            'dest_mac': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            'eth_type': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            'eth_value': {'allow_post': True, 'allow_put': True,
                          'validate': {'type:string': None},
                          'default': '', 'is_visible': True},
            'sip_type': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': 'any', 'is_visible': True},
            'dip_type': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': 'any', 'is_visible': True},
            'sip_start': {'allow_post': True, 'allow_put': True,
                          'validate': {'type:string': None},
                          'default': '', 'is_visible': True},
            'sip_end': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
            'dip_start': {'allow_post': True, 'allow_put': True,
                          'validate': {'type:string': None},
                          'default': '', 'is_visible': True},
            'dip_end': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
            'sp_type': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': 'any', 'is_visible': True},
            'dp_type': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': 'any', 'is_visible': True},
            'sp_start': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            'sp_end': {'allow_post': True, 'allow_put': True,
                       'validate': {'type:string': None},
                       'default': '', 'is_visible': True},
            'dp_start': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            'dp_end': {'allow_post': True, 'allow_put': True,
                       'validate': {'type:string': None},
                       'default': '', 'is_visible': True},
            'ip_protocol': {'allow_post': True, 'allow_put': True,
                            'validate': {'type:string': None},
                            'default': '', 'is_visible': True},
            'nwservice_count': {'allow_post': True, 'allow_put': True,
                                'validate': {'type:string': None},
                                'default': '', 'is_visible': True},
            'nwservice_names': {'allow_post': True, 'allow_put': True,
                                'validate': {'type:string': None},
                                'default': '', 'is_visible': True},
            'tenant_id': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},
        }
    },

    'rules': {
        'parent': {
            'collection_name': 'chainsets',
            'member_name': 'chainset'
        },
        'parameters': {
            'id': {'allow_post': True, 'allow_put': False,
                   #'validate': {'type:regex': attr.UUID_PATTERN},
                   'default': None,
                   'is_visible': True},
            'name': {'allow_post': True, 'allow_put': True,
                     'validate': {'type:string': None},
                     'default': '', 'is_visible': True},
            'chain_id': {'allow_post': True, 'allow_put': True,
                         #'validate': {'type:string': None},
                         'default': None,
                         #'required_by_policy': True,
                         'is_visible': True},
            'chainset_id': {'allow_post': False, 'allow_put': True,
                            'validate': {'type:string': None},
                            'required_by_policy': True,
                            'is_visible': True},
            'src_mac_type': {'allow_post': True, 'allow_put': True,
                             'validate': {'type:string': None},
                             'default': 'any', 'is_visible': True},
            'dest_mac_type': {'allow_post': True, 'allow_put': True,
                              'validate': {'type:string': None},
                              'default': 'any', 'is_visible': True},
            'src_mac': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
            'dest_mac': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            'eth_type': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            'eth_value': {'allow_post': True, 'allow_put': True,
                          'validate': {'type:string': None},
                          'default': '', 'is_visible': True},
            'sip_type': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': 'any', 'is_visible': True},
            'dip_type': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': 'any', 'is_visible': True},
            'sip_start': {'allow_post': True, 'allow_put': True,
                          'validate': {'type:string': None},
                          'default': '', 'is_visible': True},
            'sip_end': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
            'dip_start': {'allow_post': True, 'allow_put': True,
                          'validate': {'type:string': None},
                          'default': '', 'is_visible': True},
            'dip_end': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': '', 'is_visible': True},
            'sp_type': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': 'any', 'is_visible': True},
            'dp_type': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'default': 'any', 'is_visible': True},
            'sp_start': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            'sp_end': {'allow_post': True, 'allow_put': True,
                       'validate': {'type:string': None},
                       'default': '', 'is_visible': True},
            'dp_start': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            'dp_end': {'allow_post': True, 'allow_put': True,
                       'validate': {'type:string': None},
                       'default': '', 'is_visible': True},
            'ip_protocol': {'allow_post': True, 'allow_put': True,
                            'validate': {'type:string': None},
                            'default': '', 'is_visible': True},
            'tenant_id': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},

        }
    },
    'instances': {
        'parent'  : {
                'collection_name': 'appliances',
                'member_name': 'appliance'
            },
        'parameters': {
            'id': {'allow_post': True, 'allow_put': False,
                   'default': None, 'is_visible': True},
            'instance_uuid': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'default': '', 'is_visible': True},
            'network_id': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},
            'vlan_in': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},
            'vlan_out': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},
            'tenant_id': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},
        }
    },
    'zones': {
        'parent': {
            'collection_name': 'chainsets',
            'member_name': 'chainset'
        },
        'parameters': {
            'id': {'allow_post': False, 'allow_put': False,
                   'validate': {'type:regex': attr.UUID_PATTERN},
                   'is_visible': True},
            'zone': {'allow_post': True, 'allow_put': True,
                     'validate': {'type:string': None},
                     'default': '', 'is_visible': True},
            'direction': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'required_by_policy': True,
                         'is_visible': True},
            'chainset_id': {'allow_post': False, 'allow_put': False,
                            'validate': {'type:string': None},
                            'required_by_policy': True,
                            'is_visible': True},
            'tenant_id': {'allow_post': True, 'allow_put': False,
                          'validate': {'type:string': None},
                          'required_by_policy': True,
                          'is_visible': True},
        }
    },
}


class Sfcext(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Network service"

    @classmethod
    def get_alias(cls):
        return "sfc"

    @classmethod
    def get_description(cls):
        return "Extension for Service Function Chaining"

    @classmethod
    def get_namespace(cls):
        return "http://wiki.openstack.org/Crd/LBaaS/API_1.0"

    @classmethod
    def get_updated(cls):
        return "2012-10-07T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        attr.PLURALS.update(SFC_PLURALS)
        resources = []
        plugin = manager.CrdManager.get_service_plugins()[constants.SFC]
        for collection_name in RESOURCE_ATTRIBUTE_MAP:
            #resource_name = collection_name[:-1]
            resource_name = SFC_PLURALS[collection_name]
            parents = None
            path_prefix = None
            parent = None
            if 'parameters' in RESOURCE_ATTRIBUTE_MAP[collection_name]:
                params = RESOURCE_ATTRIBUTE_MAP[collection_name].get(
                    'parameters')
                parent = RESOURCE_ATTRIBUTE_MAP[collection_name].get('parent')
                parents = []
                path_prefix = []

                def generate_parent(parent_attr):
                    parents.append(parent_attr)
                    if parent_attr != parent:
                        path_prefix.insert(0, "/%s/{%s_id}" % (parent_attr['collection_name'], parent_attr['member_name']))
                    if RESOURCE_ATTRIBUTE_MAP[parent_attr['collection_name']].has_key('parent'):
                        generate_parent(RESOURCE_ATTRIBUTE_MAP[parent_attr['collection_name']].get('parent'))
                generate_parent(parent)
                path_prefix = constants.COMMON_PREFIXES[constants.SFC] + \
                              ''.join(path_prefix)
            else:
                params = RESOURCE_ATTRIBUTE_MAP[collection_name]
                path_prefix = constants.COMMON_PREFIXES[constants.SFC]

            member_actions = {}
            controller = base.create_resource(collection_name,
                                              resource_name,
                                              plugin, params,
                                              member_actions=member_actions,
                                              parent=parents)

            resource = extensions.ResourceExtension(
                collection_name,
                controller,
                parent=parent,
                path_prefix=path_prefix,
                member_actions=member_actions,
                attr_map=params)
            resources.append(resource)

        TMP_RESOURCE_ATTRIBUTE_MAP = RESOURCE_ATTRIBUTE_MAP.copy()
        TMP_RESOURCE_ATTRIBUTE_MAP.update(SUB_RESOURCE_ATTRIBUTE_MAP)
        for collection_name in SUB_RESOURCE_ATTRIBUTE_MAP:
            resource_name = SFC_SUB_PLURALS[collection_name]
            parents = None
            path_prefix = None
            parent = None
            if 'parameters' in TMP_RESOURCE_ATTRIBUTE_MAP[collection_name]:
                params = TMP_RESOURCE_ATTRIBUTE_MAP[collection_name].get(
                    'parameters')
                parent = TMP_RESOURCE_ATTRIBUTE_MAP[collection_name].get(
                    'parent')
                parents = []
                path_prefix = []

                def generate_parent(parent_attr):
                    parents.append(parent_attr)
                    if parent_attr != parent:
                        path_prefix.insert(0, "/%s/{%s_id}" % (
                            parent_attr['collection_name'],
                            parent_attr['member_name']))
                    if 'parent' in TMP_RESOURCE_ATTRIBUTE_MAP[parent_attr[
                        'collection_name']]:
                        generate_parent(TMP_RESOURCE_ATTRIBUTE_MAP[parent_attr[
                            'collection_name']].get('parent'))

                generate_parent(parent)
                path_prefix = constants.COMMON_PREFIXES[constants.SFC] + \
                              ''.join(path_prefix)
            else:
                params = TMP_RESOURCE_ATTRIBUTE_MAP[collection_name]
                path_prefix = constants.COMMON_PREFIXES[constants.SFC]

            member_actions = {}
            controller = base.create_resource(collection_name,
                                              resource_name,
                                              plugin, params,
                                              member_actions=member_actions,
                                              parent=parents)

            resource = extensions.ResourceExtension(
                collection_name,
                controller,
                parent=parent,
                path_prefix=path_prefix,
                member_actions=member_actions,
                attr_map=params)
            resources.append(resource)
        return resources

    @classmethod
    def get_plugin_interface(cls):
        return SFCPluginBase


class SFCPluginBase(ServicePluginBase):
    __metaclass__ = abc.ABCMeta

    def get_plugin_name(self):
        return constants.SFC

    def get_plugin_type(self):
        return constants.SFC

    def get_plugin_description(self):
        return 'Service Function chain plugin'

    @abc.abstractmethod
    def get_networkfunctions(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_networkfunction(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_networkfunction(self, context, networkfunction):
        pass

    @abc.abstractmethod
    def update_networkfunction(self, context, id, networkfunction):
        pass

    @abc.abstractmethod
    def delete_networkfunction(self, context, id):
        pass

    @abc.abstractmethod
    def get_categories(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_category(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_category(self, context, category):
        pass

    @abc.abstractmethod
    def update_category(self, context, id, category):
        pass

    @abc.abstractmethod
    def delete_category(self, context, id):
        pass

    @abc.abstractmethod
    def get_category_nf_map(self, context, category_id, networkfunction_id, fields=None):
        pass

    @abc.abstractmethod
    def create_category_nf_map(self, context, category_networkfunction, category_id):
        pass

    @abc.abstractmethod
    def delete_category_nf_map(self, context, category_id, networkfunction_id):
        pass

    @abc.abstractmethod
    def get_vendors(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_vendor(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_vendor(self, context, vendor):
        pass

    @abc.abstractmethod
    def update_vendor(self, context, id, vendor):
        pass

    @abc.abstractmethod
    def delete_vendor(self, context, id):
        pass

    @abc.abstractmethod
    def get_appliances(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_appliance(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_appliance(self, context, appliance):
        pass

    @abc.abstractmethod
    def update_appliance(self, context, id, appliance):
        pass

    @abc.abstractmethod
    def delete_appliance(self, context, id):
        pass

    @abc.abstractmethod
    def get_chains(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_chain(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_chain(self, context, chain):
        pass

    @abc.abstractmethod
    def update_chain(self, context, id, chain):
        pass

    @abc.abstractmethod
    def delete_chain(self, context, id):
        pass

    # Chainmap Related
    def get_chainmaps(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_chainmap(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_chainmap(self, context, chainmap):
        pass

    @abc.abstractmethod
    def update_chainmap(self, context, id, chainmap):
        pass

    @abc.abstractmethod
    def delete_chainmap(self, context, id):
        pass

    @abc.abstractmethod
    def get_chain_appliances(self, context, filters=None, fields=None, chain_id=None):
        pass

    @abc.abstractmethod
    def get_chain_appliance(self, context, id, chain_id, fields=None):
        pass

    @abc.abstractmethod
    def create_chain_appliance(self, context, appliance_map, chain_id):
        pass

    @abc.abstractmethod
    def update_chain_appliance(self, context, id, chain_id, appliance_map):
        pass

    @abc.abstractmethod
    def delete_chain_appliance(self, context, id, chain_id):
        pass

    @abc.abstractmethod
    def get_config_handles(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_config_handle(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_config_handle(self, context, config_handle):
        pass

    @abc.abstractmethod
    def update_config_handle(self, context, id, config_handle):
        pass

    @abc.abstractmethod
    def delete_config_handle(self, context, id):
        pass

    @abc.abstractmethod
    def create_launch(self, context, launch):
        pass

    @abc.abstractmethod
    def get_vlanquotas(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_vlanquota(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_vlanquota(self, context, vlanquota):
        pass

    @abc.abstractmethod
    def update_vlanquota(self, context, id, vlanquota):
        pass

    @abc.abstractmethod
    def delete_vlanquota(self, context, id):
        pass
    
    @abc.abstractmethod
    def create_vmscaleout(self, context, vmscaleout):
        pass
