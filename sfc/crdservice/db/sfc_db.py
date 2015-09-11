# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
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
from sqlalchemy.orm import exc, relationship

# CRD Service based imports
from nscs.crdservice.db import model_base, db_base_plugin_v2
from nscs.crdservice.common import exceptions as q_exc
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import uuidutils

LOG = logging.getLogger(__name__)


############    
# Service Function Chaining Tables
############
class SFCNetworkFunction(model_base.BASEV2, model_base.HasId,
                         model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_networkfunctions'
    name = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)



class SFCCategoryNetworkFunction(model_base.BASEV2, model_base.HasId,
                                 model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_category_networkfunctions'
    category_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_categories.id'),
                            nullable=False)
    networkfunction_id = sa.Column(sa.String(36),
                                   sa.ForeignKey('sfc_networkfunctions.id'),
                                   nullable=False)
    shared = sa.Column(sa.Boolean)
    networkfunctions = relationship(SFCNetworkFunction)


class SFCCategory(model_base.BASEV2, model_base.HasId, model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_categories'
    name = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)
    category_networkfunctions = relationship(SFCCategoryNetworkFunction,
                                             backref="sfc_categories")


class SFCVendor(model_base.BASEV2, model_base.HasId, model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_vendors'
    name = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)


class SFCAppliance(model_base.BASEV2, model_base.HasId, model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_appliances'
    name = sa.Column(sa.String(50), nullable=False)
    category_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_categories.id'),
                            nullable=False)
    vendor_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_vendors.id'),
                          nullable=False)
    image_id = sa.Column(sa.String(36), nullable=False)
    flavor_id = sa.Column(sa.String(36), nullable=False)
    security_group_id = sa.Column(sa.String(36), nullable=False)
    form_factor_type = sa.Column(sa.String(36), nullable=False)
    type = sa.Column(sa.String(36), nullable=False)
    load_share_algorithm = sa.Column(sa.String(50), nullable=False)
    high_threshold = sa.Column(sa.String(50), nullable=False)
    low_threshold = sa.Column(sa.String(50), nullable=False)
    pkt_field_to_hash = sa.Column(sa.String(255), nullable=False)
    load_indication_type = sa.Column(sa.String(50), nullable=False)
    appliance_categories = orm.relationship(SFCCategory,
                                            backref='sfc_appliances')
    appliance_vendors = orm.relationship(SFCVendor,
                                         backref='sfc_appliances')
    config_handle_id = sa.Column(sa.String(36), sa.ForeignKey('crd_config_handles.id'), nullable=False)


class SFCChain(model_base.BASEV2, model_base.HasId, model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_chains'
    name = sa.Column(sa.String(50), nullable=False)
    auto_boot = sa.Column(sa.Boolean)


class SFCChainBypassRule(model_base.BASEV2, model_base.HasId,
                         model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_chain_bypass_rules'
    name = sa.Column(sa.String(50), nullable=False)
    chain_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_chains.id'),
                         nullable=False)
    src_mac_type = sa.Column(sa.String(50))
    dest_mac_type = sa.Column(sa.String(50))
    src_mac = sa.Column(sa.String(50))
    dest_mac = sa.Column(sa.String(50))
    eth_type = sa.Column(sa.String(50))
    eth_value = sa.Column(sa.String(50))
    sip_type = sa.Column(sa.String(50))
    dip_type = sa.Column(sa.String(50))
    sip_start = sa.Column(sa.String(50))
    sip_end = sa.Column(sa.String(50))
    dip_start = sa.Column(sa.String(50))
    dip_end = sa.Column(sa.String(50))
    sp_type = sa.Column(sa.String(50))
    dp_type = sa.Column(sa.String(50))
    sp_start = sa.Column(sa.String(50))
    sp_end = sa.Column(sa.String(50))
    dp_start = sa.Column(sa.String(50))
    dp_end = sa.Column(sa.String(50))
    ip_protocol = sa.Column(sa.String(50))
    nwservice_count = sa.Column(sa.String(50))
    nwservice_names = sa.Column(sa.Text())


class SFCChainSet(model_base.BASEV2, model_base.HasId, model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_chainsets'
    name = sa.Column(sa.String(50), nullable=False)
    zonefull = sa.Column(sa.Boolean)
    direction = sa.Column(sa.String(50))


class SFCChainSelectionRule(model_base.BASEV2, model_base.HasId,
                            model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_chain_selection_rules'
    name = sa.Column(sa.String(50), nullable=False)
    chainset_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_chainsets.id'),
                            nullable=False)
    chain_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_chains.id'),
                         nullable=False)
    src_mac_type = sa.Column(sa.String(50))
    dest_mac_type = sa.Column(sa.String(50))
    src_mac = sa.Column(sa.String(50))
    dest_mac = sa.Column(sa.String(50))
    eth_type = sa.Column(sa.String(50))
    eth_value = sa.Column(sa.String(50))
    sip_type = sa.Column(sa.String(50))
    dip_type = sa.Column(sa.String(50))
    sip_start = sa.Column(sa.String(50))
    sip_end = sa.Column(sa.String(50))
    dip_start = sa.Column(sa.String(50))
    dip_end = sa.Column(sa.String(50))
    sp_type = sa.Column(sa.String(50))
    dp_type = sa.Column(sa.String(50))
    sp_start = sa.Column(sa.String(50))
    sp_end = sa.Column(sa.String(50))
    dp_start = sa.Column(sa.String(50))
    dp_end = sa.Column(sa.String(50))
    ip_protocol = sa.Column(sa.String(50))


class SFCChainsetNetworkMap(model_base.BASEV2, model_base.HasId,
                            model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_chainset_network_maps'

    name = sa.Column(sa.String(50), nullable=False)
    inbound_network_id = sa.Column(sa.String(36), nullable=False)
    outbound_network_id = sa.Column(sa.String(36), nullable=False)
    chainset_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_chainsets.id'),
                            nullable=False)


class SFCChainAppliance(model_base.BASEV2, model_base.HasId,
                        model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = "sfc_chain_appliances"
    name = sa.Column(sa.String(50), nullable=False)
    chain_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_chains.id',
                                                      ondelete='CASCADE'),
                         nullable=False)
    appliance_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_appliances.id'),
                             nullable=False)
    sequence_number = sa.Column(sa.Integer)
    chain_appliance = orm.relationship(SFCAppliance,
                                       backref='sfc_chain_appliances')


class SFCInternalSubnet(model_base.BASEV2, model_base.HasId):
    __tablename__ = "sfc_internal_subnets"
    subnet_cidr = sa.Column(sa.String(50),
                            nullable=False)


class SFCVLANQuota(model_base.BASEV2, model_base.HasId, model_base.HasTenant):
    __tablename__ = "sfc_vlanquotas"
    vlan_start = sa.Column(sa.Integer, nullable=False)
    vlan_end = sa.Column(sa.Integer, nullable=False)

#
#class SFCVLANPair(model_base.BASEV2, model_base.HasId, model_base.HasTenant):
#    __tablename__ = "sfc_vlan_pairs"
#    instance_id = sa.Column(sa.String(36))
#    network_id = sa.Column(sa.String(36))
#    vlan_in = sa.Column(sa.Integer)
#    vlan_out = sa.Column(sa.Integer)
#    chain_id = sa.Column(sa.String(36))
#    appliance_map_id = sa.Column(sa.String(36))

class SFCApplianceInstance(model_base.BASEV2, model_base.HasId,
                        model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = "sfc_appliance_instances"
    appliance_map_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_chain_appliances.id',
                                                                ondelete='CASCADE'),
                                   nullable=False)
    instance_uuid = sa.Column(sa.String(36))
    network_id = sa.Column(sa.String(36))
    vlan_in = sa.Column(sa.Integer)
    vlan_out = sa.Column(sa.Integer)
    chain_appliance = orm.relationship(SFCChainAppliance,
                                       backref='sfc_appliance_instances')
    
    
class SFCChainsetZone(model_base.BASEV2, model_base.HasId,
                            model_base.HasTenant):
    """Represents a v2 crd FSL service."""
    __tablename__ = 'sfc_chainset_zones'
    chainset_id = sa.Column(sa.String(36), sa.ForeignKey('sfc_chainsets.id', ondelete="CASCADE"),
                            nullable=False)
    zone = sa.Column(sa.String(50))
    direction = sa.Column(sa.String(50))

class SFCPluginDb(db_base_plugin_v2.CrdDbPluginV2):
    """
    A class that wraps the implementation of the Crd
    nwservices plugin database access interface using SQLAlchemy models.

    As opposed to all other DB plugins NwServicePluginDb does not
    implement plugin interface. nwservicesPlugin follows "has-a" instead of
    "is-a" relation with db-plugin. The main reason is that Db plugin is
    called not only by plugin, but also by notify handler and direct calls
    are a logical way.
    """

    @staticmethod
    def __get_id(obj):
        return obj.get('id') or uuidutils.generate_uuid()

    def _make_networkfunction_dict(self, networkfunction, fields=None):
        res = {'id': networkfunction['id'],
               'name': networkfunction['name'],
               'tenant_id': networkfunction['tenant_id'],
               'description': networkfunction['description'],
               'shared': networkfunction['shared']}
        return self._fields(res, fields)

    def get_networkfunction(self, context, id, fields=None):
        networkfunction = self._get_networkfunction(context, id)
        return self._make_networkfunction_dict(networkfunction, fields)

    def get_networkfunctions(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCNetworkFunction,
                                    self._make_networkfunction_dict,
                                    filters=filters, fields=fields)

    def create_networkfunction(self, context, networkfunction):
        n = networkfunction['networkfunction']
        tenant_id = self._get_tenant_id_for_create(context, n)

        with context.session.begin(subtransactions=True):
            networkfunction = SFCNetworkFunction(tenant_id=tenant_id,
                                                 id=self.__get_id(n),
                                                 name=n['name'],
                                                 description=n['description'],
                                                 shared=n['shared'])
            context.session.add(networkfunction)
        return self._make_networkfunction_dict(networkfunction)

    def _get_networkfunction(self, context, id):
        try:
            networkfunction = self._get_by_id(context, SFCNetworkFunction, id)
        except exc.NoResultFound:
            raise q_exc.NetworkfunctionNotFound(networkfunction_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Networkfunctions match for %s' % id)
            raise q_exc.NetworkfunctionNotFound(networkfunction_id=id)
        return networkfunction

    def delete_networkfunction(self, context, id):
        networkfunction = self._get_networkfunction(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(networkfunction)

    def update_networkfunction(self, context, id, networkfunction):
        n = networkfunction['networkfunction']
        with context.session.begin(subtransactions=True):
            networkfunction = self._get_networkfunction(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, networkfunction, n)
            networkfunction.update(n)
        return self._make_networkfunction_dict(networkfunction)


    def _make_category_dict(self, category, fields=None):
        res = {'id': category['id'],
               'name': category['name'],
               'tenant_id': category['tenant_id'],
               'description': category['description'],
               'shared': category['shared'],
               'category_networkfunctions': []}
        for cat_nf in category['category_networkfunctions']:
            nf_res = {
                'id': cat_nf['networkfunctions'].id,
                'name': cat_nf['networkfunctions'].name,
            }
            res['category_networkfunctions'].append(nf_res)
        return self._fields(res, fields)

    def get_category(self, context, id, fields=None):
        category = self._get_category(context, id)
        return self._make_category_dict(category, fields)

    def get_categories(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCCategory,
                                    self._make_category_dict,
                                    filters=filters, fields=fields)

    def create_category(self, context, category):
        n = category['category']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            category = SFCCategory(id=self.__get_id(n),
                                   tenant_id=tenant_id,
                                   name=n['name'],
                                   description=n['description'],
                                   shared=n['shared'])
            context.session.add(category)
            network_functions = n['category_networkfunctions']
            for nf in network_functions:
                category_networkfunction = {'nf_map': {
                    'networkfunction_id': nf}}
                self.create_category_networkfunction(context,
                                                     category_networkfunction,
                                                     category.id)

        return self._make_category_dict(category)

    def _get_category(self, context, id):
        try:
            category = self._get_by_id(context, SFCCategory, id)
        except exc.NoResultFound:
            raise q_exc.CategoryNotFound(category_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Categories match for %s' % id)
            raise q_exc.CategoryNotFound(category_id=id)
        return category

    def delete_category(self, context, id):
        category = self._get_category(context, id)
        cat_data = self._make_category_dict(category)
        network_functions = cat_data['category_networkfunctions']
        with context.session.begin(subtransactions=True):
            for nf in network_functions:
                nf_id = nf['id']
                self.delete_category_networkfunction(context, category.id,
                                                     nf_id)
            context.session.delete(category)

    def update_category(self, context, id, category):
        n = category['category']
        with context.session.begin(subtransactions=True):
            category = self._get_category(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, category, n)
            category.update(n)
        return self._make_category_dict(category)

    def _make_category_networkfunction_dict(self, category_networkfunction,
                                            fields=None):
        res = {'id': category_networkfunction['id'],
               'category_id': category_networkfunction['category_id'],
               'networkfunction_id': category_networkfunction[
                   'networkfunction_id'],
               'tenant_id': category_networkfunction['tenant_id'],
               'shared': category_networkfunction['shared']}
        return self._fields(res, fields)

    def get_category_networkfunction(self, context, category_id,
                                     networkfunction_id, fields=None):
        cat_nf = self._get_category_networkfunction(context,
                                                    category_id,
                                                    networkfunction_id)
        return self._make_category_networkfunction_dict(cat_nf, fields)

    def create_category_networkfunction(self, context,
                                        category_networkfunction, category_id):
        n = category_networkfunction['nf_map']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            category_networkfunction = SFCCategoryNetworkFunction(
                id=self.__get_id(n),
                category_id=category_id,
                networkfunction_id=n['networkfunction_id'],
                tenant_id=tenant_id,
                shared=False)
            context.session.add(category_networkfunction)
        return self._make_category_networkfunction_dict(
            category_networkfunction)

    @staticmethod
    def _get_category_networkfunction(context, category_id, nf_id):
        try:
            query = context.session.query(SFCCategoryNetworkFunction)
            category_networkfunction = query.filter(
                SFCCategoryNetworkFunction.category_id == category_id,
                SFCCategoryNetworkFunction.networkfunction_id == nf_id).one()
        except exc.NoResultFound:
            raise q_exc.Category_networkfunctionNotFound(
                category_id=category_id, networkfunction_id=nf_id)
        except exc.MultipleResultsFound:
            LOG.error(
                'Multiple Category_networkfunctions match for '
                'Category %s and Network Function %s' % (
                    category_id, nf_id))
            raise q_exc.Category_networkfunctionNotFound(
                category_id=category_id, networkfunction_id=nf_id)
        return category_networkfunction

    def delete_category_networkfunction(self, context, category_id,
                                        networkfunction_id):
        cat_nf = self._get_category_networkfunction(context,
                                                    category_id,
                                                    networkfunction_id)
        with context.session.begin(subtransactions=True):
            context.session.delete(cat_nf)

    def _make_vendor_dict(self, vendor, fields=None):
        res = {'id': vendor['id'],
               'name': vendor['name'],
               'tenant_id': vendor['tenant_id'],
               'description': vendor['description'],
               'shared': vendor['shared']}
        return self._fields(res, fields)

    def get_vendor(self, context, id, fields=None):
        vendor = self._get_vendor(context, id)
        return self._make_vendor_dict(vendor, fields)

    def get_vendors(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCVendor,
                                    self._make_vendor_dict,
                                    filters=filters, fields=fields)

    def create_vendor(self, context, vendor):
        n = vendor['vendor']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            vendor = SFCVendor(tenant_id=tenant_id,
                               id=self.__get_id(n),
                               name=n['name'],
                               description=n['description'],
                               shared=n['shared'])
            context.session.add(vendor)
        return self._make_vendor_dict(vendor)

    def _get_vendor(self, context, id):
        try:
            vendor = self._get_by_id(context, SFCVendor, id)
        except exc.NoResultFound:
            raise q_exc.VendorNotFound(vendor_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Vendors match for %s' % id)
            raise q_exc.VendorNotFound(vendor_id=id)
        return vendor

    def delete_vendor(self, context, id):
        vendor = self._get_vendor(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(vendor)

    def update_vendor(self, context, id, vendor):
        n = vendor['vendor']
        with context.session.begin(subtransactions=True):
            vendor = self._get_vendor(context, id)
            if 'shared' in n:
                self._validate_shared_update(context, id, vendor, n)
            vendor.update(n)
        return self._make_vendor_dict(vendor)

    def _make_appliance_dict(self, appliance, fields=None):
        vendor_name = ''
        cat_name = ''
        for ven in appliance['appliance_vendors']:
            if str(ven[0]) == 'name':
                vendor_name = str(ven[1])
        for cat in appliance['appliance_categories']:
            if str(cat[0]) == 'name':
                cat_name = str(cat[1])
        res = {'id': appliance['id'],
               'name': appliance['name'],
               'tenant_id': appliance['tenant_id'],
               'category_id': appliance['category_id'],
               'vendor_id': appliance['vendor_id'],
               'image_id': appliance['image_id'],
               'flavor_id': appliance['flavor_id'],
               'security_group_id': appliance['security_group_id'],
               'form_factor_type': appliance['form_factor_type'],
               'type': appliance['type'],
               'load_share_algorithm': appliance['load_share_algorithm'],
               'high_threshold': appliance['high_threshold'],
               'low_threshold': appliance['low_threshold'],
               'pkt_field_to_hash': appliance['pkt_field_to_hash'],
               'load_indication_type': appliance['load_indication_type'],
               'config_handle_id': appliance['config_handle_id'],
               'appliance_categories': cat_name,
               'appliance_vendors': vendor_name}
        return self._fields(res, fields)

    def get_appliance(self, context, id, fields=None):
        appliance = self._get_appliance(context, id)
        return self._make_appliance_dict(appliance, fields)

    def get_appliances(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCAppliance,
                                    self._make_appliance_dict,
                                    filters=filters, fields=fields)

    def create_appliance(self, context, appliance):
        n = appliance['appliance']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            appl = SFCAppliance(tenant_id=tenant_id,
                                id=self.__get_id(n),
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
                                config_handle_id=n['config_handle_id'])
            context.session.add(appl)
        return self._make_appliance_dict(appl)

    def _get_appliance(self, context, id):
        try:
            appliance = self._get_by_id(context, SFCAppliance, id)
        except exc.NoResultFound:
            raise q_exc.ImageNotFound(appliance_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Images match for %s' % id)
            raise q_exc.ImageNotFound(appliance_id=id)
        return appliance

    def delete_appliance(self, context, id):
        appliance = self._get_appliance(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(appliance)

    def update_appliance(self, context, id, appliance):
        n = appliance['appliance']
        with context.session.begin(subtransactions=True):
            appliance = self._get_appliance(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, appliance, n)
            appliance.update(n)
        return self._make_appliance_dict(appliance)

    def _make_chain_dict(self, chain, fields=None):
        res = {'id': chain['id'],
               'name': chain['name'],
               'tenant_id': chain['tenant_id'],
               'auto_boot': chain['auto_boot']}

        return self._fields(res, fields)

    def get_chains(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCChain,
                                    self._make_chain_dict,
                                    filters=filters, fields=fields)

    def get_chain(self, context, id, fields=None):
        chain = self._get_chain(context, id)
        return self._make_chain_dict(chain, fields)

    def create_chain(self, context, chain):
        n = chain['chain']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            chain = SFCChain(tenant_id=tenant_id,
                             id=self.__get_id(n),
                             name=n['name'],
                             auto_boot=n['auto_boot'])
            context.session.add(chain)
        return self._make_chain_dict(chain)

    def _get_chain(self, context, id):
        try:
            chain = self._get_by_id(context, SFCChain, id)
        except exc.NoResultFound:
            raise q_exc.ChainNotFound(chain_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Chains match for %s' % id)
            raise q_exc.ChainNotFound(chain_id=id)
        return chain

    def delete_chain(self, context, id):
        chain = self._get_chain(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chain)

    def update_chain(self, context, id, chain):
        n = chain['chain']
        with context.session.begin(subtransactions=True):
            chain = self._get_chain(context, id)
            chain.update(n)
        return self._make_chain_dict(chain)

    ### Chain related
    def _make_appliance_map_dict(self, appliance_map, fields=None):
        img_name = ''
        for img in appliance_map['chain_appliance']:
            if str(img[0]) == 'name':
                img_name = str(img[1])

        res = {'id': appliance_map['id'],
               'name': appliance_map['name'],
               'chain_id': appliance_map['chain_id'],
               'appliance_id': appliance_map['appliance_id'],
               'sequence_number': appliance_map['sequence_number'],
               'chain_appliance': img_name,
               'tenant_id': appliance_map['tenant_id']}

        return self._fields(res, fields)

    def get_chain_appliance_map(self, context, id, chain_id=None, fields=None):
        appliance_map = self._get_appliance_map(context, id)
        return self._make_appliance_map_dict(appliance_map, fields)

    def get_chain_appliance_maps(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCChainAppliance,
                                    self._make_appliance_map_dict,
                                    filters=filters, fields=fields)

    def create_chain_appliance_map(self, context, appliance_map, chain_id):
        n = appliance_map['appliance']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            app_map = SFCChainAppliance(id=self.__get_id(n),
                                        name=n['name'],
                                        chain_id=chain_id,
                                        appliance_id=n['appliance_id'],
                                        sequence_number=n['sequence_number'],
                                        tenant_id=tenant_id)
            context.session.add(app_map)

        return self._make_appliance_map_dict(app_map)

    def _get_appliance_map(self, context, id):
        try:
            appliance_map = self._get_by_id(context, SFCChainAppliance, id)
        except exc.NoResultFound:
            raise q_exc.ChainImageNotFound(appliance_map_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Chain_appliances match for %s' % id)
            raise q_exc.ChainImageNotFound(appliance_map_id=id)
        return appliance_map

    def delete_chain_appliance_map(self, context, id, chain_id):
        appliance_map = self._get_appliance_map(context, id)
        filters = dict()
        filters['chain_map_id'] = [id]
        with context.session.begin(subtransactions=True):
            context.session.delete(appliance_map)

    def update_chain_appliance_map(self, context, id, chain_id,
                                   appliance_map):
        n = appliance_map['appliance_map']
        with context.session.begin(subtransactions=True):
            appliance_map = self._get_appliance_map(context, id)
            appliance_map.update(n)
        return self._make_appliance_map_dict(appliance_map)

    def _make_chain_bypass_rule_dict(self, chain_bypass_rule, fields=None):
        res = {'id': chain_bypass_rule['id'],
               'name': chain_bypass_rule['name'],
               'tenant_id': chain_bypass_rule['tenant_id'],
               'chain_id': chain_bypass_rule['chain_id'],
               'src_mac_type': chain_bypass_rule['src_mac_type'],
               'dest_mac_type': chain_bypass_rule['dest_mac_type'],
               'src_mac': chain_bypass_rule['src_mac'],
               'dest_mac': chain_bypass_rule['dest_mac'],
               'eth_type': chain_bypass_rule['eth_type'],
               'eth_value': chain_bypass_rule['eth_value'],
               'sip_type': chain_bypass_rule['sip_type'],
               'dip_type': chain_bypass_rule['dip_type'],
               'sip_start': chain_bypass_rule['sip_start'],
               'sip_end': chain_bypass_rule['sip_end'],
               'dip_start': chain_bypass_rule['dip_start'],
               'dip_end': chain_bypass_rule['dip_end'],
               'sp_type': chain_bypass_rule['sp_type'],
               'dp_type': chain_bypass_rule['dp_type'],
               'sp_start': chain_bypass_rule['sp_start'],
               'sp_end': chain_bypass_rule['sp_end'],
               'dp_start': chain_bypass_rule['dp_start'],
               'dp_end': chain_bypass_rule['dp_end'],
               'ip_protocol': chain_bypass_rule['ip_protocol'],
               'nwservice_count': chain_bypass_rule['nwservice_count'],
               'nwservice_names': chain_bypass_rule['nwservice_names']}
        return self._fields(res, fields)

    def get_chain_bypass_rules(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCChainBypassRule,
                                    self._make_chain_bypass_rule_dict,
                                    filters=filters, fields=fields)

    def get_chain_bypass_rule(self, context, id, chain_id, fields=None):
        chain_bypass_rule = self._get_chain_bypass_rule(context, id)
        return self._make_chain_bypass_rule_dict(chain_bypass_rule, fields)

    def create_chain_bypass_rule(self, context, chain_bypass_rule, chain_id):
        cbr = chain_bypass_rule['bypass_rule']
        tenant_id = self._get_tenant_id_for_create(context, cbr)

        with context.session.begin(subtransactions=True):
            rule = SFCChainBypassRule(tenant_id=tenant_id,
                                      id=self.__get_id(cbr),
                                      name=cbr['name'],
                                      chain_id=chain_id,
                                      src_mac_type=cbr['src_mac_type'],
                                      dest_mac_type=cbr['dest_mac_type'],
                                      src_mac=cbr['src_mac'],
                                      dest_mac=cbr['dest_mac'],
                                      eth_type=cbr['eth_type'],
                                      eth_value=cbr['eth_value'],
                                      sip_type=cbr['sip_type'],
                                      dip_type=cbr['dip_type'],
                                      sip_start=cbr['sip_start'],
                                      sip_end=cbr['sip_end'],
                                      dip_start=cbr['dip_start'],
                                      dip_end=cbr['dip_end'],
                                      sp_type=cbr['sp_type'],
                                      dp_type=cbr['dp_type'],
                                      sp_start=cbr['sp_start'],
                                      sp_end=cbr['sp_end'],
                                      dp_start=cbr['dp_start'],
                                      dp_end=cbr['dp_end'],
                                      ip_protocol=cbr['ip_protocol'],
                                      nwservice_count=cbr['nwservice_count'],
                                      nwservice_names=cbr['nwservice_names'])
            context.session.add(rule)
        return self._make_chain_bypass_rule_dict(rule)

    def _get_chain_bypass_rule(self, context, id):
        try:
            bypass_rule = self._get_by_id(context, SFCChainBypassRule, id)
        except exc.NoResultFound:
            raise q_exc.ChainmapNotFound(chain_bypass_rule_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chain_bypass_rules match for %s' % id)
            raise q_exc.ChainBypassRuleNotFound(chain_bypass_rule_id=id)
        return bypass_rule

    def delete_chain_bypass_rule(self, context, id, chain_id):
        chain_bypass_rule = self._get_chain_bypass_rule(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chain_bypass_rule)

    def update_chain_bypass_rule(self, context, id, chain_id,
                                 chain_bypass_rule):
        n = chain_bypass_rule['bypass_rule']
        with context.session.begin(subtransactions=True):
            chain_bypass_rule = self._get_chain_bypass_rule(context, id)
            chain_bypass_rule.update(n)
        return self._make_chain_bypass_rule_dict(chain_bypass_rule)

    def _make_chainset_dict(self, chainset, fields=None):
        res = {'id': chainset['id'],
               'name': chainset['name'],
               'zonefull': chainset['zonefull'],
               'direction': chainset['direction'],
               'tenant_id': chainset['tenant_id']}
        return self._fields(res, fields)

    def get_chainsets(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCChainSet,
                                    self._make_chainset_dict,
                                    filters=filters, fields=fields)

    def get_chainset(self, context, id, fields=None):
        chainset = self._get_chainset(context, id)
        return self._make_chainset_dict(chainset, fields)

    def create_chainset(self, context, chainset):
        n = chainset['chainset']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            chainset = SFCChainSet(tenant_id=tenant_id,
                                   id=self.__get_id(n),
                                   name=n['name'],
                                   zonefull=n['zonefull'],
                                   direction=n['direction'])
            context.session.add(chainset)
        return self._make_chainset_dict(chainset)

    def _get_chainset(self, context, id):
        try:
            chainset = self._get_by_id(context, SFCChainSet, id)
        except exc.NoResultFound:
            raise q_exc.ChainSetNotFound(chainset_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chainsets match for %s' % id)
            raise q_exc.ChainSetNotFound(chainset_id=id)
        return chainset

    def delete_chainset(self, context, id):
        chainset = self._get_chainset(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chainset)

    def update_chainset(self, context, id, chainset):
        n = chainset['chainset']
        with context.session.begin(subtransactions=True):
            chainset = self._get_chainset(context, id)
            chainset.update(n)
        return self._make_chainset_dict(chainset)

    def _make_chainset_rule_dict(self, chainset_rule, fields=None):
        res = {'id': chainset_rule['id'],
               'name': chainset_rule['name'],
               'tenant_id': chainset_rule['tenant_id'],
               'chainset_id': chainset_rule['chainset_id'],
               'chain_id': chainset_rule['chain_id'],
               'src_mac_type': chainset_rule['src_mac_type'],
               'dest_mac_type': chainset_rule['dest_mac_type'],
               'src_mac': chainset_rule['src_mac'],
               'dest_mac': chainset_rule['dest_mac'],
               'eth_type': chainset_rule['eth_type'],
               'eth_value': chainset_rule['eth_value'],
               'sip_type': chainset_rule['sip_type'],
               'dip_type': chainset_rule['dip_type'],
               'sip_start': chainset_rule['sip_start'],
               'sip_end': chainset_rule['sip_end'],
               'dip_start': chainset_rule['dip_start'],
               'dip_end': chainset_rule['dip_end'],
               'sp_type': chainset_rule['sp_type'],
               'dp_type': chainset_rule['dp_type'],
               'sp_start': chainset_rule['sp_start'],
               'sp_end': chainset_rule['sp_end'],
               'dp_start': chainset_rule['dp_start'],
               'dp_end': chainset_rule['dp_end'],
               'ip_protocol': chainset_rule['ip_protocol']}
        return self._fields(res, fields)

    def get_chainset_rules(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCChainSelectionRule,
                                    self._make_chainset_rule_dict,
                                    filters=filters, fields=fields)

    def get_chainset_rule(self, context, id, chainset_id, fields=None):
        chainset_rule = self._get_chainset_rule(context, id)
        return self._make_chainset_rule_dict(chainset_rule, fields)

    def create_chainset_rule(self, context, chainset_rule, chainset_id):
        cbr = chainset_rule['rule']
        tenant_id = self._get_tenant_id_for_create(context, cbr)

        with context.session.begin(subtransactions=True):
            rule = SFCChainSelectionRule(tenant_id=tenant_id,
                                         id=self.__get_id(cbr),
                                         name=cbr['name'],
                                         src_mac_type=cbr['src_mac_type'],
                                         dest_mac_type=cbr['dest_mac_type'],
                                         src_mac=cbr['src_mac'],
                                         dest_mac=cbr['dest_mac'],
                                         eth_type=cbr['eth_type'],
                                         eth_value=cbr['eth_value'],
                                         sip_type=cbr['sip_type'],
                                         dip_type=cbr['dip_type'],
                                         sip_start=cbr['sip_start'],
                                         sip_end=cbr['sip_end'],
                                         dip_start=cbr['dip_start'],
                                         dip_end=cbr['dip_end'],
                                         sp_type=cbr['sp_type'],
                                         dp_type=cbr['dp_type'],
                                         sp_start=cbr['sp_start'],
                                         sp_end=cbr['sp_end'],
                                         dp_start=cbr['dp_start'],
                                         dp_end=cbr['dp_end'],
                                         ip_protocol=cbr['ip_protocol'],
                                         chain_id=cbr['chain_id'],
                                         chainset_id=chainset_id)
            context.session.add(rule)
        return self._make_chainset_rule_dict(rule)

    def _get_chainset_rule(self, context, id):
        try:
            chainset_rule = self._get_by_id(context, SFCChainSelectionRule, id)
        except exc.NoResultFound:
            raise q_exc.ChainmapNotFound(chainset_rule_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chainset_rules match for %s' % id)
            raise q_exc.ChainSetRuleNotFound(chainset_rule_id=id)
        return chainset_rule

    def delete_chainset_rule(self, context, id, chainset_id):
        chainset_rule = self._get_chainset_rule(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chainset_rule)

    def update_chainset_rule(self, context, id, chainset_id, chainset_rule):
        n = chainset_rule['rule']
        with context.session.begin(subtransactions=True):
            chainset_rule = self._get_chainset_rule(context, id)
            chainset_rule.update(n)
        return self._make_chainset_rule_dict(chainset_rule)

    def _make_chainmap_dict(self, chainmap, fields=None):
        res = {'id': chainmap['id'],
               'name': chainmap['name'],
               'tenant_id': chainmap['tenant_id'],
               'chainset_id': chainmap['chainset_id'],
               'inbound_network_id': chainmap['inbound_network_id'],
               'outbound_network_id': chainmap['outbound_network_id']}
        return self._fields(res, fields)

    def get_chainmaps(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCChainsetNetworkMap,
                                    self._make_chainmap_dict,
                                    filters=filters, fields=fields)

    def get_chainmap(self, context, id, fields=None):
        chainmap = self._get_chainmap(context, id)
        return self._make_chainmap_dict(chainmap, fields)

    def create_chainmap(self, context, chainmap):
        n = chainmap['chainmap']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            chainmap = SFCChainsetNetworkMap(tenant_id=tenant_id,
                                             id=self.__get_id(n),
                                             name=n['name'],
                                             chainset_id=n['chainset_id'],
                                             inbound_network_id=n[
                                                 'inbound_network_id'],
                                             outbound_network_id=n[
                                                 'inbound_network_id'])
            context.session.add(chainmap)
        return self._make_chainmap_dict(chainmap)

    def _get_chainmap(self, context, id):
        try:
            chainmap = self._get_by_id(context, SFCChainsetNetworkMap, id)
        except exc.NoResultFound:
            raise q_exc.ChainmapNotFound(chainmap_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chainmaps match for %s' % id)
            raise q_exc.ChainMapNotFound(chainmap_id=id)
        return chainmap

    def delete_chainmap(self, context, id):
        chainmap = self._get_chainmap(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chainmap)

    def update_chainmap(self, context, id, chainmap):
        n = chainmap['chainmap']
        n['outbound_network_id'] = n['inbound_network_id']
        with context.session.begin(subtransactions=True):
            chainmap = self._get_chainmap(context, id)
            chainmap.update(n)
        return self._make_chainmap_dict(chainmap)

    def _make_internal_subnet_dict(self, subnet, fields=None):
        res = {'id': subnet['id'],
               'subnet_cidr': subnet['subnet_cidr']}

        return self._fields(res, fields)

    def _get_internal_subnet_handle(self, context, id):
        try:
            internal_subnet = self._get_by_id(context, SFCInternalSubnet, id)
        except exc.NoResultFound:
            raise q_exc.VendorNotFound(vendor_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Internal Subnets match for %s' % id)
            raise q_exc.VendorNotFound(vendor_id=id)
        return internal_subnet

    def create_internal_subnet(self, context, subnet):
        n = subnet['subnet']
        with context.session.begin(subtransactions=True):
            subnet = SFCInternalSubnet(
                id=self.__get_id(n),
                subnet_cidr=n['subnet_cidr'])
            context.session.add(subnet)

        return self._make_internal_subnet_dict(subnet)

    def update_internal_subnet(self, context, id, subnet):
        n = subnet['subnet']
        with context.session.begin(subtransactions=True):
            subnet = self._get_internal_subnet_handle(context, id)
            subnet.update(n)

        return self._make_internal_subnet_dict(subnet)

    @staticmethod
    def get_internal_subnet(context):
        internal_subnet = False
        try:
            internal_subnet = context.session.query(SFCInternalSubnet).one()
        except exc.NoResultFound:
            LOG.error('No Internal Subnet found!!!')
        except exc.MultipleResultsFound:
            LOG.error('Multiple Internal Subnets found!!!')
        return internal_subnet

    def _make_vlanquota_dict(self, vlanquota, fields=None):
        res = {'id': vlanquota['id'],
               'vlan_start': vlanquota['vlan_start'],
               'vlan_end': vlanquota['vlan_end'],
               'tenant_id': vlanquota['tenant_id'], }
        return self._fields(res, fields)

    def get_vlanquota(self, context, id, fields=None):
        vlanquota = self._get_vlanquota(context, id)
        return self._make_vlanquota_dict(vlanquota, fields)

    def get_vlanquotas(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCVLANQuota,
                                    self._make_vlanquota_dict,
                                    filters=filters, fields=fields)

    def create_vlanquota(self, context, vlanquota):
        n = vlanquota['vlanquota']
        tenant_id = self._get_tenant_id_for_create(context, n)

        with context.session.begin(subtransactions=True):
            quota = SFCVLANQuota(tenant_id=tenant_id,
                                 id=n.get('id') or uuidutils.generate_uuid(),
                                 vlan_start=n['vlan_start'],
                                 vlan_end=n['vlan_end'])
            context.session.add(quota)
        return self._make_vlanquota_dict(quota)

    def _get_vlanquota(self, context, id):
        try:
            vlanquota = self._get_by_id(context, SFCVLANQuota, id)
        except exc.NoResultFound:
            raise q_exc.VLANQuotaNotFound(vlanquota_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple vlanquotas match for %s' % id)
            raise q_exc.VLANQuotaNotFound(vlanquota_id=id)
        return vlanquota

    def delete_vlanquota(self, context, id):
        vlanquota = self._get_vlanquota(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(vlanquota)

    def update_vlanquota(self, context, id, vlanquota):
        n = vlanquota['vlanquota']
        with context.session.begin(subtransactions=True):
            vlanquota = self._get_vlanquota(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, vlanquota, n)
            vlanquota.update(n)
        return self._make_vlanquota_dict(vlanquota)

    #def _make_vlan_pair_dict(self, vlanpair, fields=None):
    #    res = {'id': vlanpair['id'],
    #           'instance_id': vlanpair['instance_id'],
    #           'network_id': vlanpair['network_id'],
    #           'vlan_in': vlanpair['vlan_in'],
    #           'vlan_out': vlanpair['vlan_out'],
    #           'chain_id': vlanpair['chain_id'],
    #           'appliance_map_id': vlanpair['appliance_map_id'],
    #           'tenant_id': vlanpair['tenant_id']}
    #
    #    return self._fields(res, fields)
    #
    #def _get_vlan_pair_handle(self, context, id):
    #    try:
    #        vlan_pair = self._get_by_id(context, SFCVLANPair, id)
    #    except exc.NoResultFound:
    #        raise q_exc.VendorNotFound(vendor_id=id)
    #    except exc.MultipleResultsFound:
    #        LOG.error('Multiple Internal Subnets match for %s' % id)
    #        raise q_exc.VendorNotFound(vendor_id=id)
    #    return vlan_pair
    #
    #def create_vlan_pair(self, context, vlanpair):
    #    n = vlanpair['vlanpair']
    #    with context.session.begin(subtransactions=True):
    #        vlanpair = SFCVLANPair(id=self.__get_id(n),
    #                               instance_id=n['instance_id'],
    #                               network_id=n['network_id'],
    #                               vlan_in=n['vlan_in'],
    #                               vlan_out=n['vlan_out'],
    #                               chain_id=n['chain_id'],
    #                               appliance_map_id=n['appliance_map_id'],
    #                               tenant_id=n['tenant_id'])
    #        context.session.add(vlanpair)
    #    return self._make_vlan_pair_dict(vlanpair)
    #
    #def delete_vlan_pair(self, context, id):
    #    vlan_pair = self._get_vlan_pair_handle(context, id)
    #    with context.session.begin(subtransactions=True):
    #        context.session.delete(vlan_pair)
    #
    #def update_vlan_pair(self, context, id, vlanpair):
    #    n = vlanpair['vlanpair']
    #    with context.session.begin(subtransactions=True):
    #        vlanpair = self._get_vlan_pair_handle(context, id)
    #        vlanpair.update(n)
    #
    #    return self._make_vlan_pair_dict(vlanpair)
    #
    #def get_vlan_pairs(self, context, filters=None, fields=None):
    #    return self._get_collection(context, SFCVLANPair,
    #                                self._make_vlan_pair_dict,
    #                                filters=filters, fields=fields)
    
    def _make_chain_appliance_map_instance_dict(self, chain_appliance_map_instance, fields=None):
        res = {'id': chain_appliance_map_instance['id'],
               'instance_uuid': chain_appliance_map_instance['instance_uuid'],
               'appliance_map_id': chain_appliance_map_instance['appliance_map_id'],
               'network_id': chain_appliance_map_instance['network_id'],
               'vlan_in': chain_appliance_map_instance['vlan_in'],
               'vlan_out': chain_appliance_map_instance['vlan_out'],
               'tenant_id': chain_appliance_map_instance['tenant_id']}

        return self._fields(res, fields)

    def _get_chain_appliance_map_instance_handle(self, context, id):
        try:
            chain_appliance_map_instance = self._get_by_id(context, SFCApplianceInstance, id)
        except exc.NoResultFound:
            LOG.error('Appliance Instance Mapping NOT Found for %s' % id)
            raise q_exc.VendorNotFound(vendor_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Appliance Instance Mappings match for %s' % id)
            raise q_exc.VendorNotFound(vendor_id=id)
        return chain_appliance_map_instance
    
    def create_chain_appliance_map_instance(self, context, chain_appliance_map_instance):
        n = chain_appliance_map_instance['instance']
        with context.session.begin(subtransactions=True):
            chain_appliance_map_instance = SFCApplianceInstance(id=self.__get_id(n),
                                                      appliance_map_id=n['appliance_map_id'],
                                                      instance_uuid=n['instance_uuid'],
                                                      network_id=n['network_id'],
                                                      vlan_in=n['vlan_in'],
                                                      vlan_out=n['vlan_out'],
                                                      tenant_id=n['tenant_id'])
            context.session.add(chain_appliance_map_instance)
        return self._make_chain_appliance_map_instance_dict(chain_appliance_map_instance)
    
    def update_chain_appliance_map_instance(self, context, id, chain_appliance_map_instance):
        n = chain_appliance_map_instance['appliance_instance']
        with context.session.begin(subtransactions=True):
            chain_appliance_map_instance = self._get_chain_appliance_map_instance_handle(context, id)
            chain_appliance_map_instance.update(n)

        return self._make_chain_appliance_map_instance_dict(chain_appliance_map_instance)
    
    def get_chain_appliance_map_instances(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCApplianceInstance,
                                    self._make_chain_appliance_map_instance_dict,
                                    filters=filters, fields=fields)
    
    def delete_chain_appliance_map_instance(self, context, id):
        chain_appliance_map_instance = self._get_chain_appliance_map_instance_handle(context, id)
        LOG.debug(_("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"))
        LOG.debug(_("Chain Appliance Instance: %s"), str(chain_appliance_map_instance))
        LOG.debug(_("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"))
        
        with context.session.begin(subtransactions=True):
            context.session.delete(chain_appliance_map_instance)
    
    def _make_chainset_zone_dict(self, chainset_zone, fields=None):
        res = {'id': chainset_zone['id'],
               'zone': chainset_zone['zone'],
               'direction': chainset_zone['direction'],
               'tenant_id': chainset_zone['tenant_id'],
               'chainset_id': chainset_zone['chainset_id']}
        return self._fields(res, fields)

    def get_chainset_zones(self, context, filters=None, fields=None):
        return self._get_collection(context, SFCChainsetZone,
                                    self._make_chainset_zone_dict,
                                    filters=filters, fields=fields)

    def get_chainset_zone(self, context, id, chainset_id, fields=None):
        chainset_zone = self._get_chainset_zone(context, id)
        return self._make_chainset_zone_dict(chainset_zone, fields)

    def create_chainset_zone(self, context, chainset_zone, chainset_id):
        cbr = chainset_zone['zone']
        tenant_id = self._get_tenant_id_for_create(context, cbr)

        with context.session.begin(subtransactions=True):
            zone = SFCChainsetZone(tenant_id=tenant_id,
                                         id=self.__get_id(cbr),
                                         zone=cbr['zone'],
                                         direction=cbr['direction'],
                                         chainset_id=chainset_id)
            context.session.add(zone)
        return self._make_chainset_zone_dict(zone)

    def _get_chainset_zone(self, context, id):
        try:
            chainset_zone = self._get_by_id(context, SFCChainsetZone, id)
        except exc.NoResultFound:
            raise q_exc.ChainmapNotFound(chainset_zone_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple chainset_zones match for %s' % id)
            raise q_exc.ChainSetRuleNotFound(chainset_zone_id=id)
        return chainset_zone

    def delete_chainset_zone(self, context, id, chainset_id):
        chainset_zone = self._get_chainset_zone(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chainset_zone)

    def update_chainset_zone(self, context, id, chainset_id, chainset_zone):
        n = chainset_zone['zone']
        with context.session.begin(subtransactions=True):
            chainset_zone = self._get_chainset_zone(context, id)
            chainset_zone.update(n)
        return self._make_chainset_zone_dict(chainset_zone)
    