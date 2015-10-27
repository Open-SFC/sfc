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
from nscs.ocas_utils.openstack.common.gettextutils import _
from nscs.ocas_utils.openstack.common import log as logging
from nscs.ocas_utils.openstack.common import context
from nscs.ocas_utils.openstack.common.rpc import proxy
from sfc.crdconsumer.client import ocas_client

LOG = logging.getLogger(__name__)


class SFCConsumerPlugin(proxy.RpcProxy):
    """
    Implementation of the Crd Consumer Core Network Service Plugin.
    """
    RPC_API_VERSION = '1.0'
    
    def __init__(self):
        super(SFCConsumerPlugin,self).__init__(topic="crd-service-queue",default_version=self.RPC_API_VERSION)
        self.uc = ocasclient()
        self.listener_topic = 'crd-listener'
        # RPC network init
        self.consumer_context = context.RequestContext('crd', 'crd',
                                                       is_admin=False)
        
    def get_plugin_type(self):
        return "SFC"
    
    def init_consumer(self, consumer=None):
        delta_msg = {}
        try:
            delta_msg = self.call(self.consumer_context,self.make_msg('sfc_init_consumer',consumer=consumer),self.listener_topic)
        except BaseException,msg1:
            LOG.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            LOG.error(_("Exception raised when running method - sfc_init_consumer with msg '%s'"), msg1)
        return delta_msg

    def build_ucm_wsgi_msg(self, payload, message_type=None):
        msg = {}
        if message_type == 'create_chain':
            chain_name = payload.get('name')
            chain_name = payload.get('chain_id')[:16]
            chain_name = payload.get('name') + "_" + chain_name
            tenant = payload.get('tenant_id')
            msg = {"chain":{"name": chain_name,
                    "id": payload.get('chain_id'),
                    "tenant": tenant,
                    "admin_status": True,
                   }
            }
        elif message_type == 'update_chain':
            chain_name = payload.get('name')
            chain_name = payload.get('chain_id')[:16]
            chain_name = payload.get('name') + "_" + chain_name

            msg = {"chain":{"name": chain_name,
                   "admin_status": True,
                   }
            }
        elif message_type == 'create_chain_bypass_rule':
            bypass_rule_name = payload.get('name')
            bypass_rule_name = payload.get('chain_bypass_rule_id')[:16]
            bypass_rule_name = payload.get('name') + "_" + bypass_rule_name
            tenant = payload.get('tenant_id')
            chain_id = payload.get('chain_id')
            src_mac_type = payload.get('src_mac_type')
            dest_mac_type = payload.get('dest_mac_type')
            src_mac = payload.get('src_mac')
            dest_mac = payload.get('dest_mac')
            sip_type = payload.get('sip_type')
            dip_type = payload.get('dip_type')
            sip_start = payload.get('sip_start')
            sip_end = payload.get('sip_end')
            dip_start = payload.get('dip_start')
            dip_end = payload.get('dip_end')
            sp_type = payload.get('sp_type')
            dp_type = payload.get('dp_type')
            sp_start = payload.get('sp_start')
            sp_end = payload.get('sp_end')
            dp_start = payload.get('dp_start')
            dp_end = payload.get('dp_end')
            eth_type = payload.get('eth_type')
            eth_value = payload.get('eth_value')
            ip_protocol = payload.get('ip_protocol')
            nwservice_count = payload.get('nwservice_count')
            nwservice_names = payload.get('nwservice_names')
            
            msg = {"chain_bypass_rule":{"name": bypass_rule_name,
                    "id": payload.get('chain_bypass_rule_id'),
                    "tenant": tenant,
                    "chain_id": chain_id,
                    "protocol": ip_protocol,
                    "nwservice_count": nwservice_count,
                    "nwservice_names": nwservice_names,
                    "admin_status": True,
                    }
            }
            
            ##Eth Type
            if eth_type.lower() == 'value':
                msg['chain_bypass_rule'].update({'eth_value' : eth_value,
                                                 'eth_type': 'Single'})
            else:
                msg['chain_bypass_rule'].update({'eth_type':'Any'})
            
            ##Mach Address    
            if src_mac_type.lower() == 'value':
                msg['chain_bypass_rule'].update({'src_mac':src_mac,
                    'src_mac_type': 'Single'})
            else:
                msg['chain_bypass_rule'].update({'src_mac_type': 'Any'})
                
            if dest_mac_type.lower() == 'value':
                msg['chain_bypass_rule'].update({'dst_mac':dest_mac,
                    'dst_mac_type': 'Single'})
            else:
                msg['chain_bypass_rule'].update({'dst_mac_type': 'Any'})
                
            ##IP Address
            if sip_type.lower() == 'single':
                msg['chain_bypass_rule'].update({'sip_type': sip_type,
                                                  'sip_start': sip_start,
                                                  'sip_end': sip_start})
            elif sip_type.lower() in ['range', 'subnet']:
                msg['chain_bypass_rule'].update({'sip_type': sip_type,
                                                  'sip_start': sip_start,
                                                  'sip_end': sip_end})
            else:
                msg['chain_bypass_rule'].update({'sip_type':'Any'})
                
            if dip_type.lower() == 'single':
                msg['chain_bypass_rule'].update({'dip_type': dip_type,
                                                  'sip_start': dip_start,
                                                  'dip_end': dip_start})
            elif dip_type.lower() in ['range', 'subnet']:
                msg['chain_bypass_rule'].update({'dip_type': dip_type,
                                                  'dip_start': dip_start,
                                                  'dip_end': dip_end})
            else:
                msg['chain_bypass_rule'].update({'dip_type':'Any'})
                
            ##Port
            if sp_type.lower() == 'single':
                msg['chain_bypass_rule'].update({'sp_type':sp_type,
                                                  'sp_start':sp_start,
                                                  'sp_end':sp_start})
            elif sp_type.lower() == 'range':
                msg['chain_bypass_rule'].update({'sp_type':sp_type,
                                                  'sp_start':sp_start,
                                                  'sp_end':sp_end})
            else:
                msg['chain_bypass_rule'].update({'sp_type':'Any'})
                
            if dp_type.lower() == 'single':
                msg['chain_bypass_rule'].update({'dp_type':dp_type,
                                                  'dp_start':dp_start,
                                                  'dp_end':dp_start})
            elif dp_type.lower() == 'range':
                msg['chain_bypass_rule'].update({'dp_type':dp_type,
                                                  'dp_start':dp_start,
                                                  'dp_end':dp_end})
            else:
                msg['chain_bypass_rule'].update({'dp_type':'Any'})
            
        elif message_type == 'update_chain_bypass_rule':
            bypass_rule_name = payload.get('name')
            bypass_rule_name = payload.get('chain_bypass_rule_id')[:16]
            bypass_rule_name = payload.get('name') + "_" + bypass_rule_name
            chain_id = payload.get('chain_id')
            src_mac_type = payload.get('src_mac_type')
            dest_mac_type = payload.get('dest_mac_type')
            src_mac = payload.get('src_mac')
            dest_mac = payload.get('dest_mac')
            sip_type = payload.get('sip_type')
            dip_type = payload.get('dip_type')
            sip_start = payload.get('sip_start')
            sip_end = payload.get('sip_end')
            dip_start = payload.get('dip_start')
            dip_end = payload.get('dip_end')
            sp_type = payload.get('sp_type')
            dp_type = payload.get('dp_type')
            sp_start = payload.get('sp_start')
            sp_end = payload.get('sp_end')
            dp_start = payload.get('dp_start')
            dp_end = payload.get('dp_end')
            eth_type = payload.get('eth_type')
            eth_value = payload.get('eth_value')
            ip_protocol = payload.get('ip_protocol')
            nwservice_count = payload.get('nwservice_count')
            nwservice_names = payload.get('nwservice_names')
            
            msg = {"chain_bypass_rule":{"name": bypass_rule_name,
                    "chain_id": chain_id,
                    "protocol": ip_protocol,
                    "nwservice_count": nwservice_count,
                    "nwservice_names": nwservice_names,
                    "admin_status": True,
                   }
            }
        elif message_type == 'create_service':
            service_name = payload.get('name')
            service_name = payload.get('appliance_id')[:16]
            service_name = payload.get('name') + "_" + service_name
            tenant = payload.get('tenant_id')
            form_factor_type = payload.get('form_factor_type')
            type = payload.get('type')
            load_share_algorithm = payload.get('load_share_algorithm')
            high_threshold = payload.get('high_threshold')
            low_threshold = payload.get('low_threshold')
            pkt_field_to_hash = payload.get('pkt_field_to_hash')
            load_indication_type = payload.get('load_indication_type')
            state = payload.get('admin_state_up')

            load_share_algorithm = load_share_algorithm.replace(' ', '_')
            type = type.upper()
            type = type.replace('-MODE', '')

            if load_indication_type == 'CONNECTION_BASED':
                load_indication_type = 'Connection_Based'
            elif load_indication_type == 'TRAFFIC_BASED':
                load_indication_type = 'Traffic_Based'
            
            msg = {"service":{"name": service_name,
                    "id": payload.get('appliance_id'),
                    "tenant": tenant,
                    "form_factor_type": form_factor_type,
                    "type": type,
                    "load_share_algorithm": load_share_algorithm,
                    "high_threshold": high_threshold,
                    "low_threshold": low_threshold,
                    "pkt_field_to_hash": pkt_field_to_hash,
                    "load_indication_type": load_indication_type,
                    "admin_status": True,
                   }
            }
        elif message_type == 'update_service':
            service_name = payload.get('name')
            service_name = payload.get('appliance_id')[:16]
            service_name = payload.get('name') + "_" + service_name
            form_factor_type = payload.get('form_factor_type')
            
            msg = {"service":{"name": service_name,
                    "form_factor_type": form_factor_type,
                    "admin_status": True,
                   }
            }
        elif message_type == 'create_chain_service':
            seq_number = payload.get('sequence_number')
            
            msg = {"chain_service":{"id": payload.get('chain_appliance_map_id'),
                    "service_id": payload.get('appliance_id'),
                    "sequence_number": seq_number,
                   }
            }
        elif message_type == 'update_chain_service':
            seq_number = payload.get('sequence_number')
            
            msg = {"chain_service":{"sequence_number": seq_number,
                   }
            }
        elif message_type == 'create_chain_set':
            chain_set_name = payload.get('name')
            chain_set_name = payload.get('chainset_id')[:16]
            chain_set_name = payload.get('name') + "_" + chain_set_name
            tenant = payload.get('tenant_id')
            zonefull = payload.get('zonefull')
            direction = payload.get('direction')

            msg = {"chain_set":{"name": chain_set_name,
                                "zonefull": zonefull,
                                "id": payload.get('chainset_id'),
                                "tenant": tenant,
                                "admin_status": True,
                                "direction": direction
                                }
                }
        elif message_type == 'update_chain_set':
            chain_set_name = payload.get('name')
            chain_set_name = payload.get('chainset_id')[:16]
            chain_set_name = payload.get('name') + "_" + chain_set_name
            zonefull = payload.get('zonefull')
            direction = payload.get('direction')

            msg = {"chain_set":{"name": chain_set_name,
                    "admin_status": True,
                    "zonefull": zonefull,
                    "direction": direction
                   }
            }
        elif message_type == 'create_chain_selection_rule':
            selection_rule_name = payload.get('name')
            selection_rule_name = payload.get('chain_rule_id')[:16]
            selection_rule_name = payload.get('name') + "_" + selection_rule_name
            tenant = payload.get('tenant_id')
            chain_id = payload.get('chain_id')
            chain_set_id = payload.get('chainset_id')
            src_mac_type = payload.get('src_mac_type')
            dest_mac_type = payload.get('dest_mac_type')
            src_mac = payload.get('src_mac')
            dest_mac = payload.get('dest_mac')
            sip_type = payload.get('sip_type')
            dip_type = payload.get('dip_type')
            sip_start = payload.get('sip_start')
            sip_end = payload.get('sip_end')
            dip_start = payload.get('dip_start')
            dip_end = payload.get('dip_end')
            sp_type = payload.get('sp_type')
            dp_type = payload.get('dp_type')
            sp_start = payload.get('sp_start')
            sp_end = payload.get('sp_end')
            dp_start = payload.get('dp_start')
            dp_end = payload.get('dp_end')
            eth_type = payload.get('eth_type')
            eth_value = payload.get('eth_value')
            ip_protocol = payload.get('ip_protocol')
            
            msg = {"chain_selection_rule":{"name": selection_rule_name,
                    "id": payload.get('chain_rule_id'),
                    "tenant": tenant,
                    "chain_id": chain_id,
                    "chain_set_id": chain_set_id,
                    "protocol": ip_protocol,
                    "admin_status": True,
                   }
            }
            
            ##Eth Type
            if eth_type.lower() == 'value':
                msg['chain_selection_rule'].update({'eth_value' : eth_value,
                                                 'eth_type': 'Single'})
            else:
                msg['chain_selection_rule'].update({'eth_type':'Any'})
            
            ##Mach Address    
            if src_mac_type.lower() == 'value':
                msg['chain_selection_rule'].update({'src_mac':src_mac,
                    'src_mac_type': 'Single'})
            else:
                msg['chain_selection_rule'].update({'src_mac_type': 'Any'})
                
            if dest_mac_type.lower() == 'value':
                msg['chain_selection_rule'].update({'dst_mac':dest_mac,
                    'dst_mac_type': 'Single'})
            else:
                msg['chain_selection_rule'].update({'dst_mac_type': 'Any'})
                
            ##IP Address
            if sip_type.lower() == 'single':
                msg['chain_selection_rule'].update({'sip_type': sip_type,
                                                  'sip_start': sip_start,
                                                  'sip_end': sip_start})
            elif sip_type.lower() in ['range', 'subnet']:
                msg['chain_selection_rule'].update({'sip_type': sip_type,
                                                  'sip_start': sip_start,
                                                  'sip_end': sip_end})
            else:
                msg['chain_selection_rule'].update({'sip_type':'Any'})
                
            if dip_type.lower() == 'single':
                msg['chain_selection_rule'].update({'dip_type': dip_type,
                                                  'dip_start': dip_start,
                                                  'dip_end': dip_start})
            elif dip_type.lower() in ['range', 'subnet']:
                msg['chain_selection_rule'].update({'dip_type': dip_type,
                                                  'dip_start': dip_start,
                                                  'dip_end': dip_end})
            else:
                msg['chain_selection_rule'].update({'dip_type':'Any'})
                
            ##Port
            if sp_type.lower() == 'single':
                msg['chain_selection_rule'].update({'sp_type':sp_type,
                                                  'sp_start':sp_start,
                                                  'sp_end':sp_start})
            elif sp_type.lower() == 'range':
                msg['chain_selection_rule'].update({'sp_type':sp_type,
                                                  'sp_start':sp_start,
                                                  'sp_end':sp_end})
            else:
                msg['chain_selection_rule'].update({'sp_type':'Any'})
                
            if dp_type.lower() == 'single':
                msg['chain_selection_rule'].update({'dp_type':dp_type,
                                                  'dp_start':dp_start,
                                                  'dp_end':dp_start})
            elif dp_type.lower() == 'range':
                msg['chain_selection_rule'].update({'dp_type':dp_type,
                                                  'dp_start':dp_start,
                                                  'dp_end':dp_end})
            else:
                msg['chain_selection_rule'].update({'dp_type':'Any'})
            
        elif message_type == 'update_chain_selection_rule':
            selection_rule_name = payload.get('name')
            selection_rule_name = payload.get('chain_rule_id')[:16]
            selection_rule_name = payload.get('name') + "_" + selection_rule_name
            chain_id = payload.get('chain_id')
            chain_set_id = payload.get('chainset_id')
            src_mac_type = payload.get('src_mac_type')
            dest_mac_type = payload.get('dest_mac_type')
            src_mac = payload.get('src_mac')
            dest_mac = payload.get('dest_mac')
            sip_type = payload.get('sip_type')
            dip_type = payload.get('dip_type')
            sip_start = payload.get('sip_start')
            sip_end = payload.get('sip_end')
            dip_start = payload.get('dip_start')
            dip_end = payload.get('dip_end')
            sp_type = payload.get('sp_type')
            dp_type = payload.get('dp_type')
            sp_start = payload.get('sp_start')
            sp_end = payload.get('sp_end')
            dp_start = payload.get('dp_start')
            dp_end = payload.get('dp_end')
            eth_type = payload.get('eth_type')
            eth_value = payload.get('eth_value')
            ip_protocol = payload.get('ip_protocol')
            
            msg = {"chain_selection_rule":{"name": selection_rule_name,
                    "chain_id": chain_id,
                    "chain_set_id": chain_set_id,
                    "protocol": ip_protocol,
                    "admin_status": True,
                   }
            }
        elif message_type == 'create_chain_network':
            chain_network_name = payload.get('name')
            chain_network_name = payload.get('chain_map_id')[:16]
            chain_network_name = payload.get('name') + "_" + chain_network_name
            tenant = payload.get('tenant_id')

            chain_set_id = payload.get('chainset_id')
            inbound_networks = payload.get('inbound_network_id')
            outbound_networks = payload.get('outbound_network_id')
            
            msg = {"chain_network":{"name": chain_network_name,
                    "id": payload.get('chain_map_id'),
                    "tenant": tenant,
                    "chain_set_id": chain_set_id,
                    "inbound_network": inbound_networks,
                    "outbound_network": outbound_networks,
                    "admin_status": True,
                   }
            }
        elif message_type == 'update_chain_network':
            chain_network_name = payload.get('name')
            chain_network_name = payload.get('chain_map_id')[:16]
            chain_network_name = payload.get('name') + "_" + chain_network_name

            chain_set_id = payload.get('chainset_id')
            inbound_networks = payload.get('inbound_network_id')
            outbound_networks = payload.get('outbound_network_id')
            state = payload.get('admin_state_up')
            
            msg = {"chain_network":{"name": chain_network_name,
                   "chain_set_id": chain_set_id,
                   "inbound_networks": inbound_networks,
                   "outbound_networks": outbound_networks,
                   "admin_status": True,
                   }
            }
        elif message_type == 'create_vlan_pair':
            msg = {"service_instance":{"id": payload.get('vlan_pair_id'),
                                       "vlan_in": payload.get('vlan_in'),
                                       "vlan_out": payload.get('vlan_out'),
                                       "instance_id": payload.get('instance_id'),
                                       "chain_service_id": payload.get('chain_appliance_id'),
                                       #"tenant": tenant,
                                       #"admin_status": state,
                   }
            }
        elif message_type == 'update_vlan_pair':
            msg = {"service_instance":{"vlan_in": payload.get('vlan_in'),
                                       "vlan_out": payload.get('vlan_out'),
                                       "instance_id": payload.get('instance_id'),
                                       "chain_service_id": payload.get('chain_appliance_id'),
                   }
            }
        elif message_type == 'create_appliance_instance':
            tenant = payload.get('tenant_id')
            msg = {"service_instance":{"id": payload.get('appliance_instance_id'),
                                         "chain_appliance_id": payload.get('chain_appliance_id'),
                                         "instance_id": payload.get('instance_uuid'),
                                         "network_id": payload.get('network_id'),
                                         "vlan_in": payload.get('vlan_in'),
                                         "vlan_out": payload.get('vlan_out'),
                                         "tenant": tenant,
                                         }
                }
        elif message_type == 'update_appliance_instance':
            msg = {"service_instance":
                       {
                           "chain_appliance_id": payload.get(
                               'chain_appliance_id'),
                           "instance_id": payload.get('instance_uuid'),
                           "network_id": payload.get('network_id'),
                           "vlan_in": payload.get('vlan_in'),
                           "vlan_out": payload.get('vlan_out'),
                       }
            }
        elif message_type == 'create_chainset_zone':
            tenant = payload.get('tenant_id')
            zone_id = payload.get('zone_id')
            zone = payload.get('zone')
            direction = payload.get('direction')
            chain_set_id = payload.get('chainset_id')
            
            msg = {"chainset_zone":{"name": zone,
                    "id": zone_id,
                    "direction": direction,
                    "chain_set_id": chain_set_id,
                    "tenant": tenant,
                   }
            }
        elif message_type == 'update_chainset_zone':
            tenant = payload.get('tenant_id')
            zone_id = payload.get('zone_id')
            zone = payload.get('zone')
            direction = payload.get('direction')
            chain_set_id = payload.get('chainset_id')
            msg = {"chainset_zone":{"name": zone,
                    "direction": direction,
                    "chain_set_id": chain_set_id,
                   }
            }
            
        return msg
    
    
    ###
    ###Chains
    ###
    def create_chain(self, context, **kwargs):
        #LOG.info(_("Create Chain Body - %s"), str(kwargs))
        payload = kwargs['payload']
        body = self.build_ucm_wsgi_msg(payload, 'create_chain')
        self.uc.create_chain(body=body)
        
    def delete_chain(self, context, **kwargs):
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        #LOG.info(_("Delete Chain Name- %s"), str(chain_id))
        self.uc.delete_chain(chain_id)
        
    def update_chain(self, context, **kwargs):
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_chain')
        #LOG.info(_("Update Chain ID- %s and body=%s"), str(chain_id), str(body))
        self.uc.update_chain(chain_id, body=body)
        
    def get_chains(self, **params):
        #LOG.info(_("List Virtual Networks"))
        self.uc.list_chains(**params)
        
    def get_chain(self, payload, **params):
        chain_id = payload.get('chain_id')
        #LOG.info(_("Show Chain Details for - %s"), str(chain_id))
        self.uc.show_chain(chain_id, **params)
        
    ###
    ###Chain Bypass rules
    ###
    def create_chain_bypass_rules(self, context, **kwargs):
        #LOG.info(_("Create chain_bypass_rule Body - %s"), str(kwargs))
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        body = self.build_ucm_wsgi_msg(payload, 'create_chain_bypass_rule')
        self.uc.create_chain_bypass_rule(chain_id, body=body)
        
    def delete_chain_bypass_rules(self, context, **kwargs):
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        chain_bypass_rule_id = payload.get('chain_bypass_rule_id')
        #LOG.info(_("Delete chain_bypass_rule Name- %s"), str(chain_bypass_rule_id))
        self.uc.delete_chain_bypass_rule(chain_id, chain_bypass_rule_id)
        
    def update_chain_bypass_rules(self, context, **kwargs):
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        chain_bypass_rule_id = payload.get('chain_bypass_rule_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_chain_bypass_rule')
        #LOG.info(_("Update chain_bypass_rule ID- %s and body=%s"), str(chain_bypass_rule_id), str(body))
        self.uc.update_chain_bypass_rule(chain_id, chain_bypass_rule_id, body=body)
        
    def get_chain_bypass_rules(self, payload, **params):
        chain_id = payload.get('chain_id')
        self.uc.list_chain_bypass_rules(chain_id, **params)
        
    def get_chain_bypass_rule(self, payload, **params):
        chain_id = payload.get('chain_id')
        chain_bypass_rule_id = payload.get('chain_bypass_rule_id')
        #LOG.info(_("Show chain_bypass_rule Details for - %s"), str(chain_bypass_rule_id))
        self.uc.show_chain_bypass_rule(chain_id, chain_bypass_rule_id, **params)
    
    ###
    ###Services
    ###
    def create_appliance(self, context, **kwargs):
        payload = kwargs['payload']
        body = self.build_ucm_wsgi_msg(payload, 'create_service')
        # LOG.info(_("Create service Body - %s"), str(body))
        self.uc.create_service(body=body)
        
    def delete_appliance(self, context, **kwargs):
        payload = kwargs['payload']
        service_id = payload.get('appliance_id')
        #LOG.info(_("Delete service Name- %s"), str(service_id))
        self.uc.delete_service(service_id)
        
    def update_appliance(self, context, **kwargs):
        payload = kwargs['payload']
        service_id = payload.get('appliance_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_service')
        #LOG.info(_("Update service ID- %s and body=%s"), str(service_id), str(body))
        self.uc.update_service(service_id, body=body)
        
    def get_appliances(self, **params):
        #LOG.info(_("List Virtual Networks"))
        self.uc.list_services(**params)
        
    def get_appliance(self, payload, **params):
        service_id = payload.get('appliance_id')
        #LOG.info(_("Show service Details for - %s"), str(service_id))
        self.uc.show_service(service_id, **params)
        
    ###
    ###chain_services
    ###
    def create_chain_appliance(self, context, **kwargs):
        #LOG.info(_("Create chain_service Body - %s"), str(kwargs))
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        body = self.build_ucm_wsgi_msg(payload, 'create_chain_service')
        self.uc.create_chain_service(chain_id, body=body)
        
    def delete_chain_appliance(self, context, **kwargs):
        payload = kwargs['payload']
        chain_service_id = payload.get('chain_appliance_map_id')
        chain_id = payload.get('chain_id')
        #LOG.info(_("Delete chain_service Name- %s"), str(chain_service_id))
        self.uc.delete_chain_service(chain_id, chain_service_id)
        
    def update_chain_appliance(self, context, **kwargs):
        payload = kwargs['payload']
        chain_service_id = payload.get('chain_appliance_map_id')
        chain_id = payload.get('chain_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_chain_service')
        #LOG.info(_("Update chain_service ID- %s and body=%s"), str(chain_service_id), str(body))
        self.uc.update_chain_service(chain_id, chain_service_id, body=body)
        
    def get_chain_appliances(self, **params):
        #LOG.info(_("List Virtual Networks"))
        chain_id = params.get('chain_id')
        self.uc.list_chain_services(chain_id, **params)
        
    def get_chain_appliance(self, payload, **params):
        chain_service_id = payload.get('chain_appliance_map_id')
        chain_id = payload.get('chain_id')
        #LOG.info(_("Show chain_service Details for - %s"), str(chain_service_id))
        self.uc.show_chain_service(chain_id, chain_service_id, **params)
        
    ###
    ###chain_sets
    ###
    def create_chainsets(self, context, **kwargs):

        payload = kwargs['payload']
        LOG.info(_("Create chain_set Body - %s"), str(payload))
        body = self.build_ucm_wsgi_msg(payload, 'create_chain_set')
        LOG.info(_("Create chain_set Body - %s"), str(body))
        self.uc.create_chain_set(body=body)
        
    def delete_chainsets(self, context, **kwargs):
        payload = kwargs['payload']
        chain_set_id = payload.get('chainset_id')
        #LOG.info(_("Delete chain_set Name- %s"), str(chain_set_id))
        self.uc.delete_chain_set(chain_set_id)
        
    def update_chainsets(self, context, **kwargs):
        payload = kwargs['payload']
        chain_set_id = payload.get('chainset_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_chain_set')
        #LOG.info(_("Update chain_set ID- %s and body=%s"), str(chain_set_id), str(body))
        self.uc.update_chain_set(chain_set_id, body=body)
        
    def get_chain_sets(self, **params):
        #LOG.info(_("List Virtual Networks"))
        self.uc.list_chain_sets(**params)
        
    def get_chain_set(self, payload, **params):
        chain_set_id = payload.get('chainset_id')
        #LOG.info(_("Show chain_set Details for - %s"), str(chain_set_id))
        self.uc.show_chain_set(chain_set_id, **params)
        
    ###
    ###chain_selection_rules
    ###
    def create_chainrule(self, context, **kwargs):
        #LOG.info(_("Create chain_selection_rule Body - %s"), str(kwargs))
        payload = kwargs['payload']
        chain_set_id = payload.get('chainset_id')
        body = self.build_ucm_wsgi_msg(payload, 'create_chain_selection_rule')
        self.uc.create_chain_selection_rule(chain_set_id, body=body)
        
    def delete_chainrule(self, context, **kwargs):
        payload = kwargs['payload']
        chain_set_id = payload.get('chainset_id')
        chain_selection_rule_id = payload.get('chain_rule_id')
        #LOG.info(_("Delete chain_selection_rule Name- %s"), str(chain_selection_rule_id))
        self.uc.delete_chain_selection_rule(chain_set_id, chain_selection_rule_id)
        
    def update_chainrule(self, context, **kwargs):
        payload = kwargs['payload']
        chain_set_id = payload.get('chainset_id')
        chain_selection_rule_id = payload.get('chain_rule_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_chain_selection_rule')
        #LOG.info(_("Update chain_selection_rule ID- %s and body=%s"), str(chain_selection_rule_id), str(body))
        self.uc.update_chain_selection_rule(chain_set_id, chain_selection_rule_id, body=body)
        
    def get_chainrules(self, payload, **params):
        #LOG.info(_("List Virtual Networks"))
        chain_set_id = payload.get('chainset_id')
        self.uc.list_chain_selection_rules(chain_set_id, **params)
        
    def get_chainrule(self, payload, **params):
        chain_set_id = payload.get('chainset_id')
        chain_selection_rule_id = payload.get('chain_rule_id')
        #LOG.info(_("Show chain_selection_rule Details for - %s"), str(chain_selection_rule_id))
        self.uc.show_chain_selection_rule(chain_set_id, chain_selection_rule_id, **params)
        
    ###
    ###chain_networks
    ###
    def create_chainmap(self, context, **kwargs):
        #LOG.info(_("Create chain_network Body - %s"), str(kwargs))
        payload = kwargs['payload']
        body = self.build_ucm_wsgi_msg(payload, 'create_chain_network')
        self.uc.create_chain_network(body=body)
        
    def delete_chainmap(self, context, **kwargs):
        payload = kwargs['payload']
        chain_network_id = payload.get('chain_map_id')
        #LOG.info(_("Delete chain_network Name- %s"), str(chain_network_id))
        self.uc.delete_chain_network(chain_network_id)
        
    def update_chainmap(self, context, **kwargs):
        payload = kwargs['payload']
        chain_network_id = payload.get('chain_map_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_chain_network')
        #LOG.info(_("Update chain_network ID- %s and body=%s"), str(chain_network_id), str(body))
        self.uc.update_chain_network(chain_network_id, body=body)
        
    def get_chainmaps(self, **params):
        #LOG.info(_("List Virtual Networks"))
        self.uc.list_chain_networks(**params)
        
    def get_chainmap(self, payload, **params):
        chain_network_id = payload.get('chain_map_id')
        #LOG.info(_("Show chain_network Details for - %s"), str(chain_network_id))
        self.uc.show_chain_network(chain_network_id, **params)
        
    ###
    ###VLAN Pairs
    ###
    def create_vlan_pair(self, context, **kwargs):
        LOG.info(_("Create VLAN Pair Body - %s"), str(kwargs))
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        chain_map_id = payload.get('chain_appliance_id')
        body = self.build_ucm_wsgi_msg(payload, 'create_vlan_pair')
        self.uc.create_vlan_pair(chain_id, chain_map_id, body=body)
        
    def delete_vlan_pair(self, context, **kwargs):
        payload = kwargs['payload']
        vlan_pair_id = payload.get('vlan_pair_id')
        chain_id = payload.get('chain_id')
        chain_map_id = payload.get('chain_appliance_id')
        #LOG.info(_("Delete Chain Name- %s"), str(vlan_pair_id))
        self.uc.delete_vlan_pair(chain_id, chain_map_id, vlan_pair_id)
        
    def update_vlan_pair(self, context, **kwargs):
        payload = kwargs['payload']
        vlan_pair_id = payload.get('vlan_pair_id')
        chain_id = payload.get('chain_id')
        chain_map_id = payload.get('chain_appliance_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_vlan_pair')
        #LOG.info(_("Update Chain ID- %s and body=%s"), str(vlan_pair_id), str(body))
        self.uc.update_vlan_pair(chain_id, chain_map_id, vlan_pair_id, body=body)
        
    def get_vlan_pairs(self, **params):
        #LOG.info(_("List Virtual Networks"))
        self.uc.list_vlan_pairs(**params)
        
    def get_vlan_pair(self, payload, **params):
        vlan_pair_id = payload.get('vlan_pair_id')
        chain_id = payload.get('chain_id')
        chain_map_id = payload.get('chain_appliance_id')
        #LOG.info(_("Show Chain Details for - %s"), str(vlan_pair_id))
        self.uc.show_vlan_pair(chain_id, chain_map_id, vlan_pair_id, **params)
        
    ###
    ###appliance_instances
    ###
    def create_appliance_instance(self, context, **kwargs):
        LOG.info(_("Create appliance_instance Body - %s"), str(kwargs))
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        #chain_map_id = payload.get('chain_appliance_id')
        chain_map_id = payload.get('appliance_map_id')
        body = self.build_ucm_wsgi_msg(payload, 'create_appliance_instance')
        self.uc.create_appliance_instance(chain_id, chain_map_id, body=body)
        
    def delete_appliance_instance(self, context, **kwargs):
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        chain_map_id = payload.get('chain_appliance_id')
        appliance_instance_id = payload.get('appliance_instance_id')
        LOG.info(_("Delete appliance_instance Name- %s"),
                 str(appliance_instance_id))
        self.uc.delete_appliance_instance(chain_id, chain_map_id,
                                          appliance_instance_id)
        
    def update_appliance_instance(self, context, **kwargs):
        payload = kwargs['payload']
        chain_id = payload.get('chain_id')
        chain_map_id = payload.get('chain_appliance_id')
        appliance_instance_id = payload.get('appliance_instance_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_appliance_instance')
        LOG.info(_("Update appliance_instance ID- %s and body=%s"),
                 str(appliance_instance_id), str(body))
        self.uc.update_appliance_instance(chain_id, chain_map_id,
                                          appliance_instance_id,
                                          body=body)
        
    def get_appliance_instances(self, **params):
        LOG.info(_("List Appliance Instances"))
        payload = params['payload']
        chain_id = payload.get('chain_id')
        chain_map_id = payload.get('chain_appliance_id')
        self.uc.list_appliance_instances(chain_id, chain_map_id, **params)
        
    def get_appliance_instance(self, payload, **params):
        LOG.info(_("Show appliance_instance Details for - %s"),
                 str(payload.get('appliance_instance_id')))
        chain_id = payload.get('chain_id')
        chain_map_id = payload.get('chain_appliance_id')
        appliance_instance_id = payload.get('appliance_instance_id')
        self.uc.show_appliance_instance(chain_id, chain_map_id,
                                        appliance_instance_id,
                                        **params)
    
    ###
    ###Chainset to Zone - Direction Mappings
    ###
    def create_chainset_zone(self, context, **kwargs):
        payload = kwargs['payload']
        chain_set_id = payload.get('chainset_id')
        body = self.build_ucm_wsgi_msg(payload, 'create_chainset_zone')
        #LOG.info(_("Create chainset_zone Body - %s"), str(body))
        self.uc.create_chainset_zone(chain_set_id, body=body)
        
    def delete_chainset_zone(self, context, **kwargs):
        payload = kwargs['payload']
        chain_set_id = payload.get('chainset_id')
        chainset_zone_id = payload.get('zone_id')
        #LOG.info(_("Delete chainset_zone Name- %s"), str(chainset_zone_id))
        self.uc.delete_chainset_zone(chain_set_id, chainset_zone_id)
        
    def update_chainset_zone(self, context, **kwargs):
        payload = kwargs['payload']
        chain_set_id = payload.get('chainset_id')
        chainset_zone_id = payload.get('zone_id')
        body = self.build_ucm_wsgi_msg(payload, 'update_chainset_zone')
        #LOG.info(_("Update chainset_zone ID- %s and body=%s"), str(chainset_zone_id), str(body))
        self.uc.update_chainset_zone(chain_set_id, chainset_zone_id, body=body)
        
    def get_chainset_zones(self, payload, **params):
        #LOG.info(_("List Chainset Zone - Direction Mappings"))
        chain_set_id = payload.get('chainset_id')
        self.uc.list_chainset_zones(chain_set_id, **params)
        
    def get_chainset_zone(self, payload, **params):
        chain_set_id = payload.get('chainset_id')
        chainset_zone_id = payload.get('zone_id')
        #LOG.info(_("Show chainset_zone Details for - %s"), str(chainset_zone_id))
        self.uc.show_chainset_zone(chain_set_id, chainset_zone_id, **params)

def ocasclient():
    c = ocas_client.Client()
    return c
