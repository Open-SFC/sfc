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

INDEX_URL = "horizon:projects:chains:index"


class UpdateApplianceMapConfigAction(workflows.MembershipAction):

    def __init__(self, request, *args, **kwargs):
        super(UpdateApplianceMapConfigAction, self).__init__(request,
                                                             *args,
                                                             **kwargs)
        err_msg = _('Unable to retrieve Configurations list. '
                    'Please try again later.')
        context = args[0]
        appliance_map_id = context.get('appliance_map_id', '')
        chain_id = context.get('chain_id', '')
        tenant_id = self.request.user.tenant_id

        default_role_name = self.get_default_role_field_name()
        self.fields[default_role_name] = forms.CharField(required=False)
        self.fields[default_role_name].initial = 'member'

        # Get list of available security groups
        all_configs = []
        try:
            all_configs = api.sfc.config_handle_list_for_tenant(
                request, tenant_id)
        except:
            exceptions.handle(request, err_msg)
        configs_list = [(config.id, config.name) for config in all_configs]

        appliance_map_configs = []
        try:
            appliance_map_details = api.sfc.appliance_map_get(request,
                                                              chain_id,
                                                              appliance_map_id)
            appliance_map_configs = appliance_map_details.appliance_map_confs
        except Exception:
            exceptions.handle(request, err_msg)

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)
        self.fields[field_name].choices = configs_list
        self.fields[field_name].initial = [config['id']
                                           for config in appliance_map_configs]

    def handle(self, request, data):
        appliance_map_id = data['appliance_map_id']
        chain_id = data['chain_id']

        # update category security groups
        wanted_configs = set(data['wanted_configs'])
        try:
            appliance_map_details = api.sfc.appliance_map_get(request,
                                                              chain_id,
                                                              appliance_map_id)
            current_configs = appliance_map_details['appliance_map_confs']
        except:
            exceptions.handle(request, _("Couldn't get current Configuration "
                                         "list for appliance_map %s."
                                         % appliance_map_id))
            return False

        current_config_names = set(map(lambda g: g['id'], current_configs))
        configs_to_add = wanted_configs - current_config_names
        configs_to_remove = current_config_names - wanted_configs

        num_configs_to_modify = len(configs_to_add | configs_to_remove)
        try:
            for config in configs_to_add:
                config_handle_details = api.sfc.config_handle_get(request,
                                                                  config)
                api.sfc.appliance_map_conf_create(request,
                                                  chain_id,
                                                  appliance_map_id,
                                                  networkfunction_id=config_handle_details[
                                                      'networkfunction_id'],
                                                  config_handle_id=config)
                num_configs_to_modify -= 1
            for config in configs_to_remove:
                appliance_configs = api.sfc.appliance_map_conf_list(request,
                                                                    chain_id,
                                                                    appliance_map_id,
                                                                    config_handle_id=config)
                for appliance_config in appliance_configs:
                    api.sfc.appliance_map_conf_delete(request, chain_id, appliance_map_id,
                                                      appliance_config['id'])
                num_configs_to_modify -= 1
        except Exception:
            exceptions.handle(request, _('Failed to modify %d chain appliance map '
                                         'Configurations.'
                                         % num_configs_to_modify))
            return False

        return True

    class Meta:
        name = _("Configurations")
        slug = "update_configs"


class UpdateApplianceMapConfig(workflows.UpdateMembersStep):
    action_class = UpdateApplianceMapConfigAction
    help_text = _("From here you can add and remove configurations to "
                  "this project from the list of available configurations.")
    available_list_title = _("All Configurations")
    members_list_title = _("Configurations")
    no_available_text = _("No Configurations found.")
    no_members_text = _("No Configurations enabled.")
    show_roles = False
    depends_on = ("chain_id", "appliance_map_id",)
    contributes = ("wanted_configs",)

    def contribute(self, data, context):
        if data:
            member_field_name = self.get_member_field_name('member')
            context['wanted_configs'] = data.get(member_field_name, [])
        return context


class UpdateApplianceMapInfoAction(workflows.Action):
    chain_id = forms.CharField(widget=forms.HiddenInput())
    appliance_map_id = forms.CharField(label=_("Chain Appliance Map ID"),
                                       widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    instance_uuid = forms.CharField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(max_length=255,
                           label=_("Name"),
                           required=False)
    appliance_id = forms.ChoiceField(label=_("Appliance"),
                                     help_text=_("Select an Appliance."),
                                     required=True)
    sequence_number = forms.IntegerField(label=_("Boot order"),
                                         min_value=1,
                                         initial=1)

    def handle(self, request, data):
        try:
            appliance_map = api.sfc.appliance_map_modify(request, data['chain_id'],
                                                         data[
                                                             'appliance_map_id'],
                                                         name=data['name'],
                                                         appliance_id=data[
                                                             'appliance_id'],
                                                         sequence_number=data['sequence_number'])
        except:
            exceptions.handle(request, ignore=True)
            return False
        return True

    def populate_appliance_id_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            appliances = api.sfc.appliance_list_for_tenant(request, tenant_id)
            appliance_list = [(appliance.id, "%s" % appliance.name)
                              for appliance in appliances]
        except:
            appliance_list = []
            exceptions.handle(request,
                              _('Unable to retrieve Appliance List.'))
        return sorted(appliance_list)

    class Meta:
        name = _("Info")
        slug = 'appliance_map_info'
        help_text = _(
            "From here you can edit the Chain Appliance Map details.")


class UpdateApplianceMapInfo(workflows.Step):
    action_class = UpdateApplianceMapInfoAction
    depends_on = ("appliance_map_id",)
    contributes = ("name", "sequence_number", "appliance_id")


class UpdateChainApplianceMap(workflows.Workflow):
    slug = "update_chain_appliance_map"
    name = _("Edit Chain Appliance Map")
    finalize_button_name = _("Save")
    success_message = _('Modified Chain Appliance Map "%s".')
    failure_message = _('Unable to modify Chain Appliance Map "%s".')
    success_url = "horizon:project:chains:detail"
    default_steps = (UpdateApplianceMapInfo,
                     UpdateApplianceMapConfig)

    def format_status_message(self, message):
        return message % self.context.get('name', 'unknown appliance map')

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.context.get('chain_id'), ))