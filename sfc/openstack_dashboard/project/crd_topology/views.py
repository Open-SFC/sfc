# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2013 NTT MCL Inc.
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

import json

from django.conf import settings  # noqa
from django.core.urlresolvers import reverse  # noqa
from django.core.urlresolvers import reverse_lazy  # noqa
from django.http import HttpResponse  # noqa
from django.views.generic import TemplateView  # noqa
from django.views.generic import View  # noqa

from openstack_dashboard import api
import uuid


class NetworkTopologyView (TemplateView):
    template_name = 'project/crd_topology/index.html'


class JSONView(View):

    def add_resource_url(self, view, resources):
        tenant_id = self.request.user.tenant_id
        for resource in resources:
            if (resource.get('tenant_id')
                    and tenant_id != resource.get('tenant_id')):
                continue
            resource['url'] = reverse(view, None, [str(resource['id'])])

    def _check_router_external_port(self, ports, router_id, network_id):
        for port in ports:
            if (port['network_id'] == network_id
                    and port['device_id'] == router_id):
                return True
        return False

    def get(self, request, *args, **kwargs):
        data = {}
        # Get nova data
        try:
            servers, more = api.nova.server_list(request)
        except Exception:
            servers = []
        console_type = getattr(settings, 'CONSOLE_TYPE', 'AUTO')
        if console_type == 'SPICE':
            console = 'spice'
        else:
            console = 'vnc'
        data['ports'] = []
        data['servers'] = [{'name': server.name,
                            'status': server.status,
                            'console': console,
                            'task': getattr(server, 'OS-EXT-STS:task_state'),
                            'id': server.id} for server in servers]
        self.add_resource_url('horizon:project:instances:detail',
                              data['servers'])

        # Get neutron data
        # if we didn't specify tenant_id, all networks shown as admin user.
        # so it is need to specify the networks. However there is no need to
        # specify tenant_id for subnet. The subnet which belongs to the public
        # network is needed to draw subnet information on public network.
        try:
            neutron_public_networks = api.neutron.network_list(
                request,
                **{'router:external': True})
            neutron_networks = api.neutron.network_list_for_tenant(
                request,
                request.user.tenant_id)
            neutron_ports = api.neutron.port_list(request)
            neutron_routers = api.neutron.router_list(
                request,
                tenant_id=request.user.tenant_id)
        except Exception:
            neutron_public_networks = []
            neutron_networks = []
            neutron_ports = []
            neutron_routers = []

        networks = [{'name': network.name,
                     'id': network.id,
                     'subnets': [{'cidr': subnet.cidr}
                                 for subnet in network.subnets],
                     'router:external': network['router:external']}
                    for network in neutron_networks]
        self.add_resource_url('horizon:project:networks:detail',
                              networks)
        # Add public networks to the networks list
        for publicnet in neutron_public_networks:
            found = False
            for network in networks:
                if publicnet.id == network['id']:
                    found = True
            if not found:
                try:
                    subnets = [{'cidr': subnet.cidr}
                               for subnet in publicnet.subnets]
                except Exception:
                    subnets = []
                networks.append({
                    'name': publicnet.name,
                    'id': publicnet.id,
                    'subnets': subnets,
                    'router:external': publicnet['router:external']})

        ###
        # Adding Switches to Networks list
        ###
        cluster_filters = {}
        cluster_filters['name'] = ['DefaultCluster']
        clusters = api.sfc.of_cluster_list(
            request,
            filters=cluster_filters)
        if clusters:
            cluster_id = clusters[0].id
            cluster_name = clusters[0].name

            ofcontrollers = api.sfc.of_controller_list(request, id=cluster_id)
            for controller in ofcontrollers:
                ofc_id = controller.id
                ofc_name = controller.name
                ofc_ipaddress = controller.ip_address
                neutron_routers.append({
                    'id': ofc_id,
                    #'name': ofc_name,
                    'name': 'OF Controller',
                    'status': None,
                    'external_gateway_info': None})
                compute_filters = {}
                compute_filters['status'] = ['Active']
                compute_nodes = api.sfc.compute_node_list(
                    request, filters=compute_filters)
                for switch in compute_nodes:
                    if switch.status == 'Active':
                        switch_id = switch.id
                        switch_name = switch.datapath_name
                        switch_datapath_id = switch.datapath_id
                        switch_ip_address = switch.ip_address
                        switch_port = switch.ovs_port
                        port_id = str(uuid.uuid4())
                        neutron_ports.append({
                            'id': 'fake_' + port_id,
                            'network_id': switch_id,
                            'device_id': ofc_id,
                            'fixed_ips': [],
                            'device_owner': 'compute:nova',
                            'status': 'DOWN'})

                        networks.append({
                            'name': 'OpenvSwitch - ' + switch_name + ' (' + switch.switch + ')',
                            'id': switch_id,
                            'subnets': [{'cidr': switch_ip_address}],
                            'router:external': False})
                        instance_filters = {}
                        instances = api.sfc.instance_list(
                            request, filters=instance_filters)
                        for instance in instances:
                            if instance.state == 'active' and instance.host == switch.switch:
                                # if instance.host == switch.switch:
                                port_id = str(uuid.uuid4())
                                neutron_ports.append({
                                    'id': 'fake_' + port_id,
                                    'network_id': switch_id,
                                    'device_id': instance.instance_id,
                                    'fixed_ips': [],
                                    'device_owner': 'compute:nova',
                                    'status': 'DOWN'})

        data['networks'] = sorted(networks,
                                  key=lambda x: x.get('router:external'),
                                  reverse=True)

        data['ports'] = [{'id': port['id'],
                          'network_id': port['network_id'],
                          'device_id': port['device_id'],
                          'fixed_ips': port['fixed_ips'],
                          'device_owner': port['device_owner'],
                          'status': port['status']
                          }
                         for port in neutron_ports]
        self.add_resource_url('horizon:project:networks:ports:detail',
                              data['ports'])

        data['routers'] = [{
            'id': router['id'],
            'name': router['name'],
            'status': router['status'],
            'external_gateway_info': router['external_gateway_info']}
            for router in neutron_routers]

        # user can't see port on external network. so we are
        # adding fake port based on router information
        for router in data['routers']:
            if router['status']:
                external_gateway_info = router['external_gateway_info']
                if not external_gateway_info:
                    continue
                external_network = external_gateway_info.get(
                    'network_id')
                if not external_network:
                    continue
                if self._check_router_external_port(data['ports'],
                                                    router['id'],
                                                    external_network):
                    continue
                fake_port = {'id': 'fake%s' % external_network,
                             'network_id': external_network,
                             'device_id': router['id'],
                             'fixed_ips': []}
                data['ports'].append(fake_port)

        self.add_resource_url('horizon:project:routers:detail',
                              data['routers'])
        json_string = json.dumps(data, ensure_ascii=False)
        with open('/tmp/srik.out', 'w+') as f:
            f.write(json_string)
            f.close()
        return HttpResponse(json_string, mimetype='text/json')
