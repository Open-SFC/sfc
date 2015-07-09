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
from crdclient.v2_0 import client as crd_client

_logger = logging.getLogger(__name__)


class Client(object):
    """Client for the Service Function Chaningin - SFC v2.0 API."""
    
    #################################################
    ##        Service Function Chaining paths      ##
    #################################################

    networkfunctions_path = "/sfc/networkfunctions"
    networkfunction_path = "/sfc/networkfunctions/%s"
    categories_path = "/sfc/categories"
    category_path = "/sfc/categories/%s"
    category_networkfunctions_path = "/sfc/categories/%s/nf_maps"
    category_networkfunction_path = "/sfc/categories/%s/nf_maps/%s"
    vendors_path = "/sfc/vendors"
    vendor_path = "/sfc/vendors/%s"
    appliances_path = "/sfc/appliances"
    appliance_path = "/sfc/appliances/%s"
    
    metadatas_url = "/sfc/appliances/%s/metadatas"
    metadata_url = "/sfc/appliances/%s/metadatas/%s"
    
    personalities_path = "/sfc/appliances/%s/personalities"
    personality_path = "/sfc/appliances/%s/personalities/%s"
    chains_path = "/sfc/chains"
    chain_path = "/sfc/chains/%s"
    chainsets_path = "/sfc/chainsets"
    chainset_path = "/sfc/chainsets/%s"
    
    rules_path = "/sfc/chainsets/%s/rules"
    rule_path = "/sfc/chainsets/%s/rules/%s"
    
    appliance_maps_url = "/sfc/chains/%s/appliances"
    appliance_map_url = "/sfc/chains/%s/appliances/%s"
    
    bypass_rules_path = "/sfc/chains/%s/bypass_rules"
    bypass_rule_path = "/sfc/chains/%s/bypass_rules/%s"
    
    chainmaps_path = "/sfc/chainmaps"
    chainmap_path = "/sfc/chainmaps/%s"
    
    
    appliance_map_confs_path = "/sfc/chains/%s/appliances/%s/confs"
    appliance_map_conf_path = "/sfc/chains/%s/appliances/%s/confs/%s"
    
    config_handles_path = "/sfc/config_handles"
    config_handle_path = "/sfc/config_handles/%s"
    
    category_histories_path = "/sfc/category_histories"
    category_history_path = "/sfc/category_histories/%s"
    vendor_histories_path = "/sfc/vendor_histories"
    vendor_history_path = "/sfc/vendor_histories/%s"
    category_nf_histories_path = "/sfc/category_nf_histories"
    category_nf_history_path = "/sfc/category_nf_histories/%s"
    appliance_histories_path = "/sfc/appliance_histories"
    appliance_history_path = "/sfc/appliance_histories/%s"
    chain_histories_path = "/sfc/chain_histories"
    chain_history_path = "/sfc/chain_histories/%s"
    appliance_map_histories_path = "/sfc/appliance_map_histories"
    appliance_map_history_path = "/sfc/appliance_map_histories/%s"
    chain_img_net_histories_path = "/sfc/chain_img_net_histories"
    chain_img_net_history_path = "/sfc/chain_img_net_histories/%s"
    
    launch_path = "/sfc/launchs"
    
    nsdeltas_path = "/sfc/nsdeltas"
    nsdelta_path = "/sfc/nsdeltas/%s"
    
    ##VLAN Quota
    vlanquotas_path = "/sfc/vlanquotas"
    vlanquota_path = "/sfc/vlanquotas/%s"
    
    appliance_map_instances_path = "/sfc/chains/%s/appliances/%s/instances"
    appliance_map_instance_path = "/sfc/chains/%s/appliances/%s/instances/%s"

    
    ######################################## NSRM Start #############################################
    
    ####### Network Function API start######################################    
    @crd_client.APIParamsCall
    def list_networkfunctions(self, **_params):
        """
        Fetches a list of all networkfunctions for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.networkfunctions_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_networkfunction(self, body=None):
        """
        Creates a new Networkfunction
        """
        return self.crdclient.post(self.networkfunctions_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_networkfunction(self, networkfunction):
        """
        Deletes the specified networkfunction
        """
        return self.crdclient.delete(self.networkfunction_path % (networkfunction))
    
    @crd_client.APIParamsCall
    def show_networkfunction(self, networkfunction, **_params):
        """
        Fetches information of a certain networkfunction
        """
        return self.crdclient.get(self.networkfunction_path % (networkfunction), params=_params)
        
    @crd_client.APIParamsCall
    def update_networkfunction(self, networkfunction, body=None):
        """
        Updates a networkfunction
        """
        return self.crdclient.put(self.networkfunction_path % (networkfunction), body=body)
    ####### Network Function API End######################################   
    
    
    
    
    @crd_client.APIParamsCall
    def list_categories(self, **_params):
        """
        Fetches a list of all categories for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.categories_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_category(self, body=None):
        """
        Creates a new Category
        """
        return self.crdclient.post(self.categories_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_category(self, category):
        """
        Deletes the specified category
        """
        return self.crdclient.delete(self.category_path % (category))
    
    @crd_client.APIParamsCall
    def show_category(self, category, **_params):
        """
        Fetches information of a certain category
        """
        return self.crdclient.get(self.category_path % (category), params=_params)
        
    @crd_client.APIParamsCall
    def update_category(self, category, body=None):
        """
        Updates a category
        """
        return self.crdclient.put(self.category_path % (category), body=body)
        
    @crd_client.APIParamsCall
    def list_category_networkfunctions(self, **_params):
        """
        Fetches a list of all category_networkfunctions for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.category_networkfunctions_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_category_networkfunction(self, category_id, body=None):
        """
        Creates a new Category_networkfunction
        """
        return self.crdclient.post(self.category_networkfunctions_path % (category_id), body=body)
        
    @crd_client.APIParamsCall
    def delete_category_networkfunction(self, category_id, networkfunction_id):
        """
        Deletes the specified category_networkfunction
        """
        return self.crdclient.delete(self.category_networkfunction_path % (category_id, networkfunction_id))
        
    @crd_client.APIParamsCall
    def list_vendors(self, **_params):
        """
        Fetches a list of all vendors for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.vendors_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_vendor(self, body=None):
        """
        Creates a new Vendor
        """
        return self.crdclient.post(self.vendors_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_vendor(self, vendor):
        """
        Deletes the specified vendor
        """
        return self.crdclient.delete(self.vendor_path % (vendor))
    
    @crd_client.APIParamsCall
    def show_vendor(self, vendor, **_params):
        """
        Fetches information of a certain vendor
        """
        return self.crdclient.get(self.vendor_path % (vendor), params=_params)
        
    @crd_client.APIParamsCall
    def update_vendor(self, vendor, body=None):
        """
        Updates a vendor
        """
        return self.crdclient.put(self.vendor_path % (vendor), body=body)
        
    @crd_client.APIParamsCall
    def list_appliances(self, **_params):
        """
        Fetches a list of all appliances for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.appliances_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_appliance(self, body=None):
        """
        Creates a new Images
        """
        return self.crdclient.post(self.appliances_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_appliance(self, appliance):
        """
        Deletes the specified appliance
        """
        return self.crdclient.delete(self.appliance_path % (appliance))
    
    @crd_client.APIParamsCall
    def show_appliance(self, appliance, **_params):
        """
        Fetches information of a certain appliance
        """
        return self.crdclient.get(self.appliance_path % (appliance), params=_params)
        
    @crd_client.APIParamsCall
    def update_appliance(self, appliance, body=None):
        """
        Updates a appliance
        """
        return self.crdclient.put(self.appliance_path % (appliance), body=body)
        
    @crd_client.APIParamsCall
    def list_metadatas(self, appliance_id, **_params):
        """
        Fetches a list of all metadatas for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.metadatas_url % (appliance_id), params=_params)
        
    @crd_client.APIParamsCall
    def create_metadata(self, appliance_id, body=None):
        """
        Creates a new Metadata
        """
        #self.appliance_maps_url % (chain_id), 
        return self.crdclient.post(self.metadatas_url % (appliance_id), body=body)
        
    @crd_client.APIParamsCall
    def show_metadata(self, appliance_id, metadata, **_params):
        """
        Fetches information of a certain metadata
        """
        return self.crdclient.get(self.metadata_url % (appliance_id, metadata), params=_params)
    
    @crd_client.APIParamsCall
    def delete_metadata(self, appliance_id, metadata_id):
        """
        Deletes the specified metadata
        """
        return self.crdclient.delete(self.metadata_url % (appliance_id, metadata_id))
        
    @crd_client.APIParamsCall
    def list_personalities(self, appliance_id, **_params):
        """
        Fetches a list of all personalities for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.personalities_path % (appliance_id), params=_params)
        
    @crd_client.APIParamsCall
    def create_personality(self, appliance_id, body=None):
        """
        Creates a new Personality
        """
        return self.crdclient.post(self.personalities_path % (appliance_id), body=body)
        
    @crd_client.APIParamsCall
    def show_personality(self, appliance_id, personality, **_params):
        """
        Fetches information of a certain personality
        """
        return self.crdclient.get(self.personality_path % (appliance_id, personality), params=_params)
    
    @crd_client.APIParamsCall
    def delete_personality(self, appliance_id, personality_id):
        """
        Deletes the specified personality
        """
        return self.crdclient.delete(self.personality_path % (appliance_id, personality_id))
        
    @crd_client.APIParamsCall
    def list_chains(self, **_params):
        """
        Fetches a list of all chains for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.chains_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_chain(self, body=None):
        """
        Creates a new chain
        """
        return self.crdclient.post(self.chains_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_chain(self, chain):
        """
        Deletes the specified chain
        """
        return self.crdclient.delete(self.chain_path % (chain))
    
    @crd_client.APIParamsCall
    def show_chain(self, chain, **_params):
        """
        Fetches information of a certain chain
        """
        return self.crdclient.get(self.chain_path % (chain), params=_params)
        
    @crd_client.APIParamsCall
    def update_chain(self, chain, body=None):
        """
        Updates a chain
        """
        return self.crdclient.put(self.chain_path % (chain), body=body)
        
    @crd_client.APIParamsCall
    def list_appliance_maps(self, chain_id, **_params):
        """
        Fetches a list of all appliance_maps for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.appliance_maps_url % (chain_id), params=_params)
        
    @crd_client.APIParamsCall
    def create_appliance_map(self, chain_id, body=None):
        """
        Creates a new Chain_Appliance Map
        """
        return self.crdclient.post(self.appliance_maps_url % (chain_id), body=body)
        
    @crd_client.APIParamsCall
    def delete_appliance_map(self, chain_id, appliance_map):
        """
        Deletes the specified appliance_map
        """
        return self.crdclient.delete(self.appliance_map_url  % (chain_id, appliance_map))
    
    @crd_client.APIParamsCall
    def show_appliance_map(self, chain_id, appliance_map, **_params):
        """
        Fetches information of a certain appliance_map
        """
        return self.crdclient.get(self.appliance_map_url % (chain_id, appliance_map), params=_params)
        
    @crd_client.APIParamsCall
    def update_appliance_map(self, chain_id, appliance_map, body=None):
        """
        Updates a appliance_map
        """
        return self.crdclient.put(self.appliance_map_url % (chain_id, appliance_map), body=body)
        
    @crd_client.APIParamsCall
    def list_appliance_map_confs(self, chain_id, appliance_map_id, **_params):
        """
        Fetches a list of all appliance_map_confs for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.appliance_map_confs_path % (chain_id, appliance_map_id), params=_params)
        
    @crd_client.APIParamsCall
    def create_appliance_map_conf(self, chain_id, appliance_map_id, body=None):
        """
        Creates a new Chain_appliance_conf
        """
        return self.crdclient.post(self.appliance_map_confs_path % (chain_id, appliance_map_id), body=body)
        
    @crd_client.APIParamsCall
    def delete_appliance_map_conf(self, appliance_map_conf, appliance_map_id, chain_id):
        """
        Deletes the specified appliance_map_conf
        """
        return self.crdclient.delete(self.appliance_map_conf_path % (chain_id, appliance_map_id, appliance_map_conf))
    
    @crd_client.APIParamsCall
    def list_bypass_rules(self, chain_id, **_params):
        """
        Fetches a list of all bypass_rules for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.bypass_rules_path % (chain_id), params=_params)
        
    @crd_client.APIParamsCall
    def create_bypass_rule(self, chain_id, body=None):
        """
        Creates a new Chain_Rule
        """
        return self.crdclient.post(self.bypass_rules_path % (chain_id), body=body)
        
    @crd_client.APIParamsCall
    def delete_bypass_rule(self, chain_id, bypass_rule):
        """
        Deletes the specified bypass_rule
        """
        return self.crdclient.delete(self.bypass_rule_path  % (chain_id, bypass_rule))
    
    @crd_client.APIParamsCall
    def show_bypass_rule(self, chain_id, bypass_rule, **_params):
        """
        Fetches information of a certain bypass_rule
        """
        return self.crdclient.get(self.bypass_rule_path % (chain_id, bypass_rule), params=_params)
        
    @crd_client.APIParamsCall
    def update_bypass_rule(self, chain_id, bypass_rule, body=None):
        """
        Updates a bypass_rule
        """
        return self.crdclient.put(self.bypass_rule_path % (chain_id, bypass_rule), body=body)
        
    @crd_client.APIParamsCall
    def list_chainsets(self, **_params):
        """
        Fetches a list of all chainsets for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.chainsets_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_chainset(self, body=None):
        """
        Creates a new chainset
        """
        return self.crdclient.post(self.chainsets_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_chainset(self, chainset):
        """
        Deletes the specified chainset
        """
        return self.crdclient.delete(self.chainset_path % (chainset))
    
    @crd_client.APIParamsCall
    def show_chainset(self, chainset, **_params):
        """
        Fetches information of a certain chainset
        """
        return self.crdclient.get(self.chainset_path % (chainset), params=_params)
        
    @crd_client.APIParamsCall
    def update_chainset(self, chainset, body=None):
        """
        Updates a chainset
        """
        return self.crdclient.put(self.chainset_path % (chainset), body=body)
        
    @crd_client.APIParamsCall
    def list_rules(self, chainset_id, **_params):
        """
        Fetches a list of all rules for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.rules_path % (chainset_id), params=_params)
        
    @crd_client.APIParamsCall
    def create_rule(self, chainset_id, body=None):
        """
        Creates a new Chain_Rule
        """
        return self.crdclient.post(self.rules_path % (chainset_id), body=body)
        
    @crd_client.APIParamsCall
    def delete_rule(self, chainset_id, rule):
        """
        Deletes the specified rule
        """
        return self.crdclient.delete(self.rule_path  % (chainset_id, rule))
    
    @crd_client.APIParamsCall
    def show_rule(self, chainset_id, rule, **_params):
        """
        Fetches information of a certain rule
        """
        return self.crdclient.get(self.rule_path % (chainset_id, rule), params=_params)
        
    @crd_client.APIParamsCall
    def update_rule(self, chainset_id, rule, body=None):
        """
        Updates a rule
        """
        return self.crdclient.put(self.rule_path % (chainset_id, rule), body=body)
        
    
    @crd_client.APIParamsCall
    def list_chainmaps(self, **_params):
        """
        Fetches a list of all chainmaps for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.chainmaps_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_chainmap(self, body=None):
        """
        Creates a new chainmap
        """
        return self.crdclient.post(self.chainmaps_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_chainmap(self, chainmap):
        """
        Deletes the specified chainmap
        """
        return self.crdclient.delete(self.chainmap_path % (chainmap))
    
    @crd_client.APIParamsCall
    def show_chainmap(self, chainmap, **_params):
        """
        Fetches information of a certain chainmap
        """
        return self.crdclient.get(self.chainmap_path % (chainmap), params=_params)
        
    @crd_client.APIParamsCall
    def update_chainmap(self, chainmap, body=None):
        """
        Updates a chainmap
        """
        return self.crdclient.put(self.chainmap_path % (chainmap), body=body)
    
    
    @crd_client.APIParamsCall
    def list_config_handles(self, **_params):
        """
        Fetches a list of all config_handles for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.config_handles_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_config_handle(self, body=None):
        """
        Creates a new Config_handle
        """
        return self.crdclient.post(self.config_handles_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_config_handle(self, config_handle):
        """
        Deletes the specified config_handle
        """
        return self.crdclient.delete(self.config_handle_path % (config_handle))
    
    @crd_client.APIParamsCall
    def show_config_handle(self, config_handle, **_params):
        """
        Fetches information of a certain config_handle
        """
        return self.crdclient.get(self.config_handle_path % (config_handle), params=_params)
        
    @crd_client.APIParamsCall
    def update_config_handle(self, config_handle, body=None):
        """
        Updates a config_handle
        """
        return self.crdclient.put(self.config_handle_path % (config_handle), body=body)
        
    @crd_client.APIParamsCall
    def generate_slb_config(self, body=None):
        """
        Generate the specified configuration
        """
        return self.crdclient.post(self.slb_configs_path, body=body)
        
    @crd_client.APIParamsCall
    def launch_chain(self, body=None):
        """
        Launch Chain
        """
        return self.crdclient.post(self.launch_path, body=body)
    
    @crd_client.APIParamsCall
    def list_appliance_map_instances(self, chain_id, appliance_map_id, **_params):
        """
        Fetches a list of all appliance_map_instances for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.appliance_map_instances_path % (chain_id, appliance_map_id), params=_params)
        
    @crd_client.APIParamsCall
    def create_appliance_map_instance(self, chain_id, appliance_map_id, body=None):
        """
        Creates a new Chain_appliance_instance
        """
        return self.crdclient.post(self.appliance_map_instances_path % (chain_id, appliance_map_id), body=body)
        
    @crd_client.APIParamsCall
    def delete_appliance_map_instance(self, appliance_map_instance, appliance_map_id, chain_id):
        """
        Deletes the specified appliance_map_instance
        """
        return self.crdclient.delete(self.appliance_map_instance_path % (chain_id, appliance_map_id, appliance_map_instance))
    
    @crd_client.APIParamsCall
    def list_bypass_rules(self, chain_id, **_params):
        """
        Fetches a list of all bypass_rules for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.bypass_rules_path % (chain_id), params=_params)
    
    ################### NW Service Delta ##############################    
    @crd_client.APIParamsCall
    def list_nsdeltas(self, **_params):
        """
        Fetches a list of all ports for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.nsdeltas_path, params=_params)
        
    @crd_client.APIParamsCall
    def show_nsdelta(self, keyword, **_params):
        """
        Fetches information of a certain networkfunction
        """
        return self.crdclient.get(self.nsdelta_path % (keyword), params=_params)
    
    ####### VLAN Quota API Begin######################################
    @crd_client.APIParamsCall
    def list_vlanquotas(self, **_params):
        """
        Fetches a list of all vlanquotas for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.crdclient.get(self.vlanquotas_path, params=_params)
        
    @crd_client.APIParamsCall
    def create_vlanquota(self, body=None):
        """
        Creates a new Networkfunction
        """
        return self.crdclient.post(self.vlanquotas_path, body=body)
        
    @crd_client.APIParamsCall
    def delete_vlanquota(self, vlanquota):
        """
        Deletes the specified vlanquota
        """
        return self.crdclient.delete(self.vlanquota_path % (vlanquota))
    
    @crd_client.APIParamsCall
    def show_vlanquota(self, vlanquota, **_params):
        """
        Fetches information of a certain vlanquota
        """
        return self.crdclient.get(self.vlanquota_path % (vlanquota), params=_params)
        
    @crd_client.APIParamsCall
    def update_vlanquota(self, vlanquota, body=None):
        """
        Updates a vlanquota
        """
        return self.crdclient.put(self.vlanquota_path % (vlanquota), body=body)
    ####### VLAN Quota API End######################################
   

    def __init__(self, **kwargs):
        self.crdclient = crd_client.Client(**kwargs)
        #self.crdclient.EXTED_PLURALS.update(self.FW_EXTED_PLURALS)
        self.format = 'json' 
