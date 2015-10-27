# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

from oslo.config import cfg
import time
import socket

from nscs.crdservice.common import topics
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import context
from nscs.crdservice import context as crd_context
from nscs.crdservice.openstack.common.rpc import proxy
from nscs.crdservice.openstack.common import rpc
from nscs.crdservice.openstack.common.rpc import dispatcher
from nscs.crdservice.manager import CrdManager as q_man
from nscs.crdservice.common import exceptions as q_exc

from novaclient.v1_1 import client as nova_client
from keystoneclient.v2_0 import client as keystone_client
from neutronclient.v2_0 import client as neutron_client

from sfc.crdservice.db import sfc_db
from sfc.crdservice.db import delta as sfc_delta_db
from cns.crdservice.db import nova as nova_db

LOG = logging.getLogger(__name__)

crd_nwservices_opts = [
    cfg.StrOpt('admin_user',default="crd"),
    cfg.StrOpt('admin_password',default="password"),
    cfg.StrOpt('admin_tenant_name',default="service"),
    cfg.StrOpt('auth_url'),
]

cfg.CONF.register_opts(crd_nwservices_opts, "nscs_authtoken")


class SFCDriver(proxy.RpcProxy):
    """
        Network Services Driver is used for following tasks:
            1. Application VM Monitoring. To dynamically start service VMs
            when one or more applications are brought up
            2. Service VM Load Monitoring. To dynamically check for service
            VM load, dynamically spawn new service VMs if require
            and share the load to new service VM
            3. Inform corresponding relay agent when there is any
            configuration change.
    """
    # default RPC API version
    RPC_API_VERSION = '1.0'

    _instance = None

    def __init__(self, topic=topics.NWSERVICES_PLUGIN):
        super(SFCDriver, self).__init__(topic=topic,
                                        default_version=self.RPC_API_VERSION)
        self.context = crd_context.Context('crd', 'crd',
                                           is_admin=True)
        self.setup_rpc()


    def setup_rpc(self):
        # RPC support
        self.rpc_context = context.RequestContext('crd', 'crd',
                                                  is_admin=True)
        self.conn = rpc.create_connection(new=True)
        self.dispatcher = dispatcher.RpcDispatcher([self])
        self.conn.create_consumer(self.topic, self.dispatcher, fanout=False)
        # Consume from all consumers in a thread
        self.conn.consume_in_thread()

    def get_instance_details(self, instance_uuid, timeout=300):
        if instance_uuid == '':
            raise q_exc.InstanceNotFound(instance_id=instance_uuid)
        try:
            #LOG.debug(_("waiting for instance to be active..."))
            instance_id, tenant_id, hostname = self.wait_for_instance_active(
                instance_uuid)
        except q_exc.InstanceErrorState, msg:
            LOG.error(_(msg))
            raise q_exc.InstanceNotFound(instance_id=instance_uuid)
        #LOG.debug(_('tenant id = %s, instance id = %s hostname=%s'),
        # tenant_id,str(instance_id),hostname)
        return tenant_id, instance_uuid, hostname

    def wait_for_instance_active(self, instance_uuid, timeout=300):
        #LOG.debug('Looping for 300 secs')
        for i in range(0, timeout):
            time.sleep(1)
            #LOG.debug('After Sleep.')
            nt = novaclient()
            #LOG.debug('novaclient = %s' % str(nt))
            try:
                instance_details = nt.servers.get(instance_uuid)
            except Exception, msg:
                LOG.error(msg)
                raise q_exc.InstanceErrorState(instance_uuid=instance_uuid)
            #LOG.debug(_('VM state = %s'),instance_details.__getattribute__(
            # 'OS-EXT-STS:vm_state'))
            #LOG.debug('tenant id = %s' % instance_details.__getattribute__(
            # 'tenant_id'))
            if instance_details.__getattribute__(
                    'OS-EXT-STS:vm_state') == 'active':
                #LOG.debug('vm state is active')
                instance_id = int(instance_details.__getattribute__(
                    'OS-EXT-SRV-ATTR:instance_name').split('instance-')[1], 16)
                tenant_id = instance_details.__getattribute__('tenant_id')
                hostname = instance_details.__getattribute__(
                    'OS-EXT-SRV-ATTR:host')
                return instance_id, tenant_id, hostname
            elif instance_details.__getattribute__(
                    'OS-EXT-STS:vm_state') == 'error':
                raise q_exc.InstanceErrorState(instance_id=instance_uuid)

    def prepare_msg(self, instance_id, tenant_id, msg,
                    update_type='config_update'):
        m = self.make_msg(update_type,
                          instance_id=instance_id,
                          tenant_id=tenant_id,
                          config_request=msg)
        #LOG.debug(_('msg framed in NwServicesDriver = %s\n\n'),str(m))
        return m

    def _get_relay_topic_name(self, hostname):
        return '%s.%s' % (topics.RELAY_AGENT, hostname)

    def send_cast(self, logical_id, msg):
        #LOG.debug('In send_cast\n')
        self.db = sfc_db.SFCPluginDb()
        try:
            appliance_id = None
            filters = {}
            filters['config_handle_id'] = [logical_id]
            appliances = self.db.get_appliances(self.context,
                                                filters=filters)
            for appliance in appliances:
                LOG.debug(_("##########################Appliance: %s"), str(appliance))
                appliance_id = appliance['id']
            
            if appliance_id:
                filters = {}
                filters['appliance_id'] = [appliance_id]
                chain_appliance_maps = self.db.get_chain_appliance_maps(self.context,
                                                                       filters=filters)
                if chain_appliance_maps:
                    ###TODO :: Need to get instances from new table service_instances
                    appliance_map = chain_appliance_maps[0]
                    #instance_uuid = appliance_map['instance_uuid']
                    if appliance_map:
                        chain_appliance_id = appliance_map['id']
                        # Get instances from the table sfc_appliance_instances
                        filters = {}
                        filters['appliance_map_id'] = [chain_appliance_id]
                        appliance_instances = self.db.get_chain_appliance_map_instances(self.context,
                                                                              filters=filters)
                        
                        if appliance_instances:
                            for app_instance in appliance_instances:
                                instance_uuid = app_instance['instance_uuid']
                                if instance_uuid:
                                    tenant_id, instance_id, hostname = self.get_instance_details(instance_uuid)
                                    self.cast(self.rpc_context,
                                              self.prepare_msg(instance_id, tenant_id, msg),
                                              topic=self._get_relay_topic_name(hostname))
            
        except q_exc.InstanceNotFound, msg:
            LOG.error(msg)

    def send_delete_instance(self, instance_id, tenant_id, hostname):
        try:
            #LOG.debug(_('sending cast to machine %s\n\n'),
            # self._get_relay_topic_name(hostname))
            msg = {}
            self.cast(self.rpc_context,
                      self.prepare_msg(instance_id, tenant_id, msg,
                                       update_type="instance_deleted"),
                      topic=self._get_relay_topic_name(hostname))
        except q_exc.InstanceNotFound, msg:
            LOG.error(msg)


    def send_vlancast(self, instance_uuid, msg):
        try:
            instance_id, tenant_id, hostname = self.wait_for_instance_active(
                instance_uuid)
        except q_exc.InstanceErrorState, msg:
            LOG.error(_(msg))
            raise q_exc.InstanceNotFound(instance_uuid=instance_uuid)
        self.cast(self.rpc_context,
                  self.prepare_msg(instance_uuid, tenant_id, msg),
                  topic=self._get_relay_topic_name(hostname))


    def launch_chain(self, context, chainset_id, chainmap_id, rule_id):
        self.db = sfc_db.SFCPluginDb()
        self.delta_db = sfc_delta_db.SfcDeltaDb()
        self.crdnovadb = nova_db.NovaDb()
        self.plugin = q_man.get_plugin()
        nt = novaclient(context)
        qt = crdclient(context)
        rule_details = self.db.get_chainset_rule(context, rule_id,
                                                   chainset_id)
        chain_id = rule_details['chain_id']

        chainmap_details = self.db.get_chainmap(context, chainmap_id)
        inbound_network = chainmap_details['inbound_network_id']
        outbound_network = chainmap_details['outbound_network_id']
        chainset_details = self.db.get_chainset(context, chainset_id)
        inbound_net_id = inbound_network
        outbound_net_id = outbound_network

        #LOG.debug(
        # '*****************************************************************************\n')
        #LOG.debug('Chain ID = %s' % str(chain_id))
        #LOG.debug('Inbound Network = %s' % str(inbound_net_id))
        #LOG.debug('Outbound Network = %s' % str(outbound_net_id))
        #LOG.debug(
        # '*****************************************************************************\n')


        filters = {}
        filters['chain_id'] = [chain_id]
        appliance_maps = self.db.get_chain_appliance_maps(context, filters)
        appliance_count = len(appliance_maps)
        appliance_maps = sorted(appliance_maps,
                                key=lambda k: k['sequence_number'])
        #LOG.debug(
        # '#############################################################################\n')
        #LOG.debug('appliance count = %s' % str(appliance_count))
        #LOG.debug(
        # '#############################################################################\n')
        #inner_subnets = self.subnet_list(given_subnet, appliance_count-1)
        #LOG.debug(
        # '#############################################################################\n')
        #LOG.debug('inner subnets = %s' % str(inner_subnets))
        #LOG.debug(
        # '#############################################################################\n')
        last_net = None
        count = 1
        for appliance_map in appliance_maps:
            name = appliance_map['name']
            network_name = 'internal_net_' + name
            appliance_map_id = appliance_map['id']
            chain_id = appliance_map['chain_id']
            appliance_id = appliance_map['appliance_id']
            appliance = self.db.get_appliance(context,
                                              appliance_id)
            glance_image_id = appliance['image_id']
            flavor_id = appliance['flavor_id']
            security_group_id = appliance['security_group_id']

            security_groups = []
            secgrp = nt.security_groups.get(appliance['security_group_id'])
            security_group_name = secgrp.__getattribute__('name')
            security_groups.append(security_group_name)

            nics = []
            if inbound_net_id == outbound_net_id:
                nic = {"net-id": inbound_net_id, "v4-fixed-ip": ""}
                nics.append(nic)
            else:
                nic1 = {"net-id": inbound_net_id, "v4-fixed-ip": ""}
                nics.append(nic1)
                
                nic2 = {"net-id": outbound_net_id, "v4-fixed-ip": ""}
                nics.append(nic2)
            
            config_handle_id = appliance['config_handle_id']
            if (config_handle_id == ''):
                msg = _(
                    'Failed to launch chain  %s, No Cnfiguration '
                    'associated') % chain_id
                LOG.error(msg)
                

            LOG.debug(
                '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n')
            LOG.debug('NICS = %s' % str(nics))
            LOG.debug('Name = %s' % str(name))
            LOG.debug('Galnce Image ID = %s' % str(glance_image_id))
            LOG.debug('Security Groups = %s' % str(security_groups))
            LOG.debug(
                '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n')
            dev_mapping = None
            custom_script = None
            keypair_id = None
            meta = {'vmtype': 'service'}
            instance_count = 1

            instance = nt.servers.create(name,
                                         glance_image_id,
                                         flavor_id,
                                         meta=meta,
                                         security_groups=security_groups,
                                         nics=nics,
                                         instance_count=int(instance_count))
            LOG.debug('^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            LOG.debug('INSTANCE = %s' % str(instance))
            LOG.debug('^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            msg = _('Instance %s was successfully launched.') % instance.id
            LOG.debug(msg)
            instance_uuid = instance.id
            
            while (1):
                msg = _("Waiting for Instance in CRD DB ...%s") % str(
                    instance_uuid)
                LOG.debug("############################################")
                LOG.debug(msg)
                LOG.debug("############################################")
                try:
                    crd_instance = self.crdnovadb.get_instance(context,
                                                               instance_uuid)
                    if crd_instance['state'] == 'active' or crd_instance[
                        'state'] == 'error':
                        break
                except:
                    pass
                time.sleep(5)
            
            appliance_instance_body = {
                'instance': {
                    'appliance_map_id': appliance_map_id,
                    'instance_uuid': instance_uuid,
                    'tenant_id': context.tenant_id,
                    'network_id': None,
                    'vlan_in': None,
                    'vlan_out': None
                }
            }
            appliance_instance = self.db.create_chain_appliance_map_instance(context, appliance_instance_body)
            ###DELTA
            data = appliance_instance
            data.update({'operation' : 'create'})
            delta={}
            delta.update({'appliance_instances_delta':data})
            result_delta = self.delta_db.create_appliance_instances_delta(context,delta)
            ###DELTA
            
            appliance_instance_id = appliance_instance['id']
            
            if instance_uuid:
                fliters = []
                filters['tenant_id'] = [context.tenant_id]
                #vlanquotas = cfg.CONF.nscs_authtoken.vlan_quota
                vlanquotas = '100-200'
                #vlanquotas = self.db.get_vlanquotas(context, filters=filters)
                if vlanquotas:
                    vlan_range = vlanquotas.split('-')
                    vlan_start = int(vlan_range[0])
                    vlan_end = int(vlan_range[1])
                    tot_vlans = []
                    u = 0
                    for u in range(vlan_start, vlan_end):
                        tot_vlans.append(u)

                    for n in nics:
                        net_id = n['net-id']
                        fliters = []
                        filters['tenant_id'] = [context.tenant_id]
                        filters['network_id'] = [net_id]
                        vlan_pairs = self.db.get_chain_appliance_map_instances(context,
                                                                     filters=filters)
                        assigned_vlans = []
                        for vp in vlan_pairs:
                            vlan_in = vp['vlan_in']
                            assigned_vlans.append(vlan_in)
                            vlan_out = vp['vlan_out']
                            assigned_vlans.append(vlan_out)
                        diff_vlans = sorted(
                            list(set(tot_vlans) - set(assigned_vlans)))
                        y = 0
                        vlan_in = 0
                        vlan_out = 0
                        for y in range(0, 2):
                            if y == 0:
                                #dir = 'ingress'
                                vlan_in = diff_vlans[0]

                            else:
                                #dir = 'egress'
                                vlan_out = diff_vlans[1]

                            #vpair.append(vlid)

                            if y > 0:
                                ###Insert Vlan Pairs in CRD...
                                appliance_instance_update_body = {
                                    'appliance_instance': {'network_id': net_id,
                                                           'vlan_in': vlan_in,
                                                           'vlan_out': vlan_out,
                                                           }
                                        }
                                #vlanpair = self.db.create_vlan_pair(context,
                                #                                    vlanpair_body)
                                v_new = self.db.update_chain_appliance_map_instance(context, appliance_instance_id,
                                                                          appliance_instance_update_body)
                                ###DELTA
                                data = {}
                                data = v_new
                                data.update({'operation' : 'update'})
                                delta={}
                                delta.update({'appliance_instances_delta':data})
                                result_delta = self.delta_db.create_appliance_instances_delta(context,delta)
                                ###DELTA
                                

                                ###Send Vlan Pairs to Relay Agent

                                #res = {'header': 'request',
                                #       'instance_uuid': instance_uuid,
                                #       'slug': 'vlanpair',
                                #       'vlanin': vlan_in,
                                #       'vlanout': vlan_out,
                                #       'version': '1.0',
                                #       'tenant_id': context.tenant_id}
                                #LOG.debug('^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                                #LOG.debug('VLAN Pair Message = %s' % str(res))
                                #LOG.debug('^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                                #self.send_vlancast(instance_uuid,
                                #                   {'config': res})

                            y += 1
            
            #config_handle_details = self.db.get_config_handle(context,
            #                                                  config_handle_id)
            #res = {'header': 'request',
            #       'config_handle_id': config_handle_id,
            #       'slug': config_handle_details['slug'],
            #       'version': '1.0',
            #       'tenant_id': config_handle_details['tenant_id']}
            #if config_handle_details['config_mode'] == 'NFV':
            #    str1 = self.send_cast(config_handle_id, {'config':res})
            #    pass

            count += 1
            #time.sleep(120)
        #LOG.debug("Returning ChainID - %s" % str(chain_id))    
        return chain_id

    @classmethod
    def send_rpc_msg(cls, logical_id, msg):
        #LOG.debug('In send_rpc_msg')
        driver = cls.get_instance()
        driver.send_cast(logical_id, msg)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def subnet_list(self, last_subnet, iters):
        subnets = []
        for i in xrange(1, (iters + 1)):
            xsubnet = socket.inet_aton(last_subnet)
            if ord(xsubnet[2]) < 254:
                next_subnet = xsubnet[:2] + chr(ord(xsubnet[2]) + 1) + xsubnet[
                    -1]
                next_subnet = socket.inet_ntoa(next_subnet)
                #print next_subnet
            else:
                next_subnet = xsubnet[0] + chr(ord(xsubnet[1]) + 1) + chr(0)\
                              + \
                              xsubnet[-1]
                next_subnet = socket.inet_ntoa(next_subnet)
                #print next_subnet

            subnets.append(next_subnet)
            last_subnet = next_subnet
        return subnets


def novaclient(context=None):
    if not context:

        return nova_client.Client(cfg.CONF.nscs_authtoken.admin_user,
                                  cfg.CONF.nscs_authtoken.admin_password,
                                  cfg.CONF.nscs_authtoken.admin_tenant_name,
                                  auth_url=cfg.CONF.nscs_authtoken.auth_url,
                                  service_type="compute")
    else:
        insecure = False
        auth_url = url_for(context, 'compute')
        #LOG.debug("##################################################")
        #LOG.debug(context.user_id)
        #LOG.debug(context.user_name)
        #LOG.debug(context.tenant_id)
        #LOG.debug(context.service_catalog)
        #LOG.debug(auth_url)
        #LOG.debug("##################################################")
        c = nova_client.Client(context.user_name,
                               context.auth_token,
                               project_id=context.tenant_id,
                               auth_url=auth_url,
                               insecure=insecure)
        c.client.auth_token = context.auth_token
        c.client.management_url = auth_url
        return c


def get_service_from_catalog(catalog, service_type):
    if catalog:
        for service in catalog:
            if service['type'] == service_type:
                return service
    return None


def url_for(context, service_type, admin=False, endpoint_type=None):
    endpoint_type = endpoint_type or 'publicURL'
    catalog = context.service_catalog
    service = get_service_from_catalog(catalog, service_type)
    if service:
        try:
            if admin:
                return service['endpoints'][0]['adminURL']
            else:
                return service['endpoints'][0][endpoint_type]
        except (IndexError, KeyError):
            raise q_exc.ServiceCatalogException(service_name=str(service_type))
    else:
        raise q_exc.ServiceCatalogException(service_name=str(service_type))


def crdclient(context=None):
    c = neutron_client.Client(token=context.auth_token,
                              endpoint_url=url_for(context, 'network'))
    return c
