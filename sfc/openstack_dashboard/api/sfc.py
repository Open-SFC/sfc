# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Cisco Systems, Inc.
# Copyright 2012 NEC Corporation
# Copyright 2013 Freescale Semiconductor, Inc.
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

from __future__ import absolute_import

import logging

from sfc.crdclient.v2_0 import client as crd_client
from django.utils.datastructures import SortedDict

from horizon.conf import HORIZON_CONFIG

from openstack_dashboard.api.base import APIDictWrapper, url_for


LOG = logging.getLogger(__name__)


class CrdAPIDictWrapper(APIDictWrapper):

    def set_id_as_name_if_empty(self, length=8):
        try:
            if not self._apidict['name']:
                id = self._apidict['id']
                if length:
                    id = id[:length]
                self._apidict['name'] = '(%s)' % id
        except KeyError:
            pass

    def items(self):
        return self._apidict.items()


def crdclient(request):
    LOG.debug('crdclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, url_for(request, 'crd')))
    LOG.debug('user_id=%(user)s, tenant_id=%(tenant)s' %
              {'user': request.user.id, 'tenant': request.user.tenant_id})
    c = crd_client.Client(token=request.user.token.id,
                          endpoint_url=url_for(request, 'crd'))
    return c


class PoolHistory(CrdAPIDictWrapper):

    """Wrapper for Pool History"""
    _attrs = ['id', 'operation', 'pool_id', 'name', 'description'
              'protocol', 'lb_method',
              'admin_status', 'status', 'name_old', 'description_old'
              'protocol_old', 'lb_method_old',
              'admin_status_old', 'status_old', 'user_id', 'logged_at',
              'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(PoolHistory, self).__init__(apiresource)


class PoolMemberHistory(CrdAPIDictWrapper):

    """Wrapper for Pool Member History"""
    _attrs = ['id', 'operation', 'pool_id', 'member_id', 'ip_address'
              'name', 'ip_address', 'port_no', 'weight',
              'admin_status', 'status', 'name_old', 'ip_address_old',
              'port_no_old', 'weight_old',
              'admin_status_old', 'status_old', 'user_id', 'logged_at',
              'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(PoolMemberHistory, self).__init__(apiresource)


class HealthMonitorHistory(CrdAPIDictWrapper):

    """Wrapper for Health Monitor History"""
    _attrs = ['id', 'operation', 'pool_id', 'health_monitor_id', 'name'
              'type', 'delay', 'timeout', 'max_retries', 'http_method',
              'url_path', 'expected_codes', 'admin_status', 'status',
              'name_old', 'type_old', 'delay_old', 'timeout_old', 'max_retries_old',
              'http_method_old', 'url_path_old', 'expected_codes_old',
              'admin_status_old', 'status_old', 'user_id', 'logged_at',
              'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(HealthMonitorHistory, self).__init__(apiresource)


class VirtualIPHistory(CrdAPIDictWrapper):

    """Wrapper for VIP History"""
    _attrs = ['id', 'operation', 'pool_id', 'vip_id', 'config_handle_id', 'name'
              'description', 'port_no', 'protocol', 'connection_limit',
              'session_persistance_type', 'session_persistance_cookie_name', 'admin_status', 'status',
              'name_old', 'description_old', 'port_no_old', 'protocol_old', 'connection_limit_old',
              'session_persistance_type_old', 'session_persistance_cookie_name_old',
              'admin_status_old', 'status_old', 'user_id', 'logged_at',
              'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(VirtualIPHistory, self).__init__(apiresource)


class CategoryHistory(CrdAPIDictWrapper):

    """Wrapper for Category History"""
    _attrs = ['id', 'operation', 'name', 'description',
              'category_id', 'shared',
              'name_old', 'description_old',
              'shared_old', 'user_id', 'logged_at',
              'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(CategoryHistory, self).__init__(apiresource)


class VendorHistory(CrdAPIDictWrapper):

    """Wrapper for Vendor History"""
    _attrs = ['id', 'operation', 'name', 'description'
              'category_id', 'shared',
              'name_old', 'description_old',
              'shared_old', 'user_id', 'logged_at',
              'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(VendorHistory, self).__init__(apiresource)


class CategoryNFHistory(CrdAPIDictWrapper):

    """Wrapper for CategoryNF History"""
    _attrs = ['id', 'operation',
              'category_id', 'networkfunction_id',
              'category_id_old', 'networkfunction_id_old',
              'shared_old', 'user_id', 'logged_at',
              'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(CategoryNFHistory, self).__init__(apiresource)


class ApplianceHistory(CrdAPIDictWrapper):

    """Wrapper for Appliance History"""
    _attrs = ['id', 'operation',
              'name', 'appliance_id', 'category_id', 'vendor_id', 'image_id', 'flavor_id', 'security_group_id', 'shared',
              'name_old', 'appliance_id_old', 'category_id_old', 'vendor_id_old', 'image_id_old', 'flavor_id_old', 'security_group_id_old', 'shared_old',
              'user_id', 'logged_at', 'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(ApplianceHistory, self).__init__(apiresource)


class ChainHistory(CrdAPIDictWrapper):

    """Wrapper for Chain History"""
    _attrs = ['id', 'operation', 'name',
              'chain_id', 'type', 'auto_boot',
              'name_old', 'type_old', 'auto_boot_old',
              'user_id', 'logged_at', 'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(ChainHistory, self).__init__(apiresource)


class ChainApplianceHistory(CrdAPIDictWrapper):

    """Wrapper for ChainAppliance History"""
    _attrs = ['id', 'operation', 'name', 'chain_id'
              'appliance_map_id', 'appliance_id',
              'sequence_number', 'instance_uuid', 'instance_id',
              'name_old', 'chain_id_old', 'appliance_map_id_old', 'appliance_id_old',
              'sequence_number_old', 'instance_uuid_old', 'instance_id_old',
              'user_id', 'logged_at',
              'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(ChainApplianceHistory, self).__init__(apiresource)


class ChainAppliancesNetworkHistory(CrdAPIDictWrapper):

    """Wrapper for ChainAppliancesNetwork History"""
    _attrs = ['id', 'operation', 'appliance_map_network_id', 'name'
              'chain_map_id', 'network_id',
              'name_old', 'chain_map_id_old', 'network_id_old',
              'user_id', 'logged_at', 'version_id', 'tenant_id']

    def __init__(self, apiresource):
        super(ChainAppliancesNetworkHistory, self).__init__(apiresource)


class Networkfunction(CrdAPIDictWrapper):

    """Wrapper for crd networkfunctions"""
    _attrs = ['name', 'id', 'description', 'tenant_id', 'shared']

    def __init__(self, apiresource):
        super(Networkfunction, self).__init__(apiresource)


def networkfunction_list(request, **params):
    LOG.debug("networkfunction_list(): params=%s" % (params))
    networkfunctions = crdclient(request).list_networkfunctions(**params).get('networkfunctions')
    return [Networkfunction(n) for n in networkfunctions]


def networkfunction_list_for_tenant(request, tenant_id, **params):
    LOG.debug("networkfunction_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    networkfunctions = networkfunction_list(request, tenant_id=tenant_id,
                                            shared=False, **params)

    networkfunctions += networkfunction_list(request, shared=True, **params)

    return networkfunctions


def networkfunction_create(request, **kwargs):
    LOG.debug("networkfunction_create(): kwargs = %s" % kwargs)
    body = {'networkfunction': kwargs}
    networkfunction = crdclient(request).create_networkfunction(
        body=body).get('networkfunction')
    return Networkfunction(networkfunction)


def networkfunction_delete(request, networkfunction_id):
    LOG.debug("networkfunction_delete(): catid=%s" % networkfunction_id)
    crdclient(request).delete_networkfunction(networkfunction_id)


def networkfunction_modify(request, networkfunction_id, **kwargs):
    LOG.debug("networkfunction_modify(): cateid=%s, params=%s" %
              (networkfunction_id, kwargs))
    body = {'networkfunction': kwargs}
    networkfunction = crdclient(request).update_networkfunction(networkfunction_id,
                                                                body=body).get('networkfunction')
    return Networkfunction(networkfunction)


def networkfunction_get(request, networkfunction_id, **params):
    LOG.debug("networkfunction_get(): catid=%s, params=%s" %
              (networkfunction_id, params))
    networkfunction = crdclient(request).show_networkfunction(networkfunction_id,
                                                              **params).get('networkfunction')
    return Networkfunction(networkfunction)


class Category(CrdAPIDictWrapper):

    """Wrapper for crd Categories"""
    _attrs = ['name', 'id', 'description', 'tenant_id', 'shared']

    def __init__(self, apiresource):
        super(Category, self).__init__(apiresource)


def category_list(request, **params):
    LOG.debug("category_list(): params=%s" % (params))
    categories = crdclient(request).list_categories(**params).get('categories')
    return [Category(n) for n in categories]


def category_list_for_tenant(request, tenant_id, **params):
    LOG.debug("category_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    categories = category_list(request, tenant_id=tenant_id,
                               shared=False, **params)

    categories += category_list(request, shared=True, **params)

    return categories


def category_create(request, **kwargs):
    LOG.debug("category_create(): kwargs = %s" % kwargs)
    body = {'category': kwargs}
    category = crdclient(request).create_category(body=body).get('category')
    return Category(category)


def category_delete(request, category_id):
    LOG.debug("category_delete(): catid=%s" % category_id)
    crdclient(request).delete_category(category_id)


def category_modify(request, category_id, **kwargs):
    LOG.debug("category_modify(): cateid=%s, params=%s" %
              (category_id, kwargs))
    body = {'category': kwargs}
    category = crdclient(request).update_category(category_id,
                                                  body=body).get('category')
    return Category(category)


def category_get(request, category_id, **params):
    LOG.debug("category_get(): catid=%s, params=%s" % (category_id, params))
    category = crdclient(request).show_category(category_id,
                                                **params).get('category')
    return Category(category)


class Category_networkfunction(CrdAPIDictWrapper):

    """Wrapper for crd category_networkfunctions"""
    _attrs = ['id', 'category_id', 'networkfunction_id', 'tenant_id', 'shared']

    def __init__(self, apiresource):
        super(Category_networkfunction, self).__init__(apiresource)


def category_networkfunction_list(request, **params):
    LOG.debug("category_networkfunction_list(): params=%s" % (params))
    category_networkfunctions = crdclient(request).list_category_networkfunctions(
        **params).get('category_networkfunctions')
    return [Category_networkfunction(n) for n in category_networkfunctions]


def category_networkfunction_list_for_category(request, category_id, **params):
    LOG.debug("category_networkfunction_list_for_category(): category_id=%s, params=%s"
              % (category_id, params))
    category_networkfunctions = category_networkfunction_list(
        request, category_id=category_id, shared=False, **params)
    return category_networkfunctions


def category_networkfunction_create(request, category_id, **kwargs):
    LOG.debug("category_networkfunction_create(): kwargs = %s" % kwargs)
    body = {'nf_map': kwargs}
    #body = kwargs
    category_networkfunction = crdclient(request).create_category_networkfunction(
        category_id, body=body).get('networkfunction')
    return Category_networkfunction(category_networkfunction)


def category_networkfunction_delete(request, category_id, networkfunction_id):
    LOG.debug("category_networkfunction_delete(): catid=%s" % category_id)
    crdclient(request).delete_category_networkfunction(
        category_id, networkfunction_id)


class Vendor(CrdAPIDictWrapper):

    """Wrapper for crd vendors"""
    _attrs = ['name', 'id', 'description', 'tenant_id', 'shared']

    def __init__(self, apiresource):
        super(Vendor, self).__init__(apiresource)


def vendor_list(request, **params):
    LOG.debug("vendor_list(): params=%s" % (params))
    vendors = crdclient(request).list_vendors(**params).get('vendors')
    return [Vendor(n) for n in vendors]


def vendor_list_for_tenant(request, tenant_id, **params):
    LOG.debug("vendor_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    vendors = vendor_list(request, tenant_id=tenant_id,
                          shared=False, **params)

    vendors += vendor_list(request, shared=True, **params)

    return vendors


def vendor_create(request, **kwargs):
    LOG.debug("vendor_create(): kwargs = %s" % kwargs)
    body = {'vendor': kwargs}
    vendor = crdclient(request).create_vendor(body=body).get('vendor')
    return Vendor(vendor)


def vendor_delete(request, vendor_id):
    LOG.debug("vendor_delete(): catid=%s" % vendor_id)
    crdclient(request).delete_vendor(vendor_id)


def vendor_modify(request, vendor_id, **kwargs):
    LOG.debug("vendor_modify(): cateid=%s, params=%s" % (vendor_id, kwargs))
    body = {'vendor': kwargs}
    vendor = crdclient(request).update_vendor(vendor_id,
                                              body=body).get('vendor')
    return Vendor(vendor)


def vendor_get(request, vendor_id, **params):
    LOG.debug("vendor_get(): catid=%s, params=%s" % (vendor_id, params))
    vendor = crdclient(request).show_vendor(vendor_id,
                                            **params).get('vendor')
    return Vendor(vendor)


class Appliance(CrdAPIDictWrapper):

    """Wrapper for crd appliances"""
    _attrs = ['name', 'id', 'tenant_id', 'category_id', 'vendor_id',
              'image_id', 'flavor_id', 'security_group_id', 'form_factor_type',
              'load_share_algorithm', 'high_threshold','low_threshold',
              'pkt_field_to_hash', 'load_indication_type', 'type']

    def __init__(self, apiresource):
        super(Appliance, self).__init__(apiresource)


def appliance_list(request, **params):
    LOG.debug("appliance_list(): params=%s" % (params))
    appliances = crdclient(request).list_appliances(**params).get('appliances')
    return [Appliance(n) for n in appliances]


def appliance_list_for_tenant(request, tenant_id, **params):
    LOG.debug("appliance_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    appliances = appliance_list(request, tenant_id=tenant_id,
                                shared=False, **params)

    return appliances


def appliance_create(request, **kwargs):
    LOG.debug("appliance_create(): kwargs = %s" % kwargs)
    body = {'appliance': kwargs}
    appliance = crdclient(request).create_appliance(body=body).get('appliance')
    return Appliance(appliance)


def appliance_delete(request, appliance_id):
    LOG.debug("appliance_delete(): catid=%s" % appliance_id)
    crdclient(request).delete_appliance(appliance_id)


def appliance_modify(request, appliance_id, **kwargs):
    LOG.debug("appliance_modify(): cateid=%s, params=%s" %
              (appliance_id, kwargs))
    body = {'appliance': kwargs}
    appliance = crdclient(request).update_appliance(appliance_id,
                                                    body=body).get('appliance')
    return Appliance(appliance)


def appliance_get(request, appliance_id, **params):
    LOG.debug("appliance_get(): catid=%s, params=%s" % (appliance_id, params))
    appliance = crdclient(request).show_appliance(appliance_id,
                                                  **params).get('appliance')
    return Appliance(appliance)

class Chain(CrdAPIDictWrapper):

    """Wrapper for crd chains"""
    _attrs = ['name', 'id', 'type', 'tenant_id', 'auto_boot']

    def __init__(self, apiresource):
        super(Chain, self).__init__(apiresource)


def chain_list(request, **params):
    LOG.debug("chain_list(): params=%s" % (params))
    chains = crdclient(request).list_chains(**params).get('chains')
    return [Chain(n) for n in chains]


def chain_list_for_tenant(request, tenant_id, **params):
    LOG.debug("chain_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    chains = chain_list(request, tenant_id=tenant_id,
                        shared=True, **params)

    #chains += chain_list(request, shared=True, **params)

    return chains


def chain_create(request, **kwargs):
    LOG.debug("chain_create(): kwargs = %s" % kwargs)
    body = {'chain': kwargs}
    chain = crdclient(request).create_chain(body=body).get('chain')
    return Chain(chain)


def chain_delete(request, chain_id):
    LOG.debug("chain_delete(): catid=%s" % chain_id)
    crdclient(request).delete_chain(chain_id)


def chain_modify(request, chain_id, **kwargs):
    LOG.debug("chain_modify(): cateid=%s, params=%s" % (chain_id, kwargs))
    body = {'chain': kwargs}
    chain = crdclient(request).update_chain(chain_id,
                                            body=body).get('chain')
    return Chain(chain)


def chain_get(request, chain_id, **params):
    LOG.debug("chain_get(): catid=%s, params=%s" % (chain_id, params))
    chain = crdclient(request).show_chain(chain_id,
                                          **params).get('chain')
    return Chain(chain)


class Appliance_Map(CrdAPIDictWrapper):

    """Wrapper for crd appliance_maps"""
    _attrs = ['name', 'id', 'chain_id', 'appliance_id',
              'sequence_number', 'instance_id', 'instance_uuid', 'tenant_id']

    def __init__(self, apiresource):
        super(Appliance_Map, self).__init__(apiresource)


def appliance_map_list(request, chain_id, **params):
    LOG.debug("appliance_map_list(): params=%s" % (params))
    appliance_maps = crdclient(request).list_appliance_maps(
        chain_id, **params).get('appliances')
    return [Appliance_Map(n) for n in appliance_maps]


def appliance_map_list_for_chain(request, chain_id, **params):
    LOG.debug("appliance_map_list_for_chain(): chain_id=%s, params=%s"
              % (chain_id, params))
    appliance_maps = appliance_map_list(request, chain_id=chain_id, **params)

    return appliance_maps


def appliance_map_create(request, chain_id, **kwargs):
    LOG.debug("appliance_map_create(): kwargs = %s" % kwargs)
    body = {'appliance': kwargs}
    appliance_map = crdclient(request).create_appliance_map(
        chain_id, body=body).get('appliance')
    return Appliance_Map(appliance_map)


def appliance_map_delete(request, chain_id, appliance_map_id):
    LOG.debug("appliance_map_delete(): catid=%s" % appliance_map_id)
    crdclient(request).delete_appliance_map(chain_id, appliance_map_id)


def appliance_map_modify(request, chain_id, appliance_map_id, **kwargs):
    LOG.debug("appliance_map_modify(): cateid=%s, params=%s" %
              (appliance_map_id, kwargs))
    body = {'appliance_map': kwargs}
    appliance_map = crdclient(request).update_appliance_map(chain_id, appliance_map_id,
                                                            body=body).get('appliance')
    return Appliance_Map(appliance_map)


def appliance_map_get(request, chain_id, appliance_map_id, **params):
    LOG.debug("appliance_map_get(): catid=%s, params=%s" %
              (appliance_map_id, params))
    appliance_map = crdclient(request).show_appliance_map(chain_id, appliance_map_id,
                                                          **params).get('appliance')
    return Appliance_Map(appliance_map)

class Appliance_Map_conf(CrdAPIDictWrapper):

    """Wrapper for crd appliance_map_confs"""
    _attrs = ['id', 'name', 'chain_map_id',
              'config_handle_id', 'networkfunction_id', 'tenant_id']

    def __init__(self, apiresource):
        super(Appliance_Map_conf, self).__init__(apiresource)


def appliance_map_conf_list(request, chain_id, appliance_map_id, **params):
    LOG.debug("appliance_map_conf_list(): params=%s" % (params))
    appliance_map_confs = crdclient(request).list_appliance_map_confs(
        chain_id, appliance_map_id, **params).get('confs')
    return [Appliance_Map_conf(n) for n in appliance_map_confs]


def appliance_map_conf_list_for_chain(request, chain_map_id, **params):
    LOG.debug("appliance_map_conf_list_for_chain(): chain_map_id=%s, params=%s"
              % (chain_map_id, params))

    appliance_map_confs = appliance_map_conf_list(request, chain_map_id=chain_map_id,
                                                  shared=False, **params)

    #appliance_map_confs += appliance_map_conf_list(request, shared=True, **params)

    return appliance_map_confs


def appliance_map_conf_create(request, chain_id, appliance_map_id, **kwargs):
    LOG.debug("appliance_map_conf_create(): kwargs = %s" % kwargs)
    body = {'conf': kwargs}
    appliance_map_conf = crdclient(request).create_appliance_map_conf(
        chain_id, appliance_map_id, body=body).get('appliance_map_conf')
    return Appliance_Map_conf(appliance_map_conf)

def appliance_map_conf_delete(request, chain_id, appliance_map_id, appliance_map_conf_id):
    LOG.debug("appliance_map_conf_delete(): catid=%s" % appliance_map_conf_id)
    crdclient(request).delete_appliance_map_conf(
        appliance_map_conf_id, appliance_map_id, chain_id)

# For L2 bypass_rules
class Bypassrule(CrdAPIDictWrapper):

    """Wrapper for crd chains"""
    _attrs = ['id', 'name', 'chain_id', 'src_mac_type', ' dest_mac_type', 'src_mac', 'dest_mac', 'eth_type', 'eth_value', 'sip_type', 'dip_type', 'sip_start', 'sip_end',
              'dip_start', 'dip_end', 'sp_type', 'dp_type', 'sp_start', 'sp_end', 'dp_start', 'dp_end', 'ip_protocol', 'nwservice_count', 'nwservice_names', 'tenent_id']

    def __init__(self, apiresource):
        super(Bypassrule, self).__init__(apiresource)


def bypass_rule_list(request, chain_id, **params):
    LOG.debug("bypass_rule_list(): params=%s" % (params))
    bypass_rules = crdclient(request).list_bypass_rules(
        chain_id, **params).get('bypass_rules')
    return [Bypassrule(n) for n in bypass_rules]


def bypass_rule_list_for_chain(request, chain_id, **params):
    LOG.debug("bypass_rule_list_for_chain(): chain_id=%s, params=%s"
              % (chain_id, params))
    bypass_rules = bypass_rule_list(request, chain_id=chain_id, **params)

    return bypass_rules


def bypass_rule_create(request, chain_id, **kwargs):
    LOG.debug("bypass_rule_create(): kwargs = %s" % kwargs)
    body = {'bypass_rule': kwargs}
    bypass_rule = crdclient(request).create_bypass_rule(
        chain_id, body=body).get('bypass_rule')
    return Bypassrule(bypass_rule)


def bypass_rule_delete(request, chain_id, bypass_rule_id):
    LOG.debug("bypass_rule_delete(): bypass_rule_id=%s" % bypass_rule_id)
    crdclient(request).delete_bypass_rule(chain_id, bypass_rule_id)


def bypass_rule_modify(request, chain_id, bypass_rule_id, **kwargs):
    LOG.debug("bypass_rule_modify(): cateid=%s, params=%s" %
              (bypass_rule_id, kwargs))
    body = {'bypass_rule': kwargs}
    bypass_rule = crdclient(request).update_bypass_rule(chain_id, bypass_rule_id,
                                                          body=body).get('bypass_rule')
    return Bypassrule(bypass_rule)


def bypass_rule_get(request, chain_id, bypass_rule_id, **params):
    LOG.debug("bypass_rule_get(): catid=%s, params=%s" %
              (bypass_rule_id, params))
    bypass_rule = crdclient(request).show_bypass_rule(chain_id, bypass_rule_id,
                                                        **params).get('bypass_rule')
    return Bypassrule(bypass_rule)

class Chainset(CrdAPIDictWrapper):

    """Wrapper for crd chainsets"""
    _attrs = ['name', 'id', 'tenant_id', 'zonefull', 'direction']

    def __init__(self, apiresource):
        super(Chainset, self).__init__(apiresource)


def chainset_list(request, **params):
    LOG.debug("chainset_list(): params=%s" % (params))
    chainsets = crdclient(request).list_chainsets(**params).get('chainsets')
    return [Chainset(n) for n in chainsets]


def chainset_list_for_tenant(request, tenant_id, **params):
    LOG.debug("chainset_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    chainsets = chainset_list(request, tenant_id=tenant_id,
                              shared=True, **params)

    #chainsets += chainset_list(request, shared=True, **params)

    return chainsets


def chainset_create(request, **kwargs):
    LOG.debug("chainset_create(): kwargs = %s" % kwargs)
    body = {'chainset': kwargs}
    chainset = crdclient(request).create_chainset(body=body).get('chainset')
    return Chainset(chainset)


def chainset_delete(request, chainset_id):
    LOG.debug("chainset_delete(): catid=%s" % chainset_id)
    crdclient(request).delete_chainset(chainset_id)


def chainset_modify(request, chainset_id, **kwargs):
    LOG.debug("chainset_modify(): cateid=%s, params=%s" %
              (chainset_id, kwargs))
    body = {'chainset': kwargs}
    chainset = crdclient(request).update_chainset(chainset_id,
                                                  body=body).get('chainset')
    return Chainset(chainset)


def chainset_get(request, chainset_id, **params):
    LOG.debug("chainset_get(): catid=%s, params=%s" % (chainset_id, params))
    chainset = crdclient(request).show_chainset(chainset_id,
                                                **params).get('chainset')
    return Chainset(chainset)

# For L2 rules


class Rule(CrdAPIDictWrapper):

    """Wrapper for crd chainsets"""
    _attrs = ['id', 'name', 'chainset_id', 'chain_id', 'src_mac_type', ' dest_mac_type', 'src_mac', 'dest_mac', 'eth_type', 'eth_value', 'sip_type',
              'dip_type', 'sip_start', 'sip_end', 'dip_start', 'dip_end', 'sp_type', 'dp_type', 'sp_start', 'sp_end', 'dp_start', 'dp_end', 'ip_protocol', 'tenent_id']

    def __init__(self, apiresource):
        super(Rule, self).__init__(apiresource)


def rule_list(request, chainset_id, **params):
    LOG.debug("rule_list(): params=%s" % (params))
    rules = crdclient(request).list_rules(chainset_id, **params).get('rules')
    return [Rule(n) for n in rules]


def rule_list_for_chainset(request, chainset_id, **params):
    LOG.debug("rule_list_for_chain(): chainset_id=%s, params=%s"
              % (chainset_id, params))
    rules = rule_list(request, chainset_id=chainset_id, **params)

    return rules


def rule_create(request, chainset_id, **kwargs):
    LOG.debug("rule_create(): kwargs = %s" % kwargs)
    body = {'rule': kwargs}
    rule = crdclient(request).create_rule(chainset_id, body=body).get('rule')
    return Rule(rule)


def rule_delete(request, chainset_id, rule_id):
    LOG.debug("rule_delete(): rule_id=%s" % rule_id)
    crdclient(request).delete_rule(chainset_id, rule_id)


def rule_modify(request, chainset_id, rule_id, **kwargs):
    LOG.debug("rule_modify(): cateid=%s, params=%s" % (rule_id, kwargs))
    body = {'rule': kwargs}
    rule = crdclient(request).update_rule(chainset_id, rule_id,
                                          body=body).get('rule')
    return Rule(rule)


def rule_get(request, chainset_id, rule_id, **params):
    LOG.debug("rule_get(): catid=%s, params=%s" % (rule_id, params))
    rule = crdclient(request).show_rule(chainset_id, rule_id,
                                        **params).get('rule')
    return Rule(rule)


# For chain Map
class Chainmap(CrdAPIDictWrapper):

    """Wrapper for crd chainmaps"""
    _attrs = ['name', 'id', 'type', 'inbound_network_id',
              'outbound_network_id', 'chainset_id', 'tenant_id']

    def __init__(self, apiresource):
        super(Chainmap, self).__init__(apiresource)


def chainmap_list(request, **params):
    LOG.debug("chainmap_list(): params=%s" % (params))
    chainmaps = crdclient(request).list_chainmaps(**params).get('chainmaps')
    return [Chainmap(n) for n in chainmaps]


def chainmap_list_for_tenant(request, tenant_id, **params):
    LOG.debug("chainmap_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    chainmaps = chainmap_list(request, tenant_id=tenant_id,
                              shared=True, **params)

    #chainmaps += chainmap_list(request, shared=True, **params)

    return chainmaps


def chainmap_create(request, **kwargs):
    LOG.debug("chainmap_create(): kwargs = %s" % kwargs)
    body = {'chainmap': kwargs}
    chainmap = crdclient(request).create_chainmap(body=body).get('chainmap')
    return Chainmap(chainmap)


def chainmap_delete(request, chainmap_id):
    LOG.debug("chainmap_delete(): catid=%s" % chainmap_id)
    crdclient(request).delete_chainmap(chainmap_id)


def chainmap_modify(request, chainmap_id, **kwargs):
    LOG.debug("chainmap_modify(): cateid=%s, params=%s" %
              (chainmap_id, kwargs))
    body = {'chainmap': kwargs}
    chainmap = crdclient(request).update_chainmap(chainmap_id,
                                                  body=body).get('chainmap')
    return Chainmap(chainmap)


def chainmap_get(request, chainmap_id, **params):
    LOG.debug("chainmap_get(): catid=%s, params=%s" % (chainmap_id, params))
    chainmap = crdclient(request).show_chainmap(chainmap_id,
                                                **params).get('chainmap')
    return Chainmap(chainmap)


class Config_handle(CrdAPIDictWrapper):

    """Wrapper for crd config_handles"""
    _attrs = ['name', 'id', 'description',
              'tenant_id', 'shared', 'config_mode']

    def __init__(self, apiresource):
        super(Config_handle, self).__init__(apiresource)


def config_handle_list(request, **params):
    LOG.debug("config_handle_list(): params=%s" % (params))
    config_handles = crdclient(request).list_config_handles(
        **params).get('config_handles')
    return [Config_handle(n) for n in config_handles]


def config_handle_list_for_tenant(request, tenant_id, **params):
    LOG.debug("config_handle_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))
    config_handles = config_handle_list(request, tenant_id=tenant_id,
                                        shared=False, **params)

    #config_handles += config_handle_list(request, shared=True, **params)

    return config_handles


def config_handle_create(request, **kwargs):
    LOG.debug("config_handle_create(): kwargs = %s" % kwargs)
    body = {'config_handle': kwargs}
    config_handle = crdclient(request).create_config_handle(
        body=body).get('config_handle')
    return Config_handle(config_handle)


def config_handle_delete(request, config_handle_id):
    LOG.debug("config_handle_delete(): catid=%s" % config_handle_id)
    crdclient(request).delete_config_handle(config_handle_id)


def config_handle_modify(request, config_handle_id, **kwargs):
    LOG.debug("config_handle_modify(): cateid=%s, params=%s" %
              (config_handle_id, kwargs))
    body = {'config_handle': kwargs}
    config_handle = crdclient(request).update_config_handle(config_handle_id,
                                                            body=body).get('config_handle')
    return Config_handle(config_handle)


def config_handle_get(request, config_handle_id, **params):
    LOG.debug("config_handle_get(): catid=%s, params=%s" %
              (config_handle_id, params))
    config_handle = crdclient(request).show_config_handle(config_handle_id,
                                                          **params).get('config_handle')
    return Config_handle(config_handle)


def generate_config(request, config_handle_id, **params):
    LOG.debug("generate_config(): config_handle_id=%s" % config_handle_id)
    config = crdclient(request).generate_configuration(
        config_handle_id, **params).get('config')
    return config


def launch_chain(request, **kwargs):
    LOG.debug("launch_chain(): kwargs = %s" % kwargs)
    body = {'launch': kwargs}
    launch = crdclient(request).launch_chain(body=body).get('launch')
    return launch

# Pool History


def pool_history(request, **params):
    LOG.debug("pool_history(): params=%s" % (params))
    pool_history = crdclient(request).list_pool_history(
        **params).get('pool_histories')
    return [PoolHistory(s) for s in pool_history]


def pool_history_get(request, delta_id, **params):
    LOG.debug("pool_history_get(): delta_id=%s, params=%s" %
              (delta_id, params))
    pool_delta = crdclient(request).show_pool_history(delta_id,
                                                      **params).get('pool_historie')
    return PoolHistory(pool_delta)

# Pool Member History


def member_history(request, **params):
    LOG.debug("member_history(): params=%s" % (params))
    pool_member_history = crdclient(request).list_member_history(
        **params).get('member_histories')
    return [PoolMemberHistory(s) for s in pool_member_history]


def member_history_get(request, delta_id, **params):
    LOG.debug("member_history_get(): delta_id=%s, params=%s" %
              (delta_id, params))
    member_delta = crdclient(request).show_member_history(delta_id,
                                                          **params).get('member_historie')
    return PoolMemberHistory(member_delta)

# Health Monitor History


def health_monitor_history(request, **params):
    LOG.debug("health_monitor_history(): params=%s" % (params))
    health_monitor_history = crdclient(
        request).list_health_monitor_history(**params).get('hm_histories')
    return [HealthMonitorHistory(s) for s in health_monitor_history]


def health_monitor_history_get(request, delta_id, **params):
    LOG.debug("health_monitor_history_get(): delta_id=%s, params=%s" %
              (delta_id, params))
    monitor_delta = crdclient(request).show_monitor_history(delta_id,
                                                            **params).get('hm_historie')
    return HealthMonitorHistory(monitor_delta)

# Virtual IP History


def virtual_ip_history(request, **params):
    LOG.debug("virtual_ip_history(): params=%s" % (params))
    virtual_ip_history = crdclient(request).list_virtual_ip_history(
        **params).get('vip_histories')
    return [VirtualIPHistory(s) for s in virtual_ip_history]


def virtual_ip_history_get(request, delta_id, **params):
    LOG.debug("virtual_ip_history_get(): delta_id=%s, params=%s" %
              (delta_id, params))
    vip_delta = crdclient(request).show_vip_history(delta_id,
                                                    **params).get('vip_historie')
    return VirtualIPHistory(vip_delta)

########################NW Service Delta #########################


class Nsdelta(CrdAPIDictWrapper):

    """Wrapper for crd nsdeltas"""
    _attrs = ['keyword', 'delta', 'tenant_id', 'id']

    def __init__(self, apiresource):
        super(Nsdelta, self).__init__(apiresource)


def nsdelta_list(request, **params):
    LOG.debug("nsdelta_list(): params=%s" % (params))
    nsdeltas = crdclient(request).list_nsdeltas(**params).get('nsdeltas')
    return [Nsdelta(n) for n in nsdeltas]


def nsdelta_get(request, keyword, **params):
    nsdelta = crdclient(request).show_nsdelta(keyword,
                                              **params).get('nsdelta')
    return Nsdelta(nsdelta)

# OF Clusters


class OFCluster(CrdAPIDictWrapper):

    """Wrapper for CRD Openflow Clusters"""
    _attrs = ['name', 'id', 'ca_cert_pem',
              'private_key_pem', 'root_cert_pem',
              'inter_cert_pem', 'created_at', 'deleted_at',
              'updated_at']

    def __init__(self, apiresource):
        super(OFCluster, self).__init__(apiresource)


class OFController(CrdAPIDictWrapper):

    """Wrapper for CRD Openflow Controllers"""
    _attrs = ['name', 'id', 'ip_address',
              'port', 'cell',
              'cluster_id', 'status', 'created_at', 'deleted_at',
              'updated_at']

    def __init__(self, apiresource):
        super(OFController, self).__init__(apiresource)


class LogicalSwitches(CrdAPIDictWrapper):

    """Wrapper for CRD Openflow Logical Switches"""
    _attrs = ['name', 'id', 'ip_address',
              'port', 'certificate_pem', 'private_key_pem',
              'cluster_id', 'cluster_id', 'datapath_id', 'created_at', 'deleted_at',
              'updated_at']

    def __init__(self, apiresource):
        super(LogicalSwitches, self).__init__(apiresource)


def of_cluster_list(request, **params):
    LOG.debug("of_cluster_list(): params=%s" % (params))
    clusters = crdclient(request).list_ofclusters(**params).get('ofclusters')
    return [OFCluster(n) for n in clusters]


def of_cluster_create(request, **kwargs):
    """
    Create a OF Cluster
    """
    LOG.debug("of_cluster_create(): kwargs = %s" % kwargs)
    body = {'ofcluster': kwargs}
    cluster = crdclient(request).create_ofcluster(body=body).get('ofcluster')
    return OFCluster(cluster)


def of_cluster_delete(request, cluster_id):
    LOG.debug("of_cluster_delete(): cluster_id=%s" % cluster_id)
    crdclient(request).delete_ofcluster(cluster_id)


def of_cluster_get(request, cluster_id, **params):
    LOG.debug("of_cluster_get(): cluster_id=%s, params=%s" %
              (cluster_id, params))
    cluster = crdclient(request).show_ofcluster(
        cluster_id, **params).get('ofcluster')
    return OFCluster(cluster)


def of_cluster_modify(request, cluster_id, **kwargs):
    LOG.debug("of_cluster_modify(): cluster_id=%s, kwargs=%s" %
              (cluster_id, kwargs))
    body = {'ofcluster': kwargs}
    cluster = crdclient(request).update_ofcluster(cluster_id,
                                                  body=body).get('ofcluster')
    return OFCluster(cluster)


def of_controller_list(request, **params):
    LOG.debug("of_controller_list(): params=%s" % (params))
    controllers = crdclient(request).list_ofcontrollers(
        **params).get('ofcontrollers')
    return [OFController(n) for n in controllers]


def of_controller_create(request, **kwargs):
    """
    Create a OF Controller
    """
    LOG.debug("of_controller_create(): kwargs = %s" % kwargs)
    body = {'ofcontroller': kwargs}
    controller = crdclient(request).create_ofcontroller(
        body=body).get('ofcontroller')
    return OFController(controller)


def of_controller_get(request, controller_id, cluster_id, **params):
    LOG.debug("of_controller_get(): controller_id=%s, params=%s" %
              (controller_id, params))
    body = {'cluster_id': cluster_id}
    controller = crdclient(request).show_ofcontroller(
        controller_id, body=body).get('ofcontroller')
    return OFController(controller)


def of_controller_delete(request, cluster_id, controller_id):
    LOG.debug("of_controller_delete(): cluster_id=%s, controller_id=%s" %
              (cluster_id, controller_id))
    body = {'body': {'cluster_id': cluster_id, 'id': controller_id}}
    crdclient(request).delete_ofcontroller(controller_id, body=body)


def of_switches_list(request, cluster_id, controller_id, **params):
    LOG.debug("of_switches_list(): params=%s" % (params))
    switches = crdclient(request).list_logicalswitchs(
        cluster_id, controller_id, **params).get('logicalswitchs')
    return [LogicalSwitches(n) for n in switches]


def of_switch_delete(request, cluster_id, controller_id, switch_id):
    LOG.debug("of_switch_delete(): cluster_id=%s, controller_id=%s, switch_id=%s" % (
        cluster_id, controller_id, switch_id))
    body = {'body': {'cluster_id': cluster_id,
                     'controller_id': controller_id, 'id': switch_id}}
    crdclient(request).delete_logicalswitch(switch_id, body=body)


def of_switch_create(request, **kwargs):
    """
    Create a OF Logical Switch
    """
    LOG.debug("of_switch_create(): kwargs = %s" % kwargs)
    body = {'logicalswitch': kwargs}
    switch = crdclient(request).create_logicalswitch(
        body=body).get('logicalswitchs')
    return LogicalSwitches(switch)


class ComputeNodes(CrdAPIDictWrapper):

    """Wrapper for CRD ComputeNodes"""
    _attrs = ['compute_id', 'id', 'ip_address',
              'ip_address', 'hostname', 'datapath_id',
              'created_at', 'ovs_port', 'switch']


class Instances(CrdAPIDictWrapper):

    """Wrapper for CRD Instances"""
    _attrs = ['display_name', 'instance_id', 'state',
              'created_at', 'host', 'launched_at']


def compute_node_list(request, **params):
    LOG.debug("compute_node_list(): params=%s" % (params))
    computes = crdclient(request).list_computes(**params).get('computes')
    return [ComputeNodes(n) for n in computes]


def instance_list(request, **params):
    LOG.debug("instance_list(): params=%s" % (params))
    instances = crdclient(request).list_instances(**params).get('instances')
    return [Instances(n) for n in instances]

##########VLAN Quotas#####################


class VLANQuota(CrdAPIDictWrapper):

    """Wrapper for crd vlanquotas"""
    _attrs = ['id', 'vlan_start', 'vlan_end', 'tenant_id']

    def __init__(self, apiresource):
        super(VLANQuota, self).__init__(apiresource)


def vlanquota_list(request, **params):
    LOG.debug("vlanquota_list(): params=%s" % (params))
    vlanquotas = crdclient(request).list_vlanquotas(**params).get('vlanquotas')
    return [VLANQuota(n) for n in vlanquotas]


def vlanquota_list_for_tenant(request, tenant_id, **params):
    LOG.debug("vlanquota_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))
    vlanquotas = vlanquota_list(request, tenant_id=tenant_id, **params)
    return vlanquotas


def vlanquota_create(request, **kwargs):
    LOG.debug("vlanquota_create(): kwargs = %s" % kwargs)
    body = {'vlanquota': kwargs}
    vlanquota = crdclient(request).create_vlanquota(body=body).get('vlanquota')
    return VLANQuota(vlanquota)


def vlanquota_delete(request, vlanquota_id):
    LOG.debug("vlanquota_delete(): catid=%s" % vlanquota_id)
    crdclient(request).delete_vlanquota(vlanquota_id)


def vlanquota_modify(request, vlanquota_id, **kwargs):
    LOG.debug("vlanquota_modify(): cateid=%s, params=%s" %
              (vlanquota_id, kwargs))
    body = {'vlanquota': kwargs}
    vlanquota = crdclient(request).update_vlanquota(vlanquota_id,
                                                    body=body).get('vlanquota')
    return VLANQuota(vlanquota)


def vlanquota_get(request, vlanquota_id, **params):
    LOG.debug("vlanquota_get(): catid=%s, params=%s" % (vlanquota_id, params))
    vlanquota = crdclient(request).show_vlanquota(vlanquota_id,
                                                  **params).get('vlanquota')
    return VLANQuota(vlanquota)


#############Appliance Map Instances#######################
class Appliance_Map_instance(CrdAPIDictWrapper):

    """Wrapper for crd appliance_map_instances"""
    _attrs = ['id', 'appliance_map_id',
              'instance_uuid', 'network_id', 'tenant_id',
              'vlan_in', 'vlan_out']

    def __init__(self, apiresource):
        super(Appliance_Map_instance, self).__init__(apiresource)


def appliance_map_instance_list(request, chain_id, appliance_map_id, **params):
    LOG.debug("appliance_map_instance_list(): params=%s" % (params))
    appliance_map_instances = crdclient(request).list_appliance_map_instances(
        chain_id, appliance_map_id, **params).get('instances')
    return [Appliance_Map_instance(n) for n in appliance_map_instances]


def appliance_map_instance_list_for_chain(request, chain_id, appliance_map_id, **params):
    LOG.debug("appliance_map_instance_list_for_chain(): chain_id=%s, appliance_map_id=%s, params=%s"
              % (chain_id, appliance_map_id, params))

    appliance_map_instances = appliance_map_instance_list(request, chain_id, appliance_map_id,
                                                  shared=False, **params)

    #appliance_map_instances += appliance_map_instance_list(request, shared=True, **params)

    return appliance_map_instances

#############Zones#######################
class Zone(CrdAPIDictWrapper):

    """Wrapper for crd chainsets"""
    _attrs = ['id', 'zone', 'chainset_id', 'direction', 'tenent_id']

    def __init__(self, apiresource):
        super(Zone, self).__init__(apiresource)


def zone_list(request, chainset_id, **params):
    LOG.debug("zone_list(): params=%s" % (params))
    zones = crdclient(request).list_zones(chainset_id, **params).get('zones')
    return [Zone(n) for n in zones]


def zone_list_for_chainset(request, chainset_id, **params):
    LOG.debug("zone_list_for_chain(): chainset_id=%s, params=%s"
              % (chainset_id, params))
    zones = zone_list(request, chainset_id=chainset_id, **params)

    return zones


def zone_create(request, chainset_id, **kwargs):
    LOG.debug("zone_create(): kwargs = %s" % kwargs)
    body = {'zone': kwargs}
    zone = crdclient(request).create_zone(chainset_id, body=body).get('zone')
    return Zone(zone)


def zone_delete(request, chainset_id, zone_id):
    LOG.debug("zone_delete(): zone_id=%s" % zone_id)
    crdclient(request).delete_zone(chainset_id, zone_id)


def zone_modify(request, chainset_id, zone_id, **kwargs):
    LOG.debug("zone_modify(): cateid=%s, params=%s" % (zone_id, kwargs))
    body = {'zone': kwargs}
    zone = crdclient(request).update_zone(chainset_id, zone_id,
                                          body=body).get('zone')
    return Zone(zone)


def zone_get(request, chainset_id, zone_id, **params):
    LOG.debug("zone_get(): catid=%s, params=%s" % (zone_id, params))
    zone = crdclient(request).show_zone(chainset_id, zone_id,
                                        **params).get('zone')
    return Zone(zone)
