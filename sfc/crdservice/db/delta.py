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

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc, relationship, backref
import netaddr

from nscs.crdservice.api.v2 import attributes
from nscs.crdservice.common import exceptions as q_exc
from nscs.crdservice.db import api as qdbapi
from nscs.crdservice.db import model_base
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import uuidutils
from nscs.crdservice.plugins.common import constants
from nscs.crdservice.common import utils
from nscs.crdservice.openstack.common import timeutils
from nscs.crdservice.db import db_base_plugin_v2

from nscs.crdservice.openstack.common import rpc
from nscs.crdservice.openstack.common.rpc.proxy import RpcProxy as rpc_proxy
from sfc.crdservice.common import exceptions as sfc_exc


import datetime
LOG = logging.getLogger(__name__)

############    
#Network Service  Tables added by Veera
############
class HasTenant(object):
    """Tenant mixin, add to subclasses that have a tenant."""
    # NOTE(jkoelker) tenant_id is just a free form string ;(
    tenant_id = sa.Column(sa.String(255))


class HasId(object):
    """id mixin, add to subclasses that have an id."""
    id = sa.Column(sa.String(36), primary_key=True, default=uuidutils.generate_uuid)
    
 
###Networkfunctions table for delta
class sfc_networkfunctions_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    networkfunction_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50))
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)

###Categories delta table    
class sfc_categories_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    category_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50))
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)


###Category Networkfunctions Delta 
class sfc_category_networkfunctions_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    category_networkfunction_id = sa.Column(sa.String(36), nullable=False)
    category_id = sa.Column(sa.String(36))
    networkfunction_id = sa.Column(sa.String(36))
    shared = sa.Column(sa.Boolean)
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)

######Vendors Delta    
class sfc_vendors_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    vendor_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50))
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
class sfc_appliances_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    appliance_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50))
    category_id = sa.Column(sa.String(36))
    vendor_id = sa.Column(sa.String(36))
    image_id = sa.Column(sa.String(36))
    flavor_id = sa.Column(sa.String(36))
    security_group_id = sa.Column(sa.String(36))
    form_factor_type = sa.Column(sa.String(36))
    type = sa.Column(sa.String(36), nullable=False)
    load_share_algorithm = sa.Column(sa.String(50), nullable=False)
    high_threshold = sa.Column(sa.String(50), nullable=False)
    low_threshold = sa.Column(sa.String(50), nullable=False)
    pkt_field_to_hash = sa.Column(sa.String(255), nullable=False)
    load_indication_type = sa.Column(sa.String(50), nullable=False)
    config_handle_id = sa.Column(sa.String(36))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
    
class sfc_chains_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    chain_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50))
    auto_boot = sa.Column(sa.Boolean)
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
class sfc_chain_appliances_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    chain_appliance_map_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50))
    chain_id = sa.Column(sa.String(36))
    appliance_id = sa.Column(sa.String(36))
    sequence_number = sa.Column(sa.Integer)
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)

class sfc_chain_bypass_rules_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    chain_bypass_rule_id = sa.Column(sa.String(36), nullable=False)
    chain_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50))
    src_mac_type = sa.Column(sa.String(50))
    dest_mac_type = sa.Column(sa.String(50))
    src_mac = sa.Column(sa.String(50))
    dest_mac = sa.Column(sa.String(50))
    eth_type = sa.Column(sa.String(50))
    eth_value = sa.Column(sa.String(50))
    sip_type = sa.Column(sa.String(50))
    dip_type  = sa.Column(sa.String(50))
    sip_start = sa.Column(sa.String(50))
    sip_end = sa.Column(sa.String(50))
    dip_start = sa.Column(sa.String(50))
    dip_end = sa.Column(sa.String(50))
    sp_type = sa.Column(sa.String(50))
    dp_type = sa.Column(sa.String(50))
    sp_start = sa.Column(sa.String(50))
    sp_end = sa.Column(sa.String(50))
    dp_start = sa.Column(sa.String(50))
    dp_end  = sa.Column(sa.String(50))
    ip_protocol = sa.Column(sa.String(50))
    nwservice_count = sa.Column(sa.String(50))
    nwservice_names = sa.Column(sa.String(50))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
### Chainset for delta
class sfc_chainsets_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    chainset_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50), nullable=False)
    zonefull = sa.Column(sa.Boolean)
    direction = sa.Column(sa.String(50))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)

class sfc_chainrules_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    chain_rule_id = sa.Column(sa.String(36))
    name = sa.Column(sa.String(50))
    chainset_id = sa.Column(sa.String(36))
    chain_id = sa.Column(sa.String(36))
    src_mac_type = sa.Column(sa.String(50))
    dest_mac_type = sa.Column(sa.String(50))
    src_mac = sa.Column(sa.String(50))
    dest_mac = sa.Column(sa.String(50))
    eth_type = sa.Column(sa.String(50))
    eth_value = sa.Column(sa.String(50))
    sip_type = sa.Column(sa.String(50))
    dip_type  = sa.Column(sa.String(50))
    sip_start = sa.Column(sa.String(50))
    sip_end = sa.Column(sa.String(50))
    dip_start = sa.Column(sa.String(50))
    dip_end = sa.Column(sa.String(50))
    sp_type = sa.Column(sa.String(50))
    dp_type = sa.Column(sa.String(50))
    sp_start = sa.Column(sa.String(50))
    sp_end = sa.Column(sa.String(50))
    dp_start = sa.Column(sa.String(50))
    dp_end  = sa.Column(sa.String(50))
    ip_protocol = sa.Column(sa.String(50))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
class sfc_chainmaps_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 crd FSL service."""
    chain_map_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(50))
    type = sa.Column(sa.String(50))
    chainset_id = sa.Column(sa.String(36))
    inbound_network_id = sa.Column(sa.String(36))
    outbound_network_id = sa.Column(sa.String(36))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
  
class sfc_appliance_instances_delta(model_base.BASEV2, HasId, HasTenant):
    appliance_instance_id = sa.Column(sa.String(36))
    appliance_map_id = sa.Column(sa.String(36))
    instance_uuid = sa.Column(sa.String(36))
    network_id = sa.Column(sa.String(36))
    vlan_in = sa.Column(sa.Integer)
    vlan_out = sa.Column(sa.Integer)
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)
    
class sfc_chainset_zone_delta(model_base.BASEV2, HasId, HasTenant):
    """Represents a SFC Chainset Zone Delta."""
    zone_id = sa.Column(sa.String(36))
    zone = sa.Column(sa.String(50))
    direction = sa.Column(sa.String(50))
    chainset_id = sa.Column(sa.String(36))
    operation = sa.Column(sa.String(255), nullable=False)
    user_id = sa.Column(sa.String(36),nullable=False)
    logged_at = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=False)
    version_id = sa.Column(sa.Integer, sa.ForeignKey('crd_versions.runtime_version'), nullable=False)

class SfcDeltaDb(db_base_plugin_v2.CrdDbPluginV2):
    """
    A class that wraps the implementation of the Crd
    nwservices plugin database access interface using SQLAlchemy models.

    As opposed to all other DB plugins NwServicePluginDb does not
    implement plugin interface. nwservicesPlugin follows "has-a" instead of
    "is-a" relation with db-plugin. The main reason is that Db plugin is
    called not only by plugin, but also by notify handler and direct calls
    are a logical way.
    """

    ######################### NetworkFunction Delta ###############################   
    def _make_networkfunctions_delta_dict(self, networkfunctions_delta, fields=None):
        res = {'id': networkfunctions_delta['id'],
               'networkfunction_id': networkfunctions_delta['networkfunction_id'],
               'name': networkfunctions_delta['name'],
               'tenant_id': networkfunctions_delta['tenant_id'],
               'description': networkfunctions_delta['description'],
               'shared': networkfunctions_delta['shared'],
               'operation': networkfunctions_delta['operation'],
               'user_id': networkfunctions_delta['user_id'],
               'logged_at': networkfunctions_delta['logged_at'],
               'version_id': networkfunctions_delta['version_id']}
        return self._fields(res, fields)
    
    def get_networkfunctions_delta(self, context, id, fields=None):
        networkfunctions_delta = self._get_networkfunctions_delta(context, id)
        return self._make_networkfunctions_delta_dict(networkfunctions_delta, fields)
        
    def get_networkfunctions_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_networkfunctions_delta,
                                    self._make_networkfunctions_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_networkfunctions_delta(self, context, networkfunctions_delta):
        n = networkfunctions_delta['networkfunctions_delta']
        
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            networkfunctions_delta = sfc_networkfunctions_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         networkfunction_id=n['id'],
                                         name=n['name'],
                                         description=n['description'],
                                         shared=n['shared'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(networkfunctions_delta)
        payload = self._make_networkfunctions_delta_dict(networkfunctions_delta)
        method = n['operation']+"_networkfunction"
        return self._make_networkfunctions_delta_dict(networkfunctions_delta)
    
    def _get_networkfunctions_delta(self, context, id):
        try:
            networkfunctions_delta = self._get_by_id(context, sfc_networkfunctions_delta, id)
        except exc.NoResultFound:
            raise q_exc.networkfunctions_deltaNotFound(networkfunctions_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple networkfunctions_deltas match for %s' % id)
            raise q_exc.networkfunctions_deltaNotFound(networkfunctions_delta_id=id)
        return networkfunctions_delta

       
    ######################### Category Delta ###############################   
    def _make_categories_delta_dict(self, categories_delta, fields=None):
        res = {'id': categories_delta['id'],
               'category_id': categories_delta['category_id'],
               'name': categories_delta['name'],
               'tenant_id': categories_delta['tenant_id'],
               'description': categories_delta['description'],
               'shared': categories_delta['shared'],
               'operation': categories_delta['operation'],
               'user_id': categories_delta['user_id'],
               'logged_at': categories_delta['logged_at'],
               'version_id': categories_delta['version_id']}
        return self._fields(res, fields)
    
    def get_categories_delta(self, context, id, fields=None):
        categories_delta = self._get_categories_delta(context, id)
        return self._make_categories_delta_dict(categories_delta, fields)
        
    def get_categories_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_categories_delta,
                                    self._make_categories_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_categories_delta(self, context, categories_delta):
        n = categories_delta['categories_delta']
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            categories_delta = sfc_categories_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         category_id=n['id'],
                                         name=n['name'],
                                         description=n['description'],
                                         shared=n['shared'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(categories_delta)
        payload = self._make_categories_delta_dict(categories_delta)
        method = n['operation']+"_category"
        #rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg(method,payload=payload))
        return self._make_categories_delta_dict(categories_delta)
    
    def _get_categories_delta(self, context, id):
        try:
            categories_delta = self._get_by_id(context, sfc_categories_delta, id)
        except exc.NoResultFound:
            raise q_exc.categories_deltaNotFound(categories_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple categories_deltas match for %s' % id)
            raise q_exc.categories_deltaNotFound(categories_delta_id=id)
        return categories_delta
    
    
    ######################### Category Netwrokfunction Delta ###############################   
    def _make_category_networkfunctions_delta_dict(self, category_networkfunctions_delta, fields=None):
        res = {'id': category_networkfunctions_delta['id'],
               'category_networkfunction_id': category_networkfunctions_delta['category_networkfunction_id'],
               'category_id': category_networkfunctions_delta['category_id'],
               'tenant_id': category_networkfunctions_delta['tenant_id'],
               'networkfunction_id': category_networkfunctions_delta['networkfunction_id'],
               'shared': category_networkfunctions_delta['shared'],
               'operation': category_networkfunctions_delta['operation'],
               'user_id': category_networkfunctions_delta['user_id'],
               'logged_at': category_networkfunctions_delta['logged_at'],
               'version_id': category_networkfunctions_delta['version_id']}
        return self._fields(res, fields)
    
    def get_category_networkfunctions_delta(self, context, id, fields=None):
        category_networkfunctions_delta = self._get_category_networkfunctions_delta(context, id)
        return self._make_category_networkfunctions_delta_dict(category_networkfunctions_delta, fields)
        
    def get_category_networkfunctions_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_category_networkfunctions_delta,
                                    self._make_category_networkfunctions_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_category_networkfunctions_delta(self, context, category_networkfunctions_delta):
        n = category_networkfunctions_delta['category_networkfunctions_delta']
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            category_networkfunctions_delta = sfc_category_networkfunctions_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         category_networkfunction_id=n['id'],
                                         category_id=n['category_id'],
                                         networkfunction_id=n['networkfunction_id'],
                                         shared=n['shared'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(category_networkfunctions_delta)
        payload = self._make_category_networkfunctions_delta_dict(category_networkfunctions_delta)
        method = n['operation']+"_category_networkfunction"
        #rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg(method,payload=payload))
        return self._make_category_networkfunctions_delta_dict(category_networkfunctions_delta)
    
    def _get_category_networkfunctions_delta(self, context, id):
        try:
            category_networkfunctions_delta = self._get_by_id(context, sfc_category_networkfunctions_delta, id)
        except exc.NoResultFound:
            raise q_exc.category_networkfunctions_deltaNotFound(category_networkfunctions_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple category_networkfunctions_deltas match for %s' % id)
            raise q_exc.category_networkfunctions_deltaNotFound(category_networkfunctions_delta_id=id)
        return category_networkfunctions_delta
    
    
    
    ######################### Vendors Delta ###############################   
    def _make_vendors_delta_dict(self, vendors_delta, fields=None):
        res = {'id': vendors_delta['id'],
               'vendor_id': vendors_delta['vendor_id'],
               'name': vendors_delta['name'],
               'tenant_id': vendors_delta['tenant_id'],
               'description': vendors_delta['description'],
               'shared': vendors_delta['shared'],
               'operation': vendors_delta['operation'],
               'user_id': vendors_delta['user_id'],
               'logged_at': vendors_delta['logged_at'],
               'version_id': vendors_delta['version_id']}
        return self._fields(res, fields)
    
    def get_vendors_delta(self, context, id, fields=None):
        vendors_delta = self._get_vendors_delta(context, id)
        return self._make_vendors_delta_dict(vendors_delta, fields)
        
    def get_vendors_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_vendors_delta,
                                    self._make_vendors_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_vendors_delta(self, context, vendors_delta):
        n = vendors_delta['vendors_delta']
        
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            vendors_delta = sfc_vendors_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         vendor_id=n['id'],
                                         name=n['name'],
                                         description=n['description'],
                                         shared=n['shared'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(vendors_delta)
        payload = self._make_vendors_delta_dict(vendors_delta)
        method = n['operation']+"_vendor"
        #rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg(method,payload=payload))
        return self._make_vendors_delta_dict(vendors_delta)
    
    def _get_vendors_delta(self, context, id):
        try:
            vendors_delta = self._get_by_id(context, sfc_vendors_delta, id)
        except exc.NoResultFound:
            raise q_exc.vendors_deltaNotFound(vendors_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple vendors_deltas match for %s' % id)
            raise q_exc.vendors_deltaNotFound(vendors_delta_id=id)
        return vendors_delta
    
    
    ######################### Appliance Delta ###############################   
    def _make_appliances_delta_dict(self, appliances_delta, fields=None):
        res = {'id': appliances_delta['id'],
               'appliance_id': appliances_delta['appliance_id'],
               'name': appliances_delta['name'],
               'tenant_id': appliances_delta['tenant_id'],
               'category_id': appliances_delta['category_id'],
               'vendor_id': appliances_delta['vendor_id'],
               'image_id': appliances_delta['image_id'],
               'flavor_id': appliances_delta['flavor_id'],
               'security_group_id': appliances_delta['security_group_id'],
               'form_factor_type': appliances_delta['form_factor_type'],
               'type': appliances_delta['type'],
               'load_share_algorithm': appliances_delta['load_share_algorithm'],
               'high_threshold': appliances_delta['high_threshold'],
               'low_threshold': appliances_delta['low_threshold'],
               'pkt_field_to_hash': appliances_delta['pkt_field_to_hash'],
               'load_indication_type': appliances_delta['load_indication_type'],
               'config_handle_id': appliances_delta['config_handle_id'],
               'operation': appliances_delta['operation'],
               'user_id': appliances_delta['user_id'],
               'logged_at': appliances_delta['logged_at'],
               'version_id': appliances_delta['version_id']}
        return self._fields(res, fields)
    
    def get_appliances_delta(self, context, id, fields=None):
        appliances_delta = self._get_appliances_delta(context, id)
        return self._make_appliances_delta_dict(appliances_delta, fields)
        
    def get_appliances_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_appliances_delta,
                                    self._make_appliances_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_appliances_delta(self, context, appliances_delta):
        n = appliances_delta['appliances_delta']
        LOG.error('Delta %s' % str(n))
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            appliances_delta = sfc_appliances_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         appliance_id=n['id'],
                                         name=n['name'],
                                         category_id=n['category_id'],
                                         vendor_id=n['vendor_id'],
                                         flavor_id=n['flavor_id'],
                                         security_group_id=n['security_group_id'],
                                         form_factor_type=n['form_factor_type'],
                                         image_id=n['image_id'],
                                         type=n['type'],
                                         load_share_algorithm=n['load_share_algorithm'],
                                         high_threshold=n['high_threshold'],
                                         low_threshold=n['low_threshold'],
                                         pkt_field_to_hash=n['pkt_field_to_hash'],
                                         load_indication_type=n['load_indication_type'],
                                         config_handle_id=n['config_handle_id'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(appliances_delta)
        payload = self._make_appliances_delta_dict(appliances_delta)
        method = n['operation']+"_appliance"
        
        fanoutmsg = {}
        fanoutmsg.update({'method':method,'payload':payload})
        delta={}
        version = payload['version_id']
        delta[version] = fanoutmsg
        rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))
        
        return self._make_appliances_delta_dict(appliances_delta)
    
    def _get_appliances_delta(self, context, id):
        try:
            appliances_delta = self._get_by_id(context, sfc_appliances_delta, id)
        except exc.NoResultFound:
            raise q_exc.appliances_deltaNotFound(appliances_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple appliances_deltas match for %s' % id)
            raise q_exc.appliances_deltaNotFound(appliances_delta_id=id)
        return appliances_delta
    
    
    
    ######################### Chains Delta ###############################   
    def _make_chains_delta_dict(self, chains_delta, fields=None):
        res = {'id': chains_delta['id'],
               'chain_id': chains_delta['chain_id'],
               'name': chains_delta['name'],
               'tenant_id': chains_delta['tenant_id'],
               'auto_boot': chains_delta['auto_boot'],
               'operation': chains_delta['operation'],
               'user_id': chains_delta['user_id'],
               'logged_at': chains_delta['logged_at'],
               'version_id': chains_delta['version_id']}
        return self._fields(res, fields)
    
    def get_chains_delta(self, context, id, fields=None):
        chains_delta = self._get_chains_delta(context, id)
        return self._make_chains_delta_dict(chains_delta, fields)
        
    def get_chains_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_chains_delta,
                                    self._make_chains_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_chains_delta(self, context, chains_delta):
        n = chains_delta['chains_delta']
        LOG.error('Delta %s' % str(n))
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            chains_delta = sfc_chains_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         chain_id=n['id'],
                                         name=n['name'],
                                         auto_boot=n['auto_boot'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(chains_delta)
        payload = self._make_chains_delta_dict(chains_delta)
        method = n['operation']+"_chain"
        fanoutmsg = {}
        fanoutmsg.update({'method':method,'payload':payload})
        delta={}
        version = payload['version_id']
        delta[version] = fanoutmsg
        rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))
               
        return self._make_chains_delta_dict(chains_delta)
    
    def _get_chains_delta(self, context, id):
        try:
            chains_delta = self._get_by_id(context, sfc_chains_delta, id)
        except exc.NoResultFound:
            raise q_exc.chains_deltaNotFound(chains_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chains_deltas match for %s' % id)
            raise q_exc.chains_deltaNotFound(chains_delta_id=id)
        return chains_delta
    
    
    
    ######################### Chains Appliances Delta ###############################   
    def _make_chain_appliances_delta_dict(self, chain_appliances_delta, fields=None):
        res = {'id': chain_appliances_delta['id'],
               'chain_appliance_map_id' : chain_appliances_delta['chain_appliance_map_id'],
               'tenant_id': chain_appliances_delta['tenant_id'],
               'name': chain_appliances_delta['name'],
               'chain_id': chain_appliances_delta['chain_id'],
               'appliance_id': chain_appliances_delta['appliance_id'],
               'sequence_number': chain_appliances_delta['sequence_number'],
	       'operation': chain_appliances_delta['operation'],
               'user_id': chain_appliances_delta['user_id'],
               'logged_at': chain_appliances_delta['logged_at'],
               'version_id': chain_appliances_delta['version_id']}
        return self._fields(res, fields)
    
    def get_chain_appliances_delta(self, context, id, fields=None):
        chain_appliances_delta = self._get_chain_appliances_delta(context, id)
        return self._make_chain_appliances_delta_dict(chain_appliances_delta, fields)
        
    def get_chain_appliances_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_chain_appliances_delta,
                                    self._make_chain_appliances_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_chain_appliances_delta(self, context, chain_appliances_delta):
        n = chain_appliances_delta['chain_appliances_delta']
        LOG.error('Delta %s' % str(n))
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            chain_appliances_delta = sfc_chain_appliances_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         name=n['name'],
                                         chain_appliance_map_id=n['id'],
                                         chain_id=n['chain_id'],
                                         appliance_id=n['appliance_id'],
                                         sequence_number=n['sequence_number'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(chain_appliances_delta)
        payload = self._make_chain_appliances_delta_dict(chain_appliances_delta)
        method = n['operation']+"_chain_appliance"
        if n['operation'] != 'update':
            fanoutmsg = {}
            fanoutmsg.update({'method':method,'payload':payload})
            delta={}
            version = payload['version_id']
            delta[version] = fanoutmsg
            rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))
        return self._make_chain_appliances_delta_dict(chain_appliances_delta)
    
    def _get_chain_appliances_delta(self, context, id):
        try:
            chain_appliances_delta = self._get_by_id(context, sfc_chain_appliances_delta, id)
        except exc.NoResultFound:
            raise q_exc.chain_appliances_deltaNotFound(chain_appliances_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chain_appliances_deltas match for %s' % id)
            raise q_exc.chain_appliances_deltaNotFound(chain_appliances_delta_id=id)
        return chain_appliances_delta
    
    
    def _make_chain_bypass_rules_delta_dict(self, chain_bypass_rule, fields=None):
        res = {'id': chain_bypass_rule['id'],
               'chain_bypass_rule_id': chain_bypass_rule['chain_bypass_rule_id'],
               'name': chain_bypass_rule['name'],
               'tenant_id': chain_bypass_rule['tenant_id'],
               'chain_id' : chain_bypass_rule['chain_id'],
               'src_mac_type' : chain_bypass_rule['src_mac_type'],
               'dest_mac_type' : chain_bypass_rule['dest_mac_type'],
               'src_mac' : chain_bypass_rule['src_mac'],
               'dest_mac' : chain_bypass_rule['dest_mac'],
               'eth_type' : chain_bypass_rule['eth_type'],
               'eth_value' : chain_bypass_rule['eth_value'],
               'sip_type' : chain_bypass_rule['sip_type'],
               'dip_type' : chain_bypass_rule['dip_type'],
               'sip_start' : chain_bypass_rule['sip_start'],
               'sip_end' : chain_bypass_rule['sip_end'],
               'dip_start' :chain_bypass_rule['dip_start'],
               'dip_end' : chain_bypass_rule['dip_end'],
               'sp_type' : chain_bypass_rule['sp_type'],
               'dp_type' : chain_bypass_rule['dp_type'],
               'sp_start' : chain_bypass_rule['sp_start'],
               'sp_end' : chain_bypass_rule['sp_end'],
               'dp_start' : chain_bypass_rule['dp_start'],
               'dp_end' : chain_bypass_rule['dp_end'],
               'ip_protocol' : chain_bypass_rule['ip_protocol'],
               'nwservice_count' : chain_bypass_rule['nwservice_count'],
               'nwservice_names' : chain_bypass_rule['nwservice_names'],
               'operation': chain_bypass_rule['operation'],
               'user_id': chain_bypass_rule['user_id'],
               'logged_at': chain_bypass_rule['logged_at'],
               'version_id': chain_bypass_rule['version_id']}
        return self._fields(res, fields)
    
    def get_chain_bypass_rules_delta(self, context, id, fields=None):
        chain_bypass_rules_delta = self._get_chain_bypass_rules_delta(context, id)
        return self._make_chain_bypass_rules_delta_dict(chain_bypass_rules_delta, fields)
        
    def get_chain_bypass_rules_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_chain_bypass_rules_delta,
                                    self._make_chain_bypass_rules_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_chain_bypass_rules_delta(self, context, chain_bypass_rules_delta):
        cbr = chain_bypass_rules_delta['chain_bypass_rules_delta']
        
        tenant_id = self._get_tenant_id_for_create(context, cbr)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            chain_bypass_rules_delta = sfc_chain_bypass_rules_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         chain_bypass_rule_id= cbr['id'],
                                         name= cbr['name'],
                                         chain_id= cbr['chain_id'],
                                         src_mac_type = cbr['src_mac_type'], # any or single
                                         dest_mac_type = cbr['dest_mac_type'], # any or single
                                         src_mac = cbr['src_mac'], 
                                         dest_mac = cbr['dest_mac'],
                                         eth_type = cbr['eth_type'], # any or value
                                         eth_value = cbr['eth_value'], 
                                         sip_type = cbr['sip_type'], # any or single or range or subnet
                                         dip_type = cbr['dip_type'], # any or single or range or subnet
                                         sip_start = cbr['sip_start'],
                                         sip_end = cbr['sip_end'],
                                         dip_start =cbr['dip_start'],
                                         dip_end = cbr['dip_end'],
                                         sp_type = cbr['sp_type'],  # any or single or range
                                         dp_type = cbr['dp_type'],  # any or single or range
                                         sp_start = cbr['sp_start'],
                                         sp_end = cbr['sp_end'],
                                         dp_start = cbr['dp_start'],
                                         dp_end = cbr['dp_end'],
                                         ip_protocol = cbr['ip_protocol'], # TCP, UDP
                                         nwservice_count = cbr['nwservice_count'], 
                                         nwservice_names = cbr['nwservice_names'],
                                         operation = cbr['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(chain_bypass_rules_delta)
        payload = self._make_chain_bypass_rules_delta_dict(chain_bypass_rules_delta)
        method = cbr['operation']+"_chain_bypass_rules"
        fanoutmsg = {}
        fanoutmsg.update({'method':method,'payload':payload})
        delta={}
        version = payload['version_id']
        delta[version] = fanoutmsg
        rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))    
        return self._make_chain_bypass_rules_delta_dict(chain_bypass_rules_delta)
    
    def _get_chain_bypass_rules_delta(self, context, id):
        try:
            chain_bypass_rules_delta = self._get_by_id(context, sfc_chain_bypass_rules_delta, id)
        except exc.NoResultFound:
            raise q_exc.chain_bypass_rules_deltaNotFound(chain_bypass_rules_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chain_bypass_rules_deltas match for %s' % id)
            raise q_exc.chain_bypass_rules_deltaMultipleFound(chain_bypass_rules_delta_id=id)
        return chain_bypass_rules_delta
    
    
    def _make_chainsets_delta_dict(self, chainsets_delta, fields=None):
        res = {'id': chainsets_delta['id'],
               'chainset_id': chainsets_delta['chainset_id'],
               'name': chainsets_delta['name'],
               'zonefull': chainsets_delta['zonefull'],
               'direction': chainsets_delta['direction'],
               'tenant_id': chainsets_delta['tenant_id'],
               'operation': chainsets_delta['operation'],
               'user_id': chainsets_delta['user_id'],
               'logged_at': chainsets_delta['logged_at'],
               'version_id': chainsets_delta['version_id']}
        return self._fields(res, fields)
    
    def get_chainsets_delta(self, context, id, fields=None):
        chainsets_delta = self._get_chainsets_delta(context, id)
        return self._make_chainsets_delta_dict(chainsets_delta, fields)
        
    def get_chainsets_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_chainsets_delta,
                                    self._make_chainsets_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_chainsets_delta(self, context, chainsets_delta):
        cbr = chainsets_delta['chainsets_delta']
        
        tenant_id = self._get_tenant_id_for_create(context, cbr)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            chainsets_delta = sfc_chainsets_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         chainset_id= cbr['id'],
                                         name= cbr['name'],
                                         zonefull = cbr['zonefull'],
                                         direction = cbr['direction'],
                                         operation = cbr['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(chainsets_delta)
        payload = self._make_chainsets_delta_dict(chainsets_delta)
        method = cbr['operation']+"_chainsets"
        fanoutmsg = {}
        fanoutmsg.update({'method':method,'payload':payload})
        delta={}
        version = payload['version_id']
        delta[version] = fanoutmsg
        rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))
        return self._make_chainsets_delta_dict(chainsets_delta)
    
    def _get_chainsets_delta(self, context, id):
        try:
            chainsets_delta = self._get_by_id(context, sfc_chainsets_delta, id)
        except exc.NoResultFound:
            raise q_exc.chainsets_deltaNotFound(chainsets_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chainsets_deltas match for %s' % id)
            raise q_exc.chainsets_deltaMultipleFound(chainsets_delta_id=id)
        return chainsets_delta
        
    def _make_chainrules_delta_dict(self, chainrules_delta, fields=None):
        res = {'id': chainrules_delta['id'],
               'chain_rule_id': chainrules_delta['chain_rule_id'],
               'name': chainrules_delta['name'],
               'tenant_id': chainrules_delta['tenant_id'],
               'chainset_id': chainrules_delta['chainset_id'],
               'chain_id': chainrules_delta['chain_id'],
               'operation': chainrules_delta['operation'],
               'src_mac_type' : chainrules_delta['src_mac_type'],
               'dest_mac_type' : chainrules_delta['dest_mac_type'],
               'src_mac' : chainrules_delta['src_mac'],
               'dest_mac' : chainrules_delta['dest_mac'],
               'eth_type' : chainrules_delta['eth_type'],
               'eth_value' : chainrules_delta['eth_value'],
               'sip_type' : chainrules_delta['sip_type'],
               'dip_type' : chainrules_delta['dip_type'],
               'sip_start' : chainrules_delta['sip_start'],
               'sip_end' : chainrules_delta['sip_end'],
               'dip_start' :chainrules_delta['dip_start'],
               'dip_end' : chainrules_delta['dip_end'],
               'sp_type' : chainrules_delta['sp_type'],
               'dp_type' : chainrules_delta['dp_type'],
               'sp_start' : chainrules_delta['sp_start'],
               'sp_end' : chainrules_delta['sp_end'],
               'dp_start' : chainrules_delta['dp_start'],
               'dp_end' : chainrules_delta['dp_end'],
               'ip_protocol' : chainrules_delta['ip_protocol'],
               'user_id': chainrules_delta['user_id'],
               'logged_at': chainrules_delta['logged_at'],
               'version_id': chainrules_delta['version_id']}
        return self._fields(res, fields)
    
    def get_chainrules_delta(self, context, id, fields=None):
        chainrules_delta = self._get_chainrules_delta(context, id)
        return self._make_chainrules_delta_dict(chainrules_delta, fields)
        
    def get_chainrules_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_chainrules_delta,
                                    self._make_chainrules_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_chainrules_delta(self, context, chainrules_delta):
        n = chainrules_delta['chainrules_delta']
        LOG.error('Delta %s' % str(n))
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            chainrules_delta = sfc_chainrules_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         chain_rule_id = n['id'],
                                         name=n['name'],
                                         src_mac_type = n['src_mac_type'],
                                         dest_mac_type = n['dest_mac_type'],
                                         src_mac = n['src_mac'],
                                         dest_mac = n['dest_mac'],
                                         eth_type = n['eth_type'],
                                         eth_value = n['eth_value'],
                                         sip_type = n['sip_type'],
                                         dip_type = n['dip_type'],
                                         sip_start = n['sip_start'],
                                         sip_end = n['sip_end'],
                                         dip_start = n['dip_start'],
                                         dip_end = n['dip_end'],
                                         sp_type = n['sp_type'],
                                         dp_type = n['dp_type'],
                                         sp_start = n['sp_start'],
                                         sp_end = n['sp_end'],
                                         dp_start = n['dp_start'],
                                         dp_end = n['dp_end'],
                                         ip_protocol = n['ip_protocol'],
                                         chainset_id=n['chainset_id'],
                                         chain_id=n['chain_id'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(chainrules_delta)
        payload = self._make_chainrules_delta_dict(chainrules_delta)
        method = n['operation']+"_chainrule"
        fanoutmsg = {}
        fanoutmsg.update({'method':method,'payload':payload})
        delta={}
        version = payload['version_id']
        delta[version] = fanoutmsg
        rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))
        return self._make_chainrules_delta_dict(chainrules_delta)
    
    def _get_chainrules_delta(self, context, id):
        try:
            chainrules_delta = self._get_by_id(context, sfc_chainrules_delta, id)
        except exc.NoResultFound:
            raise q_exc.chainrules_deltaNotFound(chainrules_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chainrules_deltas match for %s' % id)
            raise q_exc.chainrules_deltaNotFound(chainrules_delta_id=id)
        return chainrules_delta
    
    
    
    ######################### Chainmaps Delta ###############################   
    def _make_chainmaps_delta_dict(self, chainmaps_delta, fields=None):
        res = {'id': chainmaps_delta['id'],
               'chain_map_id': chainmaps_delta['chain_map_id'],
               'name': chainmaps_delta['name'],
               'tenant_id': chainmaps_delta['tenant_id'],
               'type': chainmaps_delta['type'],
               'inbound_network_id': chainmaps_delta['inbound_network_id'],
               'outbound_network_id': chainmaps_delta['outbound_network_id'],
               'chainset_id': chainmaps_delta['chainset_id'],
               'operation': chainmaps_delta['operation'],
               'user_id': chainmaps_delta['user_id'],
               'logged_at': chainmaps_delta['logged_at'],
               'version_id': chainmaps_delta['version_id']}
        return self._fields(res, fields)
    
    def get_chainmaps_delta(self, context, id, fields=None):
        chainmaps_delta = self._get_chainmaps_delta(context, id)
        return self._make_chainmaps_delta_dict(chainmaps_delta, fields)
        
    def get_chainmaps_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_chainmaps_delta,
                                    self._make_chainmaps_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_chainmaps_delta(self, context, chainmaps_delta):
        n = chainmaps_delta['chainmaps_delta']
        LOG.error('Delta %s' % str(n))
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            chainmaps_delta = sfc_chainmaps_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         chain_map_id = n['id'],
                                         name=n['name'],
                                         type='L2-Mode',
                                         inbound_network_id=n['inbound_network_id'],
                                         outbound_network_id=n['inbound_network_id'],
                                         chainset_id=n['chainset_id'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(chainmaps_delta)
        payload = self._make_chainmaps_delta_dict(chainmaps_delta)
        method = n['operation']+"_chainmap"
        fanoutmsg = {}
        fanoutmsg.update({'method':method,'payload':payload})
        delta={}
        version = payload['version_id']
        delta[version] = fanoutmsg
        rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))
        return self._make_chainmaps_delta_dict(chainmaps_delta)
    
    def _get_chainmaps_delta(self, context, id):
        try:
            chainmaps_delta = self._get_by_id(context, sfc_chainmaps_delta, id)
        except exc.NoResultFound:
            raise q_exc.chainmaps_deltaNotFound(chainmaps_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chainmaps_deltas match for %s' % id)
            raise q_exc.chainmaps_deltaNotFound(chainmaps_delta_id=id)
        return chainmaps_delta
    
    ######################### Appliance Instances Delta ###############################   
    def _make_appliance_instances_delta_dict(self, appliance_instances_delta, fields=None):
        res = {'id': appliance_instances_delta['id'],
               'appliance_instance_id': appliance_instances_delta['appliance_instance_id'],
               'instance_uuid': appliance_instances_delta['instance_uuid'],
               'appliance_map_id': appliance_instances_delta['appliance_map_id'],
               'network_id': appliance_instances_delta['network_id'],
               'vlan_in': appliance_instances_delta['vlan_in'],
               'vlan_out': appliance_instances_delta['vlan_out'],
               'tenant_id': appliance_instances_delta['tenant_id'],
               'operation': appliance_instances_delta['operation'],
               'user_id': appliance_instances_delta['user_id'],
               'logged_at': appliance_instances_delta['logged_at'],
               'version_id': appliance_instances_delta['version_id']}
        return self._fields(res, fields)
    
    def get_appliance_instances_delta(self, context, id, fields=None):
        appliance_instances_delta = self._get_appliance_instances_delta(context, id)
        return self._make_appliance_instances_delta_dict(appliance_instances_delta, fields)
        
    def get_appliance_instances_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_appliance_instances_delta,
                                    self._make_appliance_instances_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_appliance_instances_delta(self, context, appliance_instances_delta):
        n = appliance_instances_delta['appliance_instances_delta']
        LOG.error('Delta %s' % str(n))
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            appliance_instances_delta = sfc_appliance_instances_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         appliance_instance_id = n['id'],
                                         appliance_map_id=n['appliance_map_id'],
                                         instance_uuid=n['instance_uuid'],
                                         network_id=n['network_id'],
                                         vlan_in=n['vlan_in'],
                                         vlan_out=n['vlan_out'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(appliance_instances_delta)
        payload = self._make_appliance_instances_delta_dict(appliance_instances_delta)
        method = n['operation']+"_appliance_instance"
        fanoutmsg = {}
        fanoutmsg.update({'method':method,'payload':payload})
        delta={}
        version = payload['version_id']
        delta[version] = fanoutmsg
        rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))
        return self._make_appliance_instances_delta_dict(appliance_instances_delta)
    
    def _get_appliance_instances_delta(self, context, id):
        try:
            appliance_instances_delta = self._get_by_id(context, sfc_appliance_instances_delta, id)
        except exc.NoResultFound:
            raise q_exc.appliance_instances_deltaNotFound(appliance_instances_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple appliance_instances_deltas match for %s' % id)
            raise q_exc.appliance_instances_deltaNotFound(appliance_instances_delta_id=id)
        return appliance_instances_delta
    
    #####Chainset SFC Zones delta####################################
    def _make_chainset_zones_delta_dict(self, chainset_zones_delta, fields=None):
        res = {'id': chainset_zones_delta['id'],
               'zone_id': chainset_zones_delta['zone_id'],
               'zone': chainset_zones_delta['zone'],
               'direction': chainset_zones_delta['direction'],
               'tenant_id': chainset_zones_delta['tenant_id'],
               'chainset_id': chainset_zones_delta['chainset_id'],
               'operation': chainset_zones_delta['operation'],
               'user_id': chainset_zones_delta['user_id'],
               'logged_at': chainset_zones_delta['logged_at'],
               'version_id': chainset_zones_delta['version_id']}
        return self._fields(res, fields)
    
    def get_chainset_zones_delta(self, context, id, fields=None):
        chainset_zones_delta = self._get_chainset_zones_delta(context, id)
        return self._make_chainset_zones_delta_dict(chainset_zones_delta, fields)
        
    def get_chainset_zones_deltas(self, context, filters=None, fields=None):
        return self._get_collection(context, sfc_chainset_zone_delta,
                                    self._make_chainset_zones_delta_dict,
                                    filters=filters, fields=fields)
    
    def create_chainset_zone_deltas(self, context, chainset_zones_delta):
        n = chainset_zones_delta['chainset_zones_delta']
        LOG.error('Delta %s' % str(n))
        tenant_id = self._get_tenant_id_for_create(context, n)
        user_id = context.user_id
                
        with context.session.begin(subtransactions=True):
            version_id = self.create_version(context, tenant_id)
            chainset_zones_delta = sfc_chainset_zone_delta(tenant_id=tenant_id,
                                         id=uuidutils.generate_uuid(),
                                         zone_id = n['id'],
                                         zone=n['zone'],
                                         direction=n['direction'],
                                         chainset_id=n['chainset_id'],
                                         operation = n['operation'],
                                         user_id=user_id,
                                         logged_at=datetime.datetime.now(),
                                         version_id=version_id)
            context.session.add(chainset_zones_delta)
        payload = self._make_chainset_zones_delta_dict(chainset_zones_delta)
        method = n['operation']+"_chainset_zone"
        fanoutmsg = {}
        fanoutmsg.update({'method':method,'payload':payload})
        delta={}
        version = payload['version_id']
        delta[version] = fanoutmsg
        rpc.fanout_cast(context,'crd-consumer', rpc_proxy.make_msg('call_consumer',payload=delta))
        return self._make_chainset_zones_delta_dict(chainset_zones_delta)
    
    def _get_chainset_zones_delta(self, context, id):
        try:
            chainset_zones_delta = self._get_by_id(context, sfc_chainset_zone_delta, id)
        except exc.NoResultFound:
            raise sfc_exc.chainset_zones_deltaNotFound(chainset_zones_delta_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chainset_zones_deltas match for %s' % id)
            raise sfc_exc.chainset_zones_deltaNotFound(chainset_zones_delta_id=id)
        return chainset_zones_delta