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

from nscs.crdservice.db import api as db_api
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common.gettextutils import _
from sfc.crdservice.db import sfc_db
from sfc.crdservice.extensions.sfcext import SFCPluginBase
from sfc.crdservice.common import constants
from sfc.crdservice.drivers.fsl_driver import SFCDriver
from sfc.crdservice.listener.sfc import SFCListener
from sfc.crdservice.plugins import delta
from sfc.crdservice.common import exceptions as sfc_exc
from nscs.crdservice.common import exceptions
LOG = logging.getLogger(__name__)


class SFCPlugin(SFCPluginBase, SFCListener):

    """
    Implementation of the Crd Network Service Plugin.
    DB related work is implemented in class SFCPluginDb
    """
    supported_extension_aliases = ["sfc"]

    def __init__(self):
        self.db = sfc_db.SFCPluginDb()
	self.sfcdelta = delta.SfcDelta()
        self.driver = SFCDriver.get_instance()
        db_api.register_models()
        super(SFCPlugin, self).__init__()

    def get_plugin_type(self):
        return constants.SFC

    def get_plugin_description(self):
        return "Crd Network Service Plugin"

    @staticmethod
    def _is_pending(obj):
        return obj['status'] in [constants.PENDING_CREATE,
                                 constants.PENDING_UPDATE,
                                 constants.PENDING_DELETE]

    def create_networkfunction(self, context, networkfunction):
        v = self.db.create_networkfunction(context, networkfunction)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'networkfunctions_delta':v})
        result_delta = self.sfcdelta.create_networkfunctions_delta(context,delta)
        return data

    def update_networkfunction(self, context, networkfunction_id,
                               networkfunction):
        # LOG.debug(_('Update networkfunction %s'), networkfunction_id)
        v = self.db.update_networkfunction(context, networkfunction_id,
                                               networkfunction)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'networkfunctions_delta':v})
        result_delta = self.sfcdelta.create_networkfunctions_delta(context,delta)
        return data

    def delete_networkfunction(self, context, networkfunction_id):
        # LOG.debug(_('Delete networkfunction %s'), networkfunction_id)
	v = self.get_networkfunction(context,networkfunction_id)
        self.db.delete_networkfunction(context, networkfunction_id)
	v.update({'operation' : 'delete'})
        delta={}
        delta.update({'networkfunctions_delta':v})
        result_delta = self.sfcdelta.create_networkfunctions_delta(context,delta)

    def get_networkfunction(self, context, networkfunction_id, fields=None):
        # LOG.debug(_('Get networkfunction %s'), networkfunction_id)
        return self.db.get_networkfunction(context, networkfunction_id,
                                           fields)

    def get_networkfunctions(self, context, filters=None, fields=None):
        # LOG.debug(_('Get networkfunctions'))
        return self.db.get_networkfunctions(context, filters, fields)

    def create_config_handle(self, context, config_handle):
        v = self.db.create_config_handle(context, config_handle)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'config_handles_delta':v})
        result_delta = self.sfcdelta.create_config_handles_delta(context,delta)
        return data

    def update_config_handle(self, context, config_handle_id, config_handle):
        # LOG.debug(_('Update config_handle %s'), config_handle_id)
        v = self.db.update_config_handle(context, config_handle_id,
                                             config_handle)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'config_handles_delta':v})
        result_delta = self.sfcdelta.create_config_handles_delta(context,delta)
        return data

    def delete_config_handle(self, context, config_handle_id):
        # LOG.debug(_('Delete config_handle %s'), config_handle_id)
	v = self.get_config_handle(context,config_handle_id)
        self.db.delete_config_handle(context, config_handle_id)
	v.update({'operation' : 'delete'})
        delta={}
        delta.update({'config_handles_delta':v})
        result_delta = self.sfcdelta.create_config_handles_delta(context,delta)

    def get_config_handle(self, context, config_handle_id, fields=None):
        # LOG.debug(_('Get config_handle %s'), config_handle_id)
        return self.db.get_config_handle(context, config_handle_id, fields)

    def get_config_handles(self, context, filters=None, fields=None):
        # LOG.debug(_('Get config_handles'))
        return self.db.get_config_handles(context, filters, fields)

    def create_category(self, context, category):
        v = self.db.create_category(context, category)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'categories_delta':v})
        result_delta = self.sfcdelta.create_categories_delta(context,delta)
        return data

    def update_category(self, context, category_id, category):
        v = self.db.update_category(context, category_id, category)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'categories_delta':v})
        result_delta = self.sfcdelta.create_categories_delta(context,delta)
        return data

    def delete_category(self, context, category_id):
	v = self.get_category(context,category_id)
        self.db.delete_category(context, category_id)
	v.update({'operation' : 'delete'})
        delta={}
        delta.update({'categories_delta':v})
        result_delta = self.sfcdelta.create_categories_delta(context,delta)

    def get_category(self, context, category_id, fields=None):
        # LOG.debug(_('Get category %s'), category_id)
        return self.db.get_category(context, category_id, fields)

    def get_categories(self, context, filters=None, fields=None):
        # LOG.debug(_('Get categories'))
        return self.db.get_categories(context, filters, fields)

    def create_category_nf_map(self, context, nf_map, category_id):
        v = self.db.create_category_networkfunction(context, nf_map,
                                                    category_id)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'category_networkfunctions_delta':v})
        result_delta = self.sfcdelta.create_category_networkfunctions_delta(context,delta)
        return data

    def delete_category_nf_map(self, context, networkfunction_id,
                               category_id):
        LOG.debug(_('Delete category_networkfunction %s'),
                  networkfunction_id)
	v = self.get_category_nf_map(context, networkfunction_id, category_id)
        self.db.delete_category_networkfunction(context, category_id,
                                                networkfunction_id)
	data = v
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'category_networkfunctions_delta':v})
        result_delta = self.sfcdelta.create_category_networkfunctions_delta(context,delta)

    def get_category_nf_map(self, context, networkfunction_id, category_id,
                            fields=None):
        # LOG.debug(_('Get category_networkfunction %s'), category_id)
        return self.db.get_category_networkfunction(context, category_id,
                                                    networkfunction_id,
                                                    fields)

    def create_vendor(self, context, vendor):
        v = self.db.create_vendor(context, vendor)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'vendors_delta':v})
        result_delta = self.sfcdelta.create_vendors_delta(context,delta)
        return data

    def update_vendor(self, context, vendor_id, vendor):
        # LOG.debug(_('Update vendor %s'), vendor_id)
        v = self.db.update_vendor(context, vendor_id, vendor)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'vendors_delta':v})
        result_delta = self.sfcdelta.create_vendors_delta(context,delta)
        return data

    def delete_vendor(self, context, vendor_id):
        # LOG.debug(_('Delete vendor %s'), vendor_id)
	v = self.get_vendor(context, vendor_id)
        self.db.delete_vendor(context, vendor_id)
	v.update({'operation' : 'delete'})
        delta={}
        delta.update({'vendors_delta':v})
        result_delta = self.sfcdelta.create_vendors_delta(context,delta)

    def get_vendor(self, context, vendor_id, fields=None):
        # LOG.debug(_('Get vendor %s'), vendor_id)
        return self.db.get_vendor(context, vendor_id, fields)

    def get_vendors(self, context, filters=None, fields=None):
        # LOG.debug(_('Get vendors'))
        return self.db.get_vendors(context, filters, fields)

    def create_appliance(self, context, appliance):
        v = self.db.create_appliance(context, appliance)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'appliances_delta':v})
        result_delta = self.sfcdelta.create_appliances_delta(context,delta)
        return data

    def update_appliance(self, context, appliance_id, appliance):
        # LOG.debug(_('Update appliance %s'), appliance_id)
        v = self.db.update_appliance(context, appliance_id, appliance)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'appliances_delta':v})
        result_delta = self.sfcdelta.create_appliances_delta(context,delta)
        return data

    def delete_appliance(self, context, appliance_id):
        # LOG.debug(_('Delete appliance %s'), appliance_id)
	v = self.get_appliance(context, appliance_id)
        self.db.delete_appliance(context, appliance_id)
	data = v
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'appliances_delta':v})
        result_delta = self.sfcdelta.create_appliances_delta(context,delta)

    def get_appliance(self, context, appliance_id, fields=None):
        # LOG.debug(_('Get appliance %s'), appliance_id)
        return self.db.get_appliance(context, appliance_id, fields)

    def get_appliances(self, context, filters=None, fields=None):
        # LOG.debug(_('Get appliances'))
        return self.db.get_appliances(context, filters, fields)

    def create_chain(self, context, chain):
        v = self.db.create_chain(context, chain)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'chains_delta':v})
        result_delta = self.sfcdelta.create_chains_delta(context,delta)
        return data

    def update_chain(self, context, chain_id, chain):
        # LOG.debug(_('Update chain %s'), chain_id)
        v = self.db.update_chain(context, chain_id, chain)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'chains_delta':v})
        result_delta = self.sfcdelta.create_chains_delta(context,delta)
        return data

    def delete_chain(self, context, chain_id):
        # LOG.debug(_('Delete chain %s'), chain_id)
	v = self.get_chain(context, chain_id)
	filters = {}
	filters['chain_id'] = [chain_id]
	chain_apps = self.get_chain_appliances(context, filters=filters)
	if chain_apps:
	    LOG.error(_('There are some dependencies still there for the Chain: %s'), str(chain_id))
	    raise sfc_exc.ChainRefExists(chain_id=chain_id)
	    #raise exceptions.CrdException()
	else:
	    self.db.delete_chain(context, chain_id)
	    data = v
	    v.update({'operation' : 'delete'})
	    delta={}
	    delta.update({'chains_delta':v})
	    result_delta = self.sfcdelta.create_chains_delta(context,delta)

    def get_chain(self, context, chain_id, fields=None):
        # LOG.debug(_('Get chain %s'), chain_id)
        return self.db.get_chain(context, chain_id, fields)

    def get_chains(self, context, filters=None, fields=None):
        # LOG.debug(_('Get chains'))
        return self.db.get_chains(context, filters, fields)

    def create_chain_appliance(self, context, appliance, chain_id):
        v = self.db.create_chain_appliance_map(context, appliance,
                                               chain_id)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'chain_appliances_delta':v})
        result_delta = self.sfcdelta.create_chain_appliances_delta(context,delta)
        return data

    def update_chain_appliance(self, context, appliance_map_id, chain_id,
                                   appliance_map):
        # LOG.debug(_('Update appliance_map %s'), appliance_map_id)
        v = self.db.update_chain_appliance_map(context, appliance_map_id,
                                                   chain_id, appliance_map)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'chain_appliances_delta':v})
        result_delta = self.sfcdelta.create_chain_appliances_delta(context,delta)
        return data

    def delete_chain_appliance(self, context, appliance_id, chain_id):
        # LOG.debug(_('Delete appliance_map %s'), appliance_map_id)
	v = self.get_chain_appliance(context, appliance_id, chain_id)
	appliance_map_id = v['id']
        self.db.delete_chain_appliance_map(context, appliance_map_id,
                                           chain_id)
	data = v
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'chain_appliances_delta':v})
        result_delta = self.sfcdelta.create_chain_appliances_delta(context,delta)

    def get_chain_appliance(self, context, appliance_id, chain_id,
                                fields=None):
        # LOG.debug(_('Get appliance_map %s'), appliance_map_id)
        #return self.db.get_chain_appliance_map(context, appliance_map_id,
        #                                       chain_id, fields)
	filters = {}
	filters['appliance_id'] = [appliance_id]
	filters['chain_id'] = [chain_id]
	try:
	    chain_appliances = self.db.get_chain_appliance_maps(context, filters, fields)
	    if chain_appliances:
		chain_appliance_map_id = chain_appliances[0]['id']
		return self.db.get_chain_appliance_map(context, chain_appliance_map_id,
						       chain_id, fields)
	    else:
		raise sfc_exc.ChainApplianceNotFound(chain_id=chain_id, appliance_id=appliance_id)
	except:
	    raise sfc_exc.ChainApplianceNotFound(chain_id=chain_id, appliance_id=appliance_id)
	

    def get_chain_appliances(self, context, filters=None, fields=None,
                                 chain_id=None):
        # LOG.debug(_('Get appliance_maps'))
	if chain_id:
	    filters['chain_id'] = [chain_id]
        return self.db.get_chain_appliance_maps(context, filters, fields)

    def create_chain_bypass_rule(self, context, bypass_rule, chain_id):
        v = self.db.create_chain_bypass_rule(context, bypass_rule, chain_id)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'chain_bypass_rules_delta':v})
        result_delta = self.sfcdelta.create_chain_bypass_rules_delta(context,delta)
	
        return data

    def update_chain_bypass_rule(self, context, rule_id, chain_id,
                                 bypass_rule):
        # LOG.debug(_('Update rule %s'), rule_id)
        v = self.db.update_chain_bypass_rule(context, rule_id, chain_id,
                                                 bypass_rule)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'chain_bypass_rules_delta':v})
        result_delta = self.sfcdelta.create_chain_bypass_rules_delta(context,delta)
        return data

    def delete_chain_bypass_rule(self, context, rule_id, chain_id):
        # LOG.debug(_('Delete rule %s'), rule_id)
	v = self.get_chain_bypass_rule(context, rule_id, chain_id)
        self.db.delete_chain_bypass_rule(context, rule_id, chain_id)
	data = v
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'chain_bypass_rules_delta':v})
        result_delta = self.sfcdelta.create_chain_bypass_rules_delta(context,delta)

    def get_chain_bypass_rule(self, context, rule_id, chain_id, fields=None):
        # LOG.debug(_('Get rule %s'), rule_id)
        return self.db.get_chain_bypass_rule(context, rule_id, chain_id,
                                             fields)

    def get_chain_bypass_rules(self, context, filters=None, fields=None,
                               chain_id=None):
        # LOG.debug(_('Get rules'))
        filters['chain_id'] = [chain_id]
        return self.db.get_chain_bypass_rules(context, filters, fields)

    def create_chainset(self, context, chainset):
        # LOG.debug(_('create_chainset'))
        v = self.db.create_chainset(context, chainset)
	data = v
	###Insert default Zone
	#zone = {'zone':{'zone': 'default', 'direction': 'left'}}
	#self.create_chainset_zone(context, zone, data['id'])
	if data['name'] != 'Default Chainset':
	    v.update({'operation' : 'create'})
	    delta={}
	    delta.update({'chainsets_delta':v})
	    result_delta = self.sfcdelta.create_chainsets_delta(context,delta)
        return data

    def update_chainset(self, context, chainset_id, chainset):
        # LOG.debug(_('Update chainset %s'), chainset_id)
        v = self.db.update_chainset(context, chainset_id, chainset)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'chainsets_delta':v})
        result_delta = self.sfcdelta.create_chainsets_delta(context,delta)
        return data

    def delete_chainset(self, context, chainset_id):
        # LOG.debug(_('Delete chainset %s'), chainset_id)
	v = self.get_chainset(context, chainset_id)
        self.db.delete_chainset(context, chainset_id)
	data = v
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'chainsets_delta':v})
        result_delta = self.sfcdelta.create_chainsets_delta(context,delta)
	

    def get_chainset(self, context, chainset_id, fields=None):
        # LOG.debug(_('Get chainset %s'), chainset_id)
        return self.db.get_chainset(context, chainset_id, fields)

    def get_chainsets(self, context, filters=None, fields=None):
        # LOG.debug(_('Get chainsets'))
        return self.db.get_chainsets(context, filters, fields)

    def create_chainset_rule(self, context, rule, chainset_id):
        v = self.db.create_chainset_rule(context, rule, chainset_id)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'chainrules_delta':v})
	cbr = v
	chain_id=cbr.get('chain_id') or ''
	if chain_id:
	    result_delta = self.sfcdelta.create_chainrules_delta(context,delta)
        return data

    def update_chainset_rule(self, context, rule_id, chainset_id, rule):
        # LOG.debug(_('Update rule %s'), rule_id)
        v = self.db.update_chainset_rule(context, rule_id, chainset_id,
                                             rule)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'chainrules_delta':v})
	cbr = v
	chain_id=cbr.get('chain_id') or ''
	if chain_id:
	    result_delta = self.sfcdelta.create_chainrules_delta(context,delta)
        return data

    def delete_chainset_rule(self, context, rule_id, chainset_id):
        # LOG.debug(_('Delete rule %s'), rule_id)
	v = self.get_chainset_rule(context, rule_id, chainset_id)
        self.db.delete_chainset_rule(context, rule_id, chainset_id)
	data = v
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'chainrules_delta':v})
	cbr = v
	chain_id=cbr.get('chain_id') or ''
	if chain_id:
	    result_delta = self.sfcdelta.create_chainrules_delta(context,delta)

    def get_chainset_rule(self, context, rule_id, chainset_id, fields=None):
        # LOG.debug(_('Get rule %s'), rule_id)
        return self.db.get_chainset_rule(context, rule_id, chainset_id,
                                         fields)

    def get_chainset_rules(self, context, filters=None, fields=None,
                           chainset_id=None):
        # LOG.debug(_('Get rules'))
        filters['chainset_id'] = [chainset_id]
        return self.db.get_chainset_rules(context, filters, fields)

    # # Chain map Related
    def create_chainmap(self, context, chainmap):
        v = self.db.create_chainmap(context, chainmap)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'chainmaps_delta':v})
        result_delta = self.sfcdelta.create_chainmaps_delta(context,delta)
        return data

    def update_chainmap(self, context, chainmap_id, chainmap):
        # LOG.debug(_('Update chainmap %s'), chainmap_id)
        v = self.db.update_chainmap(context, chainmap_id, chainmap)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'chainmaps_delta':v})
        result_delta = self.sfcdelta.create_chainmaps_delta(context,delta)
        return data

    def delete_chainmap(self, context, chainmap_id):
        # LOG.debug(_('Delete chainmap %s'), chainmap_id)
	v = self.get_chainmap(context, chainmap_id)
        self.db.delete_chainmap(context, chainmap_id)
	data = v
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'chainmaps_delta':v})
        result_delta = self.sfcdelta.create_chainmaps_delta(context,delta)

    def get_chainmap(self, context, chainmap_id, fields=None):
        # LOG.debug(_('Get chainmap %s'), chainmap_id)
        return self.db.get_chainmap(context, chainmap_id, fields)

    def get_chainmaps(self, context, filters=None, fields=None):
        # LOG.debug(_('Get chainmaps'))
        return self.db.get_chainmaps(context, filters, fields)

    def create_launch(self, context, launch):
        # LOG.debug(_('Launch  Chain'))
        n = launch['launch']
        rule_id = n['rule_id']
        chainset_id = n['chainset_id']
        chainmap_id = n['chainmap_id']
        res = {'rule_id': rule_id}
        self.driver.launch_chain(context, chainset_id, chainmap_id, rule_id)
        return res

    def create_vlanquota(self, context, vlanquota):
        v = self.db.create_vlanquota(context, vlanquota)
        return v

    def update_vlanquota(self, context, vlanquota_id, vlanquota):
        # LOG.debug(_('Update vlanquota %s'), vlanquota_id)
        v_new = self.db.update_vlanquota(context, vlanquota_id, vlanquota)
        return v_new

    def delete_vlanquota(self, context, vlanquota_id):
        # LOG.debug(_('Delete vlanquota %s'), vlanquota_id)
        self.db.delete_vlanquota(context, vlanquota_id)

    def get_vlanquota(self, context, vlanquota_id, fields=None):
        # LOG.debug(_('Get vlanquota %s'), vlanquota_id)
        return self.db.get_vlanquota(context, vlanquota_id, fields)

    def get_vlanquotas(self, context, filters=None, fields=None):
        # LOG.debug(_('Get vlanquotas'))
        return self.db.get_vlanquotas(context, filters, fields)

    def create_chain_appliance_instance(self, context, chain_id, appliance_id, instance):
	chain_appliance = self.get_chain_appliance(context, appliance_id, chain_id)
	appliance_map_id = chain_appliance['id']
	instance['instance'].update({'appliance_map_id': appliance_map_id})
	v = self.db.create_chain_appliance_map_instance(context, instance)
	data = v
	v.update({'operation' : 'create'})
	v.update({'chain_id': chain_id})
	v.update({'appliance_id': appliance_id})
        delta={}
        delta.update({'appliance_instances_delta':v})
        result_delta = self.sfcdelta.create_appliance_instances_delta(context,delta)
	return data
    
    def update_chain_appliance_instance(self, context, chain_appliance_map_instance_id, chain_appliance_map_instance):
        v = self.db.update_chain_appliance_map_instance(context, chain_appliance_map_instance_id, chain_appliance_map_instance)
	data = v
	v.update({'operation' : 'update'})
        delta={}
        delta.update({'appliance_instances_delta':v})
        result_delta = self.sfcdelta.create_appliance_instances_delta(context,delta)
	return data
    
    def delete_chain_appliance_instance(self, context, instance_id):
        filters = dict()
        filters['instance_uuid'] = [instance_id]
        chain_appliance_map_instances = self.db.get_chain_appliance_map_instances(self.context, filters=filters)
	LOG.debug("########################################")
	LOG.debug(_("Chain Appliance Instances: %s"), str(chain_appliance_map_instances))
	LOG.debug("########################################")
        for app_instance in chain_appliance_map_instances:
	    v = self.get_chain_appliance_instance(context, app_instance['id'])
            self.db.delete_chain_appliance_map_instance(self.context, app_instance['id'])
	    data = v
	    v.update({'operation' : 'delete'})
	    delta={}
	    delta.update({'appliance_instances_delta':v})
	    result_delta = self.sfcdelta.create_appliance_instances_delta(context,delta)
	    
    def get_chain_appliance_instance(self, context, chain_appliance_map_instance_id, appliance_id=None, chain_id=None, fields=None):
        return self.db._get_chain_appliance_map_instance_handle(context, chain_appliance_map_instance_id)
    
    def get_chain_appliance_instances(self, context, filters=None, fields=None, chain_id=None, appliance_id=None):
	chain_appliance = self.get_chain_appliance(context, appliance_id, chain_id)
	appliance_map_id = chain_appliance['id']
        filters['appliance_map_id'] = [appliance_map_id]
        return self.db.get_chain_appliance_map_instances(context, filters, fields)

    def send_inst_delete_driver(self, instance_id, tenant_id, hostname):
        self.driver.send_delete_instance(instance_id, tenant_id, hostname)

    def sfc_init_consumer(self, context, **kwargs):
        """
        This function is called when ever any consumer is started
        """
        LOG.debug(_("In Init Consumer for SFC.......KWArgs = %s"),
                  str(kwargs))
        payload = kwargs['consumer']
        payload = payload['payload']
        return self.sfcdelta.sfc_init(self.context, payload['version'],
				      payload['hostname'])


    def get_nsdelta(self, context, keyword, fields=None):
        delta = {}
        method = "get_"+keyword+"_deltas"
        obj = getattr(self.sfcdelta, method)
        delta = obj(context)
        res = {'delta': delta , 'keyword' : keyword, 'tenant_id' : context.tenant_id, 'id' : context.tenant_id}
        #LOG.debug('Get res  %s' % str(res))
        return res
    
    def create_chainset_zone(self, context, zone, chainset_id):
        v = self.db.create_chainset_zone(context, zone, chainset_id)
	data = v
        v.update({'operation' : 'create'})
        delta={}
        delta.update({'chainset_zones_delta':v})
        result_delta = self.sfcdelta.create_chainset_zone_deltas(context,delta)
        return data

    def update_chainset_zone(self, context, zone_id, chainset_id, zone):
        # LOG.debug(_('Update zone %s'), zone_id)
        v = self.db.update_chainset_zone(context, zone_id, chainset_id,
                                             zone)
	data = v
        v.update({'operation' : 'update'})
        delta={}
        delta.update({'chainset_zones_delta':v})
        result_delta = self.sfcdelta.create_chainset_zone_deltas(context,delta)
        return data

    def delete_chainset_zone(self, context, zone_id, chainset_id):
        # LOG.debug(_('Delete zone %s'), zone_id)
	v = self.get_chainset_zone(context, zone_id, chainset_id)
        self.db.delete_chainset_zone(context, zone_id, chainset_id)
	data = v
        v.update({'operation' : 'delete'})
        delta={}
        delta.update({'chainset_zones_delta':v})
        result_delta = self.sfcdelta.create_chainset_zone_deltas(context,delta)

    def get_chainset_zone(self, context, zone_id, chainset_id, fields=None):
        # LOG.debug(_('Get zone %s'), zone_id)
        return self.db.get_chainset_zone(context, zone_id, chainset_id,
                                         fields)

    def get_chainset_zones(self, context, filters=None, fields=None,
                           chainset_id=None):
        # LOG.debug(_('Get zones'))
        filters['chainset_id'] = [chainset_id]
        return self.db.get_chainset_zones(context, filters, fields)
    
    def create_vmscaleout(self, context, vmscaleout):
        # LOG.debug(_('Launch  Chain'))
        n = vmscaleout['vmscaleout']
        instance_id = n['instance_id']
	###Get Appliance Details###############
	filters = {}
	filters['instance_uuid'] = [instance_id]
	
	chainset_id = None
	chain_network_map_id = None
	rule_id = None
	
	appliance_instances = self.db.get_chain_appliance_map_instances(context, filters=filters)
	if appliance_instances:
	    appliance_instance_details = appliance_instances[0]
	    appliance_map_id = appliance_instance_details['appliance_map_id']
	    appliance_map_details = self.db.get_chain_appliance_map(context,
								    appliance_map_id)
	    chain_id = appliance_map_details['chain_id']
	    appliance_id = appliance_map_details['appliance_id']
	    filters = {}
	    filters['chain_id'] = [chain_id]
	    chain_sel_rules = self.db.get_chainset_rules(context, filters=filters)
	    LOG.debug("########################################")
	    LOG.debug(_("Chain ID: %s"), str(chain_id))
	    LOG.debug(_("Chain Selection Rules: %s"), str(chain_sel_rules))
	    LOG.debug("########################################")
	    if chain_sel_rules:
		rule_details = chain_sel_rules[0]
		chainset_id = rule_details['chainset_id']
		rule_id = rule_details['id']
		filters = {}
		filters['chainset_id'] = [chainset_id]
		chain_network_maps = self.get_chainmaps(context, filters=filters)
		if chain_network_maps:
		    chain_net_map_details = chain_network_maps[0]
		    chain_network_map_id = chain_net_map_details['id']
		    
	    LOG.debug("########################################")
	    LOG.debug(_("Chainset ID: %s, Chain-Network-Map ID: %s, Rule ID: %s"), str(chainset_id), str(chain_network_map_id), str(rule_id))
	    LOG.debug("########################################")
	    ####Check all the required arguments to run launch_chain in fsl_driver
	    if chainset_id and chain_network_map_id and rule_id:
		LOG.debug("########################################")
		LOG.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
		LOG.debug(_("Scaling out Instance: %s"), str(instance_id))
		LOG.debug(_("Launching Instance ... "))
		LOG.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
		LOG.debug("########################################")
		self.driver.launch_chain(context, chainset_id, chain_network_map_id, rule_id)
	    else:
		LOG.error(_("@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%"))
		LOG.error(_("@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%"))
		LOG.error(_("One of the required fields: chainset_id/chain_network_map_id/rule_id is missing to Launch Instance!!!"))
		LOG.error(_("@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%"))
		LOG.error(_("@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%@$%"))
	    
	    
        res = {'vmscaleout': {'instance_id': instance_id}}
	return res