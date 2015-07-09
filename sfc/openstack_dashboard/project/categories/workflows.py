# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
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


from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from horizon import exceptions
from horizon import workflows
from horizon import forms
from horizon import messages

from openstack_dashboard import api

INDEX_URL = "horizon:projects:categories:index"


class UpdateNFAction(workflows.MembershipAction):

    def __init__(self, request, *args, **kwargs):
        super(UpdateNFAction, self).__init__(request,
                                             *args,
                                             **kwargs)
        err_msg = _('Unable to retrieve network function list. '
                    'Please try again later.')
        context = args[0]
        category_id = context.get('category_id', '')
        tenant_id = self.request.user.tenant_id

        default_role_name = self.get_default_role_field_name()
        self.fields[default_role_name] = forms.CharField(required=False)
        self.fields[default_role_name].initial = 'member'

        # Get list of available security groups
        all_nfs = []
        try:
            all_nfs = api.sfc.networkfunction_list_for_tenant(
                request, tenant_id)
        except:
            exceptions.handle(request, err_msg)
        nfs_list = [(nf.id, nf.name) for nf in all_nfs]

        category_nfs = []
        try:
            category_details = api.sfc.category_get(request,
                                                    category_id)
            category_nfs = category_details.category_networkfunctions
        except Exception:
            exceptions.handle(request, err_msg)

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)
        self.fields[field_name].choices = nfs_list
        self.fields[field_name].initial = [nf['id']
                                           for nf in category_nfs]

    def handle(self, request, data):
        category_id = data['category_id']

        # update category security groups
        wanted_nfs = set(data['wanted_nfs'])
        try:
            category_details = api.sfc.category_get(request,
                                                    category_id)
            current_nfs = category_details.category_networkfunctions
        except:
            exceptions.handle(request, _("Couldn't get current network function "
                                         "list for category %s."
                                         % category_id))
            return False

        current_nf_names = set(map(lambda g: g['id'], current_nfs))
        nfs_to_add = wanted_nfs - current_nf_names
        nfs_to_remove = current_nf_names - wanted_nfs

        num_nfs_to_modify = len(nfs_to_add | nfs_to_remove)
        try:
            for nf in nfs_to_add:
                api.sfc.category_networkfunction_create(request,
                                                        category_id,
                                                        networkfunction_id=nf)
                num_nfs_to_modify -= 1
            for nf in nfs_to_remove:
                api.sfc.category_networkfunction_delete(request,
                                                        category_id,
                                                        nf)
                num_nfs_to_modify -= 1
        except Exception:
            exceptions.handle(request, _('Failed to modify %d category '
                                         'network functions.'
                                         % num_nfs_to_modify))
            return False

        return True

    class Meta:
        name = _("Network Functions")
        slug = "update_nfs"


class UpdateNF(workflows.UpdateMembersStep):
    action_class = UpdateNFAction
    help_text = _("From here you can add and remove network functions to "
                  "this project from the list of available network functions.")
    available_list_title = _("All Network Functions")
    members_list_title = _("Network Functions")
    no_available_text = _("No Network Functions found.")
    no_members_text = _("No Network Functions enabled.")
    show_roles = False
    depends_on = ("category_id",)
    contributes = ("wanted_nfs",)

    def contribute(self, data, context):
        if data:
            member_field_name = self.get_member_field_name('member')
            context['wanted_nfs'] = data.get(member_field_name, [])
        return context


class UpdateCategoryInfoAction(workflows.Action):
    name = forms.CharField(required=True)
    description = forms.CharField(required=True)

    def handle(self, request, data):
        try:
            api.sfc.category_modify(request,
                                    data['category_id'],
                                    name=data['name'],
                                    description=data['description'],)
        except:
            exceptions.handle(request, ignore=True)
            return False
        return True

    class Meta:
        name = _("Info")
        slug = 'category_info'
        help_text = _("From here you can edit the category details.")


class UpdateCategoryInfo(workflows.Step):
    action_class = UpdateCategoryInfoAction
    depends_on = ("category_id",)
    contributes = ("name", "description", )


class UpdateCategory(workflows.Workflow):
    slug = "update_category"
    name = _("Edit Category")
    finalize_button_name = _("Save")
    success_message = _('Modified category "%s".')
    failure_message = _('Unable to modify category "%s".')
    success_url = "horizon:project:categories:index"
    default_steps = (UpdateCategoryInfo,
                     UpdateNF)

    def format_status_message(self, message):
        return message % self.context.get('name', 'unknown category')
