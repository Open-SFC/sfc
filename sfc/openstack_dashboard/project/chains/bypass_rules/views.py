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

"""
Views for managing Crd Chains.
"""
import logging

from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon import workflows
from .workflows import Addl2Rule
from .forms import Editl2rule
from .tabs import RuleDetailTabs

LOG = logging.getLogger(__name__)


class Editl2ruleView(forms.ModalFormView):
    form_class = Editl2rule
    template_name = 'project/chains/bypass_rules/update.html'
    context_object_name = 'rule'
    success_url = 'horizon:project:chains:bypass'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chain_id'],))

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            rule_id = self.kwargs['rule_id']
            chain = self.kwargs['chain_id']
            try:
                self._object = api.sfc.bypass_rule_get(
                    self.request, chain, rule_id)
            except:
                redirect = reverse('horizon:project:chains:index')
                msg = _('Unable to l2 Rule')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        rule = self.get_object()
        context = super(Editl2ruleView, self).get_context_data(**kwargs)
        context["chain_id"] = self.kwargs['chain_id']
        context["rule_id"] = self.kwargs['rule_id']
        return context

    def get_initial(self):
        rule = self.get_object()
        return {'chain_id': self.kwargs['chain_id'],
                'rule_id': self.kwargs['rule_id'],
                'name': rule['name']}

class Addl2ruleview(workflows.WorkflowView):
    workflow_class = Addl2Rule
    template_name = 'project/chains/bypass_rules/addrule.html'
    success_url = 'horizon:project:chains:bypass'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chain_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                chain_id = self.kwargs["chain_id"]
                self._object = api.sfc.chain_get(self.request,
                                                 chain_id)
            except:
                redirect = reverse('horizon:project:chains:index')
                msg = _("Unable to retrieve Chainset.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(Addl2ruleview, self).get_context_data(**kwargs)
        context['chain'] = self.get_object()
        return context

    def get_initial(self):
        chain = self.get_object()
        return {"chain_id": self.kwargs['chain_id'],
                "chain_name": chain.name}

class RuleDetailView(tabs.TabView):
    tab_group_class = RuleDetailTabs
    template_name = 'project/chains/bypass_rules/detail.html'
