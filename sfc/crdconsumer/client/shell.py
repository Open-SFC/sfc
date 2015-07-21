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

from nscs.crd_consumer.client.common import utils

class SFCCommands():
    """"""
    
    COMMANDS = {
        ###Chains
        'list-chains': utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain.ListChain'),
        'create-chain' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain.CreateChain'),
        'update-chain' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain.UpdateChain'),
        'delete-chain' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain.DeleteChain'),
        'show-chain' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain.ShowChain'),
        
        ###Chain Bypass Rules
        'list-bypass-rules': utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.bypass_rule.ListBypassRule'),
        'create-bypass-rule' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.bypass_rule.CreateBypassRule'),
        'update-bypass-rule' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.bypass_rule.UpdateBypassRule'),
        'delete-bypass-rule' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.bypass_rule.DeleteBypassRule'),
        'show-bypass-rule' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.bypass_rule.ShowBypassRule'),
        
        ###Services
        'list-services': utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.service.ListService'),
        'create-service' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.service.CreateService'),
        'update-service' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.service.UpdateService'),
        'delete-service' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.service.DeleteService'),
        'show-service' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.service.ShowService'),
        
        ###ChainServices
        'list-chain-services': utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain_service.ListChainService'),
        'create-chain-service' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain_service.CreateChainService'),
        'update-chain-service' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain_service.UpdateChainService'),
        'delete-chain-service' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain_service.DeleteChainService'),
        'show-chain-service' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chain_service.ShowChainService'),
        
        ###ChainSets
        'list-chainsets': utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chainset.ListChainSet'),
        'create-chainset' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chainset.CreateChainSet'),
        'update-chainset' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chainset.UpdateChainSet'),
        'delete-chainset' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chainset.DeleteChainSet'),
        'show-chainset' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.chainset.ShowChainSet'),
        
        ###SelectionRules
        'list-selection-rules': utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.selection_rule.ListSelectionRule'),
        'create-selection-rule' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.selection_rule.CreateSelectionRule'),
        'update-selection-rule' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.selection_rule.UpdateSelectionRule'),
        'delete-selection-rule' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.selection_rule.DeleteSelectionRule'),
        'show-selection-rule' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.selection_rule.ShowSelectionRule'),
        
        ###ChainNetworkMaps
        'list-network-maps': utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.network_map.ListChainNetworkMap'),
        'create-network-map' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.network_map.CreateChainNetworkMap'),
        'update-network-map' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.network_map.UpdateChainNetworkMap'),
        'delete-network-map' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.network_map.DeleteChainNetworkMap'),
        'show-network-map' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.network_map.ShowChainNetworkMap'),
        
        ###Attributes
        'list-attributes': utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.attribute.ListAttribute'),
        'create-attribute' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.attribute.CreateAttribute'),
        'update-attribute' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.attribute.UpdateAttribute'),
        'delete-attribute' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.attribute.DeleteAttribute'),
        'show-attribute' : utils.import_class(
            'sfc.crdconsumer.client.sdnofcfg.v1.sfc.attribute.ShowAttribute'),
    }