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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import tabs


LOG = logging.getLogger(__name__)


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/appliances/_detail_overview.html"

    def get_context_data(self, request):
        appliance_id = self.tab_group.kwargs['appliance_id']
        try:
            appliance = api.sfc.appliance_get(self.request, appliance_id)
            appliance.category = api.sfc.category_get(self.request,
                                                      appliance.category_id)
            appliance.vendor = api.sfc.vendor_get(self.request,
                                                  appliance.vendor_id)
            appliance.full_flavor = api.nova.flavor_get(self.request,
                                                        appliance.flavor_id)
            appliance.security_group = api.network.security_group_get(
                self.request, appliance.security_group_id)
            appliance.glance_image = api.glance.image_get(self.request,
                                                          appliance.image_id)

        except:
            redirect = reverse('horizon:project:appliances:index')
            msg = _('Unable to retrieve appliance map details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'appliance': appliance}


class ImageDetailTabs(tabs.TabGroup):
    slug = "appliance_details"
    tabs = (OverviewTab,)
