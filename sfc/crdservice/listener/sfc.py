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

from novaclient.v1_1 import client as nova_client
from oslo.config import cfg
import socket
import json
from nscs.crdservice import context as crd_context
from nscs.crdservice.openstack.common import context
from nscs.crdservice.openstack.common import log as logging
from nscs.crdservice.openstack.common import rpc
from nscs.crdservice.openstack.common.rpc import dispatcher
from nscs.crdservice.openstack.common.rpc import proxy


LOG = logging.getLogger(__name__)


class SFCListener(proxy.RpcProxy):
    """
    Keep listening on SFC and CRD-Consumer Notifications
    """
    RPC_API_VERSION = '1.0'

    def __init__(self):
        self.context = crd_context.Context('crd', 'crd',
                                           is_admin=True)
        polling_interval = 2
        reconnect_interval = 2
        self.rpc = True

        self.polling_interval = polling_interval
        self.reconnect_interval = reconnect_interval
        if self.rpc:
            self.setup_rpc()
        LOG.info("SFC RPC Listener initialized successfully, now running...")


    def setup_rpc(self):
        self.host = self.get_hostname()
        self.listen_topic = "sfc-consume"
        self.consumer_listener_topic = "crd-listener"

        # CRD RPC Notification
        self.listen_context = context.RequestContext('crd', 'crd',
                                                     is_admin=False)

        # Handle updates from service
        self.dispatcher = self.create_rpc_dispatcher()

        # Define the listening consumers for the agent
        self.listen_conn = rpc.create_connection(new=True)
        LOG.debug(_("Creating CONSUMER with topic %s....\n"),
                  self.listen_topic)
        self.listen_conn.join_consumer_pool(self.process_event,
                                            self.listen_topic,
                                            'notifications.info',
                                            'nova')
        self.listen_conn.join_consumer_pool(self.process_event,
                                            self.listen_topic, 'sfc-consume',
                                            'crd')
        self.listen_conn.consume_in_thread()

        self.consumer_conn = rpc.create_connection(new=True)
        self.consumer_conn.create_consumer(self.consumer_listener_topic,
                                           self.dispatcher, fanout=False)
        self.consumer_conn.consume_in_thread()

        # self.cast(self.listen_context, self.make_msg('check_compute_status',
        #                                              payload={
        #                                              'Status': 'Active'}))

    @staticmethod
    def get_hostname():
        return "%s" % socket.gethostname()
    
    def create_rpc_dispatcher(self):
        """Get the rpc dispatcher for this manager.

        If a manager would like to set an rpc API version, or support more than
        one class as the target of rpc messages, override this method.
        """
        return dispatcher.RpcDispatcher([self])

    def process_event(self, message_data):
        event_type = message_data.get('event_type', None)
        method = message_data.get('method', None)
	foramted_txt = json.dumps(message_data, indent=4, separators=(',', ': '))
	#LOG.debug(_("Message Delta %s\n"), str(foramted_txt))
        if event_type is not None:
            payload = message_data.get('payload', {})
            if event_type == 'compute.instance.update' and  payload['state'] == 'deleted':
                host_node = payload['host']
                instance_id = payload['instance_id']
                tenant_id = payload['tenant_id']
                if 'metadata' in payload:
                    if ('vmtype' in payload['metadata']) and \
                        (payload['metadata']['vmtype'] == 'service'):
                        self.delete_chain_appliance_instance(self.context,
                                                             instance_id)
                        self.send_inst_delete_driver(instance_id, tenant_id,
                                                     host_node)
                        


    def novaclient(self):
        return  nova_client.Client(cfg.CONF.CRDNOVACLIENT.admin_user,
                                   cfg.CONF.CRDNOVACLIENT.admin_password,
                                   cfg.CONF.CRDNOVACLIENT.admin_tenant_name,
                                   auth_url=cfg.CONF.CRDNOVACLIENT.auth_url,
                                   service_type="compute")
    
