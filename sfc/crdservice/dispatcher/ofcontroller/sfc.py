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
from nscs.crdservice import context as crd_context
from nscs.crdservice.openstack.common import rpc
from nscs.crdservice.openstack.common.rpc import dispatcher
from nscs.crdservice.openstack.common.rpc import proxy

import re
import socket
import time

LOG = logging.getLogger(__name__)


class SfcDispatcher(object):
    """
    Handling Sending Notification to OF COntroller CRD Cosumer
    """
    def send_fanout(self, context, method, payload):
        LOG.info(_("Payload in Send Fanout %s\n"), payload)
        consumer_topic = "crd-consumer"
        self.fanout_cast(context, self.make_msg(method, payload=payload), consumer_topic, version=self.RPC_API_VERSION)