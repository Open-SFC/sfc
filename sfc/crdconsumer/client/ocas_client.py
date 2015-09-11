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

import logging
from nscs.crd_consumer.client import ocas_client

_logger = logging.getLogger(__name__)

class Client(object):
    """
    SFC related OCAS Client Functions in CRD Consumer 
    """
    
    def __init__(self, **kwargs):
        self.ocasclient = ocas_client.Client(**kwargs)
        #self.crdclient.EXTED_PLURALS.update(self.FW_EXTED_PLURALS)
        self.format = 'json'
        url = self.ocasclient.url
        
        chains = 'chains'
        chain_bypass_rules = 'bypassrules'
        services = 'services'
        chain_services = 'services'
        chain_sets = 'chainsets'
        chain_selection_rules = 'selectionrules'
        chain_networks = 'chainnetworks'
        attributes = 'attributes'
        vlanpairs = 'instance'
        appliance_instance = 'instance'
        chainset_zones = 'zones'
        
        
        #NSRM URLs
        self.chains_path = "%s/sfc/%s" % (url, chains)
        self.chain_path = "%s/sfc/%s" % (url, chains) + "/%s"
        
        self.chain_bypass_rules_path = "%s/sfc/%s" % (url, chains) + "/%s" + "/%s" % (chain_bypass_rules)
        self.chain_bypass_rule_path = "%s/sfc/%s" % (url, chains) + "/%s" + "/%s" % (chain_bypass_rules) + "/%s"
        
        self.services_path = "%s/sfc/%s" % (url, services)
        self.service_path = "%s/sfc/%s" % (url, services) + "/%s"
        
        self.chain_services_path = "%s/sfc/%s" % (url, chains) + "/%s" + "/%s" % (chain_services)
        self.chain_service_path = "%s/sfc/%s" % (url, chains) + "/%s" + "/%s" % (chain_services) + "/%s"
        
        self.chain_sets_path = "%s/sfc/%s" % (url, chain_sets)
        self.chain_set_path = "%s/sfc/%s" % (url, chain_sets) + "/%s"
        
        self.chain_selection_rules_path = "%s/sfc/%s" % (url, chain_sets) + "/%s" + "/%s" % (chain_selection_rules)
        self.chain_selection_rule_path = "%s/sfc/%s" % (url, chain_sets) + "/%s" + "/%s" % (chain_selection_rules) + "/%s"
        
        self.chain_networks_path = "%s/sfc/%s" % (url, chain_networks)
        self.chain_network_path = "%s/sfc/%s" % (url, chain_networks) + "/%s"
        
        self.attributes_path = "%s/sfc/%s" % (url, attributes)
        self.attribute_path = "%s/sfc/%s" % (url, attributes) + "/%s"
        
        self.vlan_pairs_path = "%s/sfc/%s" % (url, chains) + "/%s" + \
                               "/%s" % (chain_services) + "/%s" + \
                               "/%s" % (vlanpairs)
        self.vlan_pair_path = "%s/sfc/%s" % (url, chains) + "/%s" +\
                              "/%s" % (chain_services) + "/%s" +\
                              "/%s" % (vlanpairs) + "/%s"

        self.appliance_instances_path = "%s/sfc/%s" % (url, chains) + "/%s" + \
                                        "/%s" % chain_services + "/%s" + \
                                        "/%s" % appliance_instance
        self.appliance_instance_path = "%s/sfc/%s" % (url, chains) + "/%s" +\
                                       "/%s" % chain_services + "/%s" + \
                                       "/%s" % appliance_instance + "/%s"
        self.chainset_zones_path = "%s/sfc/%s" % (url, chain_sets) + \
                                        "/%s" + "/%s" % (chainset_zones)
        self.chainset_zone_path = "%s/sfc/%s" % (url, chain_sets) + \
                                        "/%s" + "/%s" % (chainset_zones) + "/%s"
    
    
    ##Chains
    def create_chain(self, body=None):
        """
        Creates a new chain
        """
        return self.ocasclient.post(self.chains_path, body=body)
        
    def delete_chain(self, chain):
        """
        Deletes the specified chain
        """
        return self.ocasclient.delete(self.chain_path % (chain))
        
    def update_chain(self, chain, body=None):
        """
        Updates the specified chain
        """
        return self.ocasclient.put(self.chain_path % (chain), body=body)
        
    def list_chains(self, **_params):
        """
        Fetches a list of all chains
        """
        return self.ocasclient.list('chains', self.chains_path, True, **_params)
        
    def show_chain(self, chain, **_params):
        """
        Fetches information of a Chain
        """
        return self.ocasclient.get(self.chain_path % (chain), params=_params)
        
    ##Chain Bypass Rules
    def create_chain_bypass_rule(self, chain_id, body=None):
        """
        Creates a new chain_bypass_rule
        """
        return self.ocasclient.post(self.chain_bypass_rules_path % (chain_id), body=body)
        
    def delete_chain_bypass_rule(self, chain_id, chain_bypass_rule):
        """
        Deletes the specified chain_bypass_rule
        """
        return self.ocasclient.delete(self.chain_bypass_rule_path % (chain_id, chain_bypass_rule))
        
    def update_chain_bypass_rule(self, chain_id, chain_bypass_rule, body=None):
        """
        Updates the specified chain_bypass_rule
        """
        return self.ocasclient.put(self.chain_bypass_rule_path % (chain_id, chain_bypass_rule), body=body)
        
    def list_chain_bypass_rules(self, chain_id, **_params):
        """
        Fetches a list of all chain_bypass_rules
        """
        return self.ocasclient.list('chain_bypass_rules', self.chain_bypass_rules_path % (chain_id), True, **_params)
        
    def show_chain_bypass_rule(self, chain_id, chain_bypass_rule, **_params):
        """
        Fetches information of a chain_bypass_rule
        """
        return self.ocasclient.get(self.chain_bypass_rule_path % (chain_id, chain_bypass_rule), params=_params)
        
    ##services
    def create_service(self, body=None):
        """
        Creates a new service
        """
        return self.ocasclient.post(self.services_path, body=body)
        
    def delete_service(self, service):
        """
        Deletes the specified service
        """
        return self.ocasclient.delete(self.service_path % (service))
        
    def update_service(self, service, body=None):
        """
        Updates the specified service
        """
        return self.ocasclient.put(self.service_path % (service), body=body)
        
    def list_services(self, **_params):
        """
        Fetches a list of all services
        """
        return self.ocasclient.list('services', self.services_path, True, **_params)
        
    def show_service(self, service, **_params):
        """
        Fetches information of a service
        """
        return self.ocasclient.get(self.service_path % (service), params=_params)
        
    ##chain_services
    def create_chain_service(self, chain_id, body=None):
        """
        Creates a new chain_service
        """
        return self.ocasclient.post(self.chain_services_path % (chain_id), body=body)
        
    def delete_chain_service(self, chain_id, chain_service):
        """
        Deletes the specified chain_service
        """
        return self.ocasclient.delete(self.chain_service_path % (chain_id, chain_service))
        
    def update_chain_service(self, chain_id, chain_service, body=None):
        """
        Updates the specified chain_service
        """
        return self.ocasclient.put(self.chain_service_path % (chain_id, chain_service), body=body)
        
    def list_chain_services(self, chain_id, **_params):
        """
        Fetches a list of all chain_services
        """
        return self.ocasclient.list('chain_services', self.chain_services_path % (chain_id), True, **_params)
        
    def show_chain_service(self, chain_id, chain_service, **_params):
        """
        Fetches information of a chain_service
        """
        return self.ocasclient.get(self.chain_service_path % (chain_id, chain_service), params=_params)
        
    ##chain_sets
    def create_chain_set(self, body=None):
        """
        Creates a new chain_set
        """
        return self.ocasclient.post(self.chain_sets_path, body=body)
        
    def delete_chain_set(self, chain_set):
        """
        Deletes the specified chain_set
        """
        return self.ocasclient.delete(self.chain_set_path % (chain_set))
        
    def update_chain_set(self, chain_set, body=None):
        """
        Updates the specified chain_set
        """
        return self.ocasclient.put(self.chain_set_path % (chain_set), body=body)
        
    def list_chain_sets(self, **_params):
        """
        Fetches a list of all chain_sets
        """
        return self.ocasclient.list('chain_sets', self.chain_sets_path, True, **_params)
        
    def show_chain_set(self, chain_set, **_params):
        """
        Fetches information of a chain_set
        """
        return self.ocasclient.get(self.chain_set_path % (chain_set), params=_params)
        
    ##Chain Selection Rules
    def create_chain_selection_rule(self, chain_set_id, body=None):
        """
        Creates a new chain_selection_rule
        """
        return self.ocasclient.post(self.chain_selection_rules_path % (chain_set_id), body=body)
        
    def delete_chain_selection_rule(self, chain_set_id, chain_selection_rule):
        """
        Deletes the specified chain_selection_rule
        """
        return self.ocasclient.delete(self.chain_selection_rule_path % (chain_set_id, chain_selection_rule))
        
    def update_chain_selection_rule(self, chain_set_id, chain_selection_rule, body=None):
        """
        Updates the specified chain_selection_rule
        """
        return self.ocasclient.put(self.chain_selection_rule_path % (chain_set_id, chain_selection_rule), body=body)
        
    def list_chain_selection_rules(self, chain_set_id, **_params):
        """
        Fetches a list of all chain_selection_rules
        """
        return self.ocasclient.list('chain_selection_rules', self.chain_selection_rules_path % (chain_set_id), True, **_params)
        
    def show_chain_selection_rule(self, chain_set_id, chain_selection_rule, **_params):
        """
        Fetches information of a chain_selection_rule
        """
        return self.ocasclient.get(self.chain_selection_rule_path % (chain_set_id, chain_selection_rule), params=_params)
        
    ##chain_networks
    def create_chain_network(self, body=None):
        """
        Creates a new chain_network
        """
        return self.ocasclient.post(self.chain_networks_path, body=body)
        
    def delete_chain_network(self, chain_network):
        """
        Deletes the specified chain_network
        """
        return self.ocasclient.delete(self.chain_network_path % (chain_network))
        
    def update_chain_network(self, chain_network, body=None):
        """
        Updates the specified chain_network
        """
        return self.ocasclient.put(self.chain_network_path % (chain_network), body=body)
        
    def list_chain_networks(self, **_params):
        """
        Fetches a list of all chain_networks
        """
        return self.ocasclient.list('chain_networks', self.chain_networks_path, True, **_params)
        
    def show_chain_network(self, chain_network, **_params):
        """
        Fetches information of a chain_network
        """
        return self.ocasclient.get(self.chain_network_path % (chain_network), params=_params)
    
    ##Attributes
    def create_attribute(self, body=None):
        """
        Creates a new attribute
        """
        return self.ocasclient.post(self.attributes_path, body=body)
        
    def delete_attribute(self, attribute):
        """
        Deletes the specified attribute
        """
        return self.ocasclient.delete(self.attribute_path % (attribute))
        
    def update_attribute(self, attribute, body=None):
        """
        Updates the specified attribute
        """
        return self.ocasclient.put(self.attribute_path % (attribute), body=body)
        
    def list_attributes(self, **_params):
        """
        Fetches a list of all attributes
        """
        return self.ocasclient.list('attributes', self.attributes_path, True, **_params)
        
    def show_attribute(self, attribute, **_params):
        """
        Fetches information of a Attribute
        """
        return self.ocasclient.get(self.attribute_path % (attribute), params=_params)
        
    ##vlan pairs
    # TODO: Need to remove vlan pairs as appliance instance replaced it
    def create_vlan_pair(self, chain_id, chain_map_id, body=None):
        """
        Creates a new vlan_pair
        """
        return self.ocasclient.post(self.vlan_pairs_path % (chain_id, chain_map_id), body=body)
        
    def delete_vlan_pair(self, chain_id, chain_map_id, vlan_pair):
        """
        Deletes the specified vlan_pair
        """
        return self.ocasclient.delete(self.vlan_pair_path % (chain_id, chain_map_id, vlan_pair))
        
    def update_vlan_pair(self, chain_id, chain_map_id, vlan_pair, body=None):
        """
        Updates the specified vlan_pair
        """
        return self.ocasclient.put(self.vlan_pair_path % (chain_id, chain_map_id, vlan_pair), body=body)
        
    def list_vlan_pairs(self, chain_id, chain_map_id, **_params):
        """
        Fetches a list of all vlan_pairs
        """
        return self.ocasclient.list('vlan_pairs', self.vlan_pairs_path % (chain_id, chain_map_id), True, **_params)
        
    def show_vlan_pair(self, chain_id, chain_map_id, vlan_pair, **_params):
        """
        Fetches information of a vlan_pair
        """
        return self.ocasclient.get(self.vlan_pair_path % (chain_id, chain_map_id, vlan_pair), params=_params)

    ##appliance_instance
    def create_appliance_instance(self, chain_id, chain_map_id, body=None):
        """
        Creates a new vlan_pair
        """
        return self.ocasclient.post(self.appliance_instances_path % (
            chain_id, chain_map_id), body=body)

    def delete_appliance_instance(self, chain_id, chain_map_id, appliance_instance_id):
        """
        Deletes the specified vlan_pair
        """
        return self.ocasclient.delete(self.appliance_instance_path % (chain_id,
                                                             chain_map_id, appliance_instance_id))

    def update_appliance_instance(self, chain_id, chain_map_id, appliance_instance_id, body=None):
        """
        Updates the specified vlan_pair
        """
        return self.ocasclient.put(self.appliance_instance_path % (chain_id, chain_map_id, appliance_instance_id), body=body)

    def list_appliance_instance(self, chain_id, chain_map_id, **_params):
        """
        Fetches a list of all vlan_pairs
        """
        return self.ocasclient.list('appliance_instances',
                                    self.appliance_instances_path % (chain_id, chain_map_id), True, **_params)

    def show_appliance_instance(self, chain_id, chain_map_id,
                                appliance_instance_id, **_params):
        """
        Fetches information of a vlan_pair
        """
        return self.ocasclient.get(self.appliance_instance_path % (chain_id, chain_map_id, appliance_instance_id), params=_params)
    
    ##Chainset Zone - Direction Mappings
    def create_chainset_zone(self, chain_set_id, body=None):
        """
        Creates a new chainset_zone
        """
        return self.ocasclient.post(self.chainset_zones_path % (chain_set_id), body=body)
        
    def delete_chainset_zone(self, chain_set_id, chainset_zone):
        """
        Deletes the specified chainset_zone
        """
        return self.ocasclient.delete(self.chainset_zone_path % (chain_set_id, chainset_zone))
        
    def update_chainset_zone(self, chain_set_id, chainset_zone, body=None):
        """
        Updates the specified chainset_zone
        """
        return self.ocasclient.put(self.chainset_zone_path % (chain_set_id, chainset_zone), body=body)
        
    def list_chainset_zones(self, chain_set_id, **_params):
        """
        Fetches a list of all chainset_zones
        """
        return self.ocasclient.list('chainset_zones', self.chainset_zones_path % (chain_set_id), True, **_params)
        
    def show_chainset_zone(self, chain_set_id, chainset_zone, **_params):
        """
        Fetches information of a chainset_zone
        """
        return self.ocasclient.get(self.chainset_zone_path % (chain_set_id, chainset_zone), params=_params)