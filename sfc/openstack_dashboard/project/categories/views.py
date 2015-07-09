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
Views for managing Crd Categories.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import workflows
from .forms import CreateCategory, UpdateCategory
from .tables import CategoriesTable
from .workflows import UpdateCategory


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = CategoriesTable
    template_name = 'project/categories/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            categories = api.sfc.category_list_for_tenant(self.request,
                                                          tenant_id)

        except:
            categories = []
            msg = _('Category list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in categories:
            n.set_id_as_name_if_empty()
        return categories


class CreateCategoryView(forms.ModalFormView):
    form_class = CreateCategory
    template_name = 'project/categories/create.html'
    success_url = reverse_lazy('horizon:project:categories:index')


class UpdateCategoryView(workflows.WorkflowView):
    workflow_class = UpdateCategory
    template_name = 'project/categories/update.html'
    success_url = reverse_lazy("horizon:project:categories:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateCategoryView, self).get_context_data(**kwargs)
        context["category_id"] = self.kwargs['category_id']
        return context

    def get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            category_id = self.kwargs['category_id']
            try:
                self._object = api.sfc.category_get(self.request, category_id)
            except:
                redirect = reverse("horizon:project:categories:index")
                msg = _('Unable to retrieve Category details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_initial(self):
        initial = super(UpdateCategoryView, self).get_initial()
        initial.update({'category_id': self.kwargs['category_id'],
                        'name': getattr(self.get_object(), 'name', '',),
                        'description': getattr(self.get_object(), 'description', '',)})
        return initial
