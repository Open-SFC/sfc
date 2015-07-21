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

from django import template
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import tables


LOG = logging.getLogger(__name__)


class AddRule(tables.LinkAction):
    name = "bypassrules"
    verbose_name = _("Add Bypass Rule")
    url = "horizon:project:chains:bypassrules"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id,))


class Deletel2rule(tables.DeleteAction):
    data_type_singular = _("Rule")
    data_type_plural = _("Rules")

    def delete(self, request, rule_id):
        try:
            chain_id = self.table.kwargs['chain_id']
            api.sfc.bypass_rule_delete(request, chain_id, rule_id)
            LOG.debug('Delete L2 Rule %s successfully' % rule_id)
        except:
            msg = _('Failed to Delete L2 Rule %s') % rule_id
            LOG.info(msg)
            chain_id = self.table.kwargs['chain_id']
            redirect = reverse('horizon:project:chains:detail',
                               args=[chain_id])
            exceptions.handle(request, msg, redirect=redirect)


class Editl2rule(tables.LinkAction):
    name = "editl2rule"
    verbose_name = _("Edit l2 Rule")
    url = "horizon:project:chains:editl2rule"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, rule):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id, rule.id))


def get_bypassrule_link(datum):
    view = "horizon:project:chains:ruledetail"
    if datum.chain_id:
        return reverse(view, args=(datum.chain_id, datum.id))
    else:
        return None


class ChainBypassTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link=get_bypassrule_link)
    nwservice_names = tables.Column("nwservice_names",
                                    verbose_name=_("Appliances"))

    class Meta:
        name = "bypassrules"
        verbose_name = _("L2Chain - Bypass Rules")
        table_actions = (AddRule, Deletel2rule)
        row_actions = (Deletel2rule, Editl2rule)