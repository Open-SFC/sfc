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
from horizon import workflows
from horizon import tabs
from .workflows import AddRule
from .forms import Editrule, Launchchain
from .tabs import RuleDetailTabs

LOG = logging.getLogger(__name__)


class Addruleview(workflows.WorkflowView):
    workflow_class = AddRule
    template_name = 'project/chainsets/rules/addrule.html'
    success_url = 'horizon:project:chainsets:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chainset_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                chainset_id = self.kwargs["chainset_id"]
                self._object = api.sfc.chainset_get(self.request,
                                                    chainset_id)
            except:
                redirect = reverse('horizon:project:chainsets:index')
                msg = _("Unable to retrieve Chainset.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(Addruleview, self).get_context_data(**kwargs)
        context['chainset'] = self.get_object()
        return context

    def get_initial(self):
        chainset = self.get_object()
        return {"chainset_id": self.kwargs['chainset_id'],
                "chainset_name": chainset.name}


class EditruleView(forms.ModalFormView):
    form_class = Editrule
    template_name = 'project/chainsets/rules/update.html'
    context_object_name = 'rule'
    success_url = 'horizon:project:chainsets:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chainset_id'],))

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            rule_id = self.kwargs['rule_id']
            chainset = self.kwargs['chainset_id']
            try:
                self._object = api.sfc.rule_get(
                    self.request, chainset, rule_id)
            except:
                redirect = reverse('horizon:project:chainsets:index')
                msg = _('Unable to Rule')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        rule = self.get_object()
        context = super(EditruleView, self).get_context_data(**kwargs)
        context["chainset_id"] = self.kwargs['chainset_id']
        context["rule_id"] = self.kwargs['rule_id']
        return context

    def get_initial(self):
        rule = self.get_object()
        return {'chainset_id': self.kwargs['chainset_id'],
                'rule_id': self.kwargs['rule_id'],
                'name': rule['name'],
                'chain_id': rule['chain_id']}


class LaunchChainView(forms.ModalFormView):
    form_class = Launchchain
    template_name = 'project/chainsets/rules/launch.html'
    context_object_name = 'rule'
    success_url = reverse_lazy('horizon:project:instances:index')

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            rule_id = self.kwargs['rule_id']
            chainset = self.kwargs['chainset_id']
            try:
                self._object = api.sfc.rule_get(
                    self.request, chainset, rule_id)
            except:
                redirect = reverse('horizon:project:chainsets:index')
                msg = _('Unable to Rule')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        rule = self.get_object()
        context = super(LaunchChainView, self).get_context_data(**kwargs)
        context["chainset_id"] = self.kwargs['chainset_id']
        context["rule_id"] = self.kwargs['rule_id']
        return context

    def get_initial(self):
        rule = self.get_object()
        return {'chainset_id': self.kwargs['chainset_id'],
                'rule_id': self.kwargs['rule_id']}


class RuleDetailView(tabs.TabView):
    tab_group_class = RuleDetailTabs
    template_name = 'project/chainsets/rules/detail.html'
