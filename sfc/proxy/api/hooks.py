# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
#         Angus Salkeld <asalkeld@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import threading
from oslo_config import cfg
from oslo_i18n._i18n import _
from pecan import hooks

from sfc.crdclient.v2_0 import client as crdclient


crd_opts = [
        cfg.StrOpt('username',
            help=_("User name to use for CRD service access.")),
        cfg.StrOpt('password',
            secret=True,
            help=_('Password to use for CRD service access.')),
        cfg.StrOpt('tenant_name',
            help=_('Tenant ID to use for CRD service access.')),
        cfg.StrOpt('auth_url',
            help=_('Auth URL to use for CRD service access.')),
        ]

# Register the configuration options
cfg.CONF.register_opts(crd_opts, group="crd")


nova_opts = [
        cfg.StrOpt('username',
            help=_("User name to use for Nova service access.")),
        cfg.StrOpt('password',
            secret=True,
            help=_('Password to use for Nova service access.')),
        cfg.StrOpt('tenant_name',
            help=_('Tenant ID to use for Nova service access.')),
        cfg.StrOpt('auth_url',
            help=_('Auth URL to use for Nova service access.')),
        ]

# Register the configuration options
cfg.CONF.register_opts(nova_opts, group="nova")


neutron_opts = [
        cfg.StrOpt('username',
            help=_("User name to use for Neutron service access.")),
        cfg.StrOpt('password',
            secret=True,
            help=_('Password to use for Neutron service access.')),
        cfg.StrOpt('tenant_name',
            help=_('Tenant ID to use for Neutron service access.')),
        cfg.StrOpt('auth_url',
            help=_('Auth URL to use for Neutron service access.')),
        ]

# Register the configuration options
cfg.CONF.register_opts(neutron_opts, group="neutron")


class ConfigHook(hooks.PecanHook):
    """Attach the configuration object to the request
    so controllers can get to it.
    """

    def __init__(self):
        self.crdclient = crdclient.Client(username=cfg.CONF.crd.username,
                                          password=cfg.CONF.crd.password,
                                          tenant_name=
                                          cfg.CONF.crd.tenant_name,
                                          auth_url=cfg.CONF.crd.auth_url)

    def before(self, state):
        state.request.cfg = cfg.CONF
        state.request.crdclient = self.crdclient


class TranslationHook(hooks.PecanHook):

    def __init__(self):
        # Use thread local storage to make this thread safe in situations
        # where one pecan instance is being used to serve multiple request
        # threads.
        self.local_error = threading.local()
        self.local_error.translatable_error = None

    def after(self, state):
        if hasattr(state.response, 'translatable_error'):
            self.local_error.translatable_error = (
                state.response.translatable_error)
