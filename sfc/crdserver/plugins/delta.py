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
from nscs.crdserver.openstack.common import log as logging
from nscs.crdserver.openstack.common import context

from sfc.crdserver.db import delta
from sfc.crdserver.db import sfc_db

import re
import socket
import time

LOG = logging.getLogger(__name__)

class SfcDelta(object):
    """
    Handling Create delta and Get Difference 
    """
    def __init__(self):
	self.deltadb = delta.SfcDeltaDb()
	self.db = sfc_db.SFCPluginDb()
	
    def create_networkfunctions_delta(self, context, data_dict):
        result_delta = self.deltadb.create_networkfunctions_delta(context, data_dict)
        return result_delta

    def create_config_handles_delta(self, context, data_dict):
        result_delta = self.deltadb.create_config_handles_delta(context, data_dict)
        return result_delta
    
    def create_categories_delta(self, context, data_dict):
        result_delta = self.deltadb.create_categories_delta(context, data_dict)
        return result_delta
    
    def create_category_networkfunctions_delta(self, context, data_dict):
        result_delta = self.deltadb.create_category_networkfunctions_delta(context, data_dict)
        return result_delta
    
    def create_vendors_delta(self, context, data_dict):
        result_delta = self.deltadb.create_vendors_delta(context, data_dict)
        return result_delta
    
    def create_appliances_delta(self, context, data_dict):
        result_delta = self.deltadb.create_appliances_delta(context, data_dict)
        return result_delta
    
    def create_chains_delta(self, context, data_dict):
        result_delta = self.deltadb.create_chains_delta(context, data_dict)
        return result_delta
    
    def create_chain_appliances_delta(self, context, data_dict):
        result_delta = self.deltadb.create_chain_appliances_delta(context, data_dict)
        return result_delta
    
    def create_chain_bypass_rules_delta(self, context, data_dict):
        result_delta = self.deltadb.create_chain_bypass_rules_delta(context, data_dict)
        return result_delta
    
    def create_chainsets_delta(self, context, data_dict):
        result_delta = self.deltadb.create_chainsets_delta(context, data_dict)
        return result_delta
    
    def create_chainrules_delta(self, context, data_dict):
        result_delta = self.deltadb.create_chainrules_delta(context, data_dict)
        return result_delta
    
    def create_chainmaps_delta(self, context, data_dict):
        result_delta = self.deltadb.create_chainmaps_delta(context, data_dict)
        return result_delta
    
    def create_appliance_instances_delta(self, context, data_dict):
        result_delta = self.deltadb.create_appliance_instances_delta(context, data_dict)
        return result_delta
    
    def sfc_init(self, ctx, version, hostname):
        delta = {}
        if version > 0:
            pass

        elif version == 0:
            #Network Delta

            fields = []
            fields = ['runtime_version']
            current_version = 0
            ver = self.db.get_versions(ctx, filters=None, fields=fields)
            if ver:
                current_version = max(ver)['runtime_version']
                LOG.debug(_("Runtime Version = %s"), str(current_version))
            #current_version = 100

            #NWApplicances Delta
            nwapp_diff = self.db.get_appliances(ctx, filters=None, fields=None)
            for nwapp in nwapp_diff:
                fil = {}
                id = nwapp['id']
                fil['appliance_id'] = [id]
                fil['operation'] = ['create']
                CompDelta = self.deltadb.get_appliances_deltas(ctx, fil)
                arr = sorted(CompDelta, key=lambda t: t['version_id'],
                             reverse=True)
                verid = arr[0]['version_id']
                nwapp.update(
                    {'appliance_id': nwapp['id'], 'operation': 'create',
                     'version_id': current_version})
                nwapp_message = {}
                nwapp_message.update(
                    {'method': 'create_appliance', 'payload': nwapp})
                delta[verid] = nwapp_message


            #NWCHains Delta
            nwchain_diff = self.db.get_chains(ctx, filters=None, fields=None)
            for nwchain in nwchain_diff:
                fil = {}
                id = nwchain['id']
                fil['chain_id'] = [id]
                fil['operation'] = ['create']
                CompDelta = self.deltadb.get_chains_deltas(ctx, fil)
                arr = sorted(CompDelta, key=lambda t: t['version_id'],
                             reverse=True)
                verid = arr[0]['version_id']
                nwchain.update(
                    {'chain_id': nwchain['id'], 'operation': 'create',
                     'version_id': current_version})
                nwchain_message = {}
                nwchain_message.update(
                    {'method': 'create_chain', 'payload': nwchain})
                delta[verid] = nwchain_message


            #NWAPPChains Delta
            nwchainapp_diff = self.db.get_chain_appliance_maps(ctx,
                                                               filters=None,
                                                               fields=None)
            for nwchainapp in nwchainapp_diff:
                fil = {}
                id = nwchainapp['id']
                fil['chain_appliance_map_id'] = [id]
                fil['operation'] = ['create']
                CompDelta = self.deltadb.get_chain_appliances_deltas(ctx, fil)
                arr = sorted(CompDelta, key=lambda t: t['version_id'],
                             reverse=True)
                verid = arr[0]['version_id']

                nwchainapp.update({'chain_appliance_map_id': nwchainapp['id'],
                                   'operation': 'create',
                                   'version_id': current_version})
                nwchainapp_message = {}
                nwchainapp_message.update({'method': 'create_chain_appliance',
                                           'payload': nwchainapp})
                delta[verid] = nwchainapp_message


            #NWbypassrule Delta
            nwbypassrule_diff = self.db.get_chain_bypass_rules(ctx,
                                                               filters=None,
                                                               fields=None)
            for nwbypassrule in nwbypassrule_diff:
                fil = {}
                id = nwbypassrule['id']
                fil['chain_bypass_rule_id'] = [id]
                fil['operation'] = ['create']
                CompDelta = self.deltadb.get_chain_bypass_rules_deltas(ctx, fil)
                arr = sorted(CompDelta, key=lambda t: t['version_id'],
                             reverse=True)
                verid = arr[0]['version_id']

                nwbypassrule.update(
                    {'chain_bypass_rule_id': nwbypassrule['id'],
                     'operation': 'create', 'version_id': current_version})
                nwbypassrule_message = {}
                nwbypassrule_message.update(
                    {'method': 'create_chain_bypass_rules',
                     'payload': nwbypassrule})
                delta[verid] = nwbypassrule_message


            #NWchainset Delta
            nwchainset_diff = self.db.get_chainsets(ctx, filters=None,
                                                    fields=None)
            for nwchainset in nwchainset_diff:
                fil = {}
                id = nwchainset['id']
                fil['chainset_id'] = [id]
                fil['operation'] = ['create']
                CompDelta = self.deltadb.get_chainsets_deltas(ctx, fil)
                arr = sorted(CompDelta, key=lambda t: t['version_id'],
                             reverse=True)
                verid = arr[0]['version_id']
                nwchainset.update(
                    {'chainset_id': nwchainset['id'], 'operation': 'create',
                     'version_id': current_version})
                nwchainset_message = {}
                nwchainset_message.update(
                    {'method': 'create_chainsets', 'payload': nwchainset})
                delta[verid] = nwchainset_message


            #NWchainrule Delta
            nwchainrule_diff = self.db.get_chainset_rules(ctx, filters=None,
                                                          fields=None)
            for nwchainrule in nwchainrule_diff:
                fil = {}
                id = nwchainrule['id']
                fil['chain_rule_id'] = [id]
                fil['operation'] = ['create']
                CompDelta = self.deltadb.get_chainrules_deltas(ctx, fil)
                arr = sorted(CompDelta, key=lambda t: t['version_id'],
                             reverse=True)
                verid = arr[0]['version_id']
                nwchainrule.update(
                    {'chain_rule_id': nwchainrule['id'], 'operation': 'create',
                     'version_id': current_version})
                nwchainrule_message = {}
                nwchainrule_message.update(
                    {'method': 'create_chainrule', 'payload': nwchainrule})
                delta[verid] = nwchainrule_message


            #NWchainmap Delta
            nwchainmap_diff = self.db.get_chainmaps(ctx, filters=None,
                                                    fields=None)
            for nwchainmap in nwchainmap_diff:
                fil = {}
                id = nwchainmap['id']
                fil['chain_map_id'] = [id]
                fil['operation'] = ['create']
                CompDelta = self.deltadb.get_chainmaps_deltas(ctx, fil)
                arr = sorted(CompDelta, key=lambda t: t['version_id'],
                             reverse=True)
                verid = arr[0]['version_id']
                nwchainmap.update(
                    {'chain_map_id': nwchainmap['id'], 'operation': 'create',
                     'version_id': current_version})
                nwchainmap_message = {}
                nwchainmap_message.update(
                    {'method': 'create_chainmap', 'payload': nwchainmap})
                delta[verid] = nwchainmap_message


            #Appliance Instance Delta
            #app_instance_diff = self.db.get_appliance_instances(ctx, filters=None,
            #                                     fields=None)
            app_instance_diff = self.db.get_chain_appliance_map_instances(ctx, filters=None,
                                                 fields=None)
	    LOG.debug(_("APP INSTANCES = %s"), str(app_instance_diff))
            for app_instance in app_instance_diff:
                fil = {}
                id = app_instance['id']
                chain_app_id = app_instance['appliance_map_id']
                chain_id = None
                chain_app_details = self.db.get_chain_appliance_map(ctx, chain_app_id)
                if chain_app_details:
                    chain_id = chain_app_details['chain_id']
                fil['appliance_instance_id'] = [id]
                fil['operation'] = ['create']
                CompDelta = self.deltadb.get_appliance_instances_deltas(ctx, fil)
                arr = sorted(CompDelta, key=lambda t: t['version_id'],
                             reverse=True)
		LOG.debug(_("ARRAY = %s"), arr)
		LOG.debug(_("Version-ID = %s"), str(arr[0]['version_id']))
                verid = arr[0]['version_id']
                app_instance.update(
                    {'appliance_instance_id': app_instance['id'], 'operation': 'create',
                        'version_id': current_version, 'chain_appliance_id': chain_app_id,
                        'chain_id': chain_id})
                app_instance_message = {}
                app_instance_message.update(
                    {'method': 'create_appliance_instance', 'payload': app_instance})
                delta[verid] = app_instance_message

        LOG.debug(_("Delta to consumer from SFC = %s"), str(delta))
        return delta
