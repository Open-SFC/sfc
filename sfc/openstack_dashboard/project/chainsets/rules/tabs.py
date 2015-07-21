# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 NEC Corporation
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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import tabs


LOG = logging.getLogger(__name__)


class RuleOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/chainsets/rules/_detail_overview.html"

    def get_context_data(self, request):
        chainset_id = self.tab_group.kwargs['chainset_id']
        rule_id = self.tab_group.kwargs['rule_id']
        try:
            rule = api.sfc.rule_get(self.request, chainset_id, rule_id)
        except:
            redirect = reverse('horizon:project:chainsets:rules')
            msg = _('Unable to retrieve Rule Details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'rule': rule,
                'chainset_id': chainset_id}


class RuleDetailTabs(tabs.TabGroup):
    slug = "rule_details"
    tabs = (RuleOverviewTab,)
