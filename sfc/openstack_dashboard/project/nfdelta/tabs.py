# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
# Copyright 2012 OpenStack LLC
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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import messages
from horizon import tabs

from openstack_dashboard import api

from .networkfunctions.tables import NetworkFunctionTable


class NetworkFunctionsTab(tabs.Tab):
    name = _("Network Functions")
    slug = "networkfunctions_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(self.request, 'networkfunctions')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])

        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class CategoriesTab(tabs.Tab):
    name = _("Categories")
    slug = "categories_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(self.request, 'categories')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])
        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class CatnfTab(tabs.Tab):
    name = _("Category Network Functions")
    slug = "category_networkfunctions_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(
                self.request, 'category_networkfunctions')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])
        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class VendorsTab(tabs.Tab):
    name = _("Vendors")
    slug = "vendors_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(self.request, 'vendors')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])
        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class AppliancesTab(tabs.Tab):
    name = _("Appliances")
    slug = "appliances_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(self.request, 'appliances')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])
        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class ChainsTab(tabs.Tab):
    name = _("Chains")
    slug = "chains_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(self.request, 'chains')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])
        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class ChainappliancesTab(tabs.Tab):
    name = _("Chain Appliances")
    slug = "chain_appliances_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(self.request, 'chain_appliances')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])
        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class ChainmapsTab(tabs.Tab):
    name = _("Chainmaps")
    slug = "chainmaps_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(self.request, 'chainmaps')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])
        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class ChainrulesTab(tabs.Tab):
    name = _("Chainrules")
    slug = "chainrules_tab"
    template_name = "project/nfdelta/_detail_overview.html"

    def get_context_data(self, request):
        try:
            delta = api.sfc.nsdelta_get(self.request, 'chainrules')
            delta_array = delta.delta
            delta_array = sorted(delta_array, key=lambda k: k['version_id'])
        except:
            redirect = reverse('horizon:project:nfdelta:index')
            msg = _('Unable to retrieve nfdelta details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'delta_array': delta_array}


class DeltaTabs(tabs.TabGroup):
    slug = "delta_tabs"
    tabs = (NetworkFunctionsTab, CategoriesTab, VendorsTab, AppliancesTab, ChainsTab,
            ChainappliancesTab, ChainmapsTab, ChainrulesTab)
    #sticky = True
