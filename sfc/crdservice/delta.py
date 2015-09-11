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
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import context

from cns.crdservice.db import delta
from cns.crdservice.db import network
from cns.crdservice.db import nova



import re
import socket
import time

LOG = logging.getLogger(__name__)

class CnsDelta(object):
    """
    Handling Create delta and Get Difference 
    """
    def __init__(self):
	self.deltadb = delta.CnsDeltaDb()
	self.networkdb = network.CrdNetworkDb()
	self.novadb = nova.NovaDb()
	
	
	
    def create_network_delta(self, context, network):
        network_delta = self.deltadb.create_network_delta(context, network)
        return network_delta
            
    def create_subnet_delta(self, context,subnet):
        subnet_delta = self.deltadb.create_subnet_delta(context, subnet)
        return subnet_delta
        
    def create_port_delta(self, context, port):
        port_delta = self.deltadb.create_port_delta(context, port)
        return port_delta
        
    def create_instance_delta(self,context, instance):
        instance_delta = self.deltadb.create_instance_delta(context, instance)
        return instance_delta
            
    def create_compute_delta(self, context, compute):
        compute_delta = self.deltadb.create_compute_delta(context, compute)
        return compute_delta
    
    def create_nwport_delta(self, context, nwport):
        nwport_delta = self.deltadb.create_nwport_delta(context, nwport)
        return nwport_delta
    
       
        
    def cns_init(self, ctx, version,hostname):
        delta={}
        if version > 0:
            pass
                
        elif version == 0:
            #Network Delta
            i = 0
            fields = []
            fields=['runtime_version']
	    current_version = 0
            ver = self.deltadb.get_versions(ctx, filters=None, fields=fields)
	    if ver:
		current_version = max(ver)['runtime_version']
		LOG.debug(_("Runtime Version = %s"),str(current_version))
            #current_version = 100
            network_diff = self.networkdb.get_networks(ctx, filters=None, fields=None)
            for network in network_diff :
                network.update({'operation':'create','version_id':current_version})
                network_message={}
                network_message.update({'method':'create_virtual_network','payload':network})
                delta[i] = network_message
                i = i+1
            #Subnet Delta
            subnet_diff = self.networkdb.get_subnets(ctx, filters=None, fields=None)
            for subnet in subnet_diff :
                subnet.update({'operation':'create','version_id':current_version})
                subnet_message={}
                subnet_message.update({'method':'create_subnet','payload':subnet})
                delta[i] = subnet_message
                i = i+1
            #Compute Nodes Delta
            compute_diff = self.novadb.get_computes(ctx, filters=None, fields=None)
            for compute in compute_diff :
                compute.update({'operation':'create','version_id':current_version})
                compute_message={}
                compute_message.update({'method':'create_datapath','payload':compute})
                delta[i] = compute_message
                i = i+1
            #NWPORTS Delta
            nwport_diff = self.novadb.get_nwports(ctx, filters=None, fields=None)
            for nwport in nwport_diff :
                nwport.update({'operation':'create','version_id':current_version})
                nwport_message={}
                nwport_message.update({'method':'create_nwport','payload':nwport})
                delta[i] = nwport_message
                i = i+1
	    
	    #Instances Delta
            instance_diff = self.novadb.get_instances(ctx, filters=None, fields=None)
            for instance in instance_diff :
                instance.update({'operation':'create','version_id':current_version})
                instance_message={}
                instance_message.update({'method':'create_instance','payload':instance})
                delta[i] = instance_message
                i = i+1
            
            #Port Delta
            port_diff = self.networkdb.get_ports(ctx, filters=None, fields=None)
            for port in port_diff :
                port.update({'operation':'create','version_id':current_version})
                port_message={}
                port_message.update({'method':'create_port','payload':port})
                delta[i] = port_message
                i = i+1
		
	    
            
        LOG.debug(_("Delta to consumer = %s"),str(delta))
        return delta
        
        
        
        
        
    