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
    name = "addrule"
    verbose_name = _("Add Rule")
    url = "horizon:project:chainsets:addrule"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        chainset_id = self.table.kwargs['chainset_id']
        return reverse(self.url, args=(chainset_id,))


class Deleterule(tables.DeleteAction):
    data_type_singular = _("Rule")
    data_type_plural = _("Rules")

    def delete(self, request, rule_id):
        try:
            chainset_id = self.table.kwargs['chainset_id']
            api.sfc.rule_delete(request, chainset_id, rule_id)
            LOG.debug('Delete Rule %s successfully' % rule_id)
        except:
            msg = _('Failed to Delete Rule %s') % rule_id
            LOG.info(msg)
            chainset_id = self.table.kwargs['chainset_id']
            redirect = reverse('horizon:project:chainsets:detail',
                               args=[chainset_id])
            exceptions.handle(request, msg, redirect=redirect)


class Editrule(tables.LinkAction):
    name = "editrule"
    verbose_name = _("Edit Rule")
    url = "horizon:project:chainsets:editrule"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, rule):
        chainset_id = self.table.kwargs['chainset_id']
        return reverse(self.url, args=(chainset_id, rule.id))


def get_chain_link(datum):
    view = "horizon:project:chains:detail"
    if datum.chain_id:
        return reverse(view, args=(datum.chain_id,))
    else:
        return None


class LaunchChain(tables.LinkAction):
    name = "launch"
    verbose_name = _("Launch")
    url = "horizon:project:chainsets:launch"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, rule):
        chainset_id = self.table.kwargs['chainset_id']
        return reverse(self.url, args=(chainset_id, rule.id))


def get_rule_link(datum):
    view = "horizon:project:chainsets:ruledetail"
    if datum.chain_id:
        return reverse(view, args=(datum.chainset_id, datum.id))
    else:
        return None


class ChainrulesTable(tables.DataTable):

    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link=get_rule_link)
    chain_id = tables.Column("chain_id",
                             verbose_name=_("Chain"),
                             link=get_chain_link)

    class Meta:
        name = "chainrules"
        verbose_name = _("Chain Rules")
        table_actions = (AddRule, Deleterule)
        row_actions = (Editrule, Deleterule)
