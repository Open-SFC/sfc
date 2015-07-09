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
from django.utils.translation import ugettext as _

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import workflows
#from horizon.utils import fields


LOG = logging.getLogger(__name__)


class CreateImageInfoAction(workflows.Action):
    form_factor_type = (
        ("", _("Select")),
        ("Virtual", _("Virtual")),
        ("Physical", _("Physical")),
    )
    
    appliance_type = (
        ("", _("Select")),
        ("l2", _("L2")),
        ("l3", _("L3")),
    )

    appliance_name = forms.CharField(max_length=255,
                                     label=_("Appliance Name"))
    appliance_type = forms.ChoiceField(label=_("Appliance Type"),
                                             required=True,
                                             choices=appliance_type)
    image_id = forms.ChoiceField(label=_("Image"))
    flavor = forms.ChoiceField(label=_("Flavor"),
                               help_text=_("Size of image to launch."))
    security_group = forms.ChoiceField(label=_("Security Group"))
    category = forms.ChoiceField(label=_("Category"),
                                 help_text=_("To which Category it belongs."))
    vendor = forms.ChoiceField(label=_("Vendor"),
                               help_text=_("Who is the Vendor."))
    form_factor_type = forms.ChoiceField(label=_("Form Factor Type"),
                                         required=True,
                                         choices=form_factor_type)
    config_handle_id = forms.ChoiceField(label=_("Config Handles"),
                                         required=True,
                                         help_text=_("Map these Config"
                                                     "Handles"))

    class Meta:
        name = ("Details")
        help_text = _("From here you can map image to Category & Vendors.\n")

    def _get_available_images(self, request, context):
        project_id = context.get('project_id', None)
        if not hasattr(self, "_public_images"):
            public = {"is_public": True,
                      "status": "active"}
            try:
                public_images, _more, prev = api.glance.image_list_detailed(request,
                                                                            filters=public)
            except:
                public_images = []
                exceptions.handle(request,
                                  _("Unable to retrieve public images."))
            self._public_images = public_images

        # Preempt if we don't have a project_id yet.
        if project_id is None:
            setattr(self, "_images_for_%s" % project_id, [])

        if not hasattr(self, "_images_for_%s" % project_id):
            owner = {"property-owner_id": project_id,
                     "status": "active"}
            try:
                owned_images, _more, prev = api.glance.image_list_detailed(request,
                                                                           filters=owner)
            except:
                exceptions.handle(request,
                                  _("Unable to retrieve images for "
                                    "the current project."))
            setattr(self, "_images_for_%s" % project_id, owned_images)

        owned_images = getattr(self, "_images_for_%s" % project_id)
        images = owned_images + self._public_images

        # Remove duplicate images
        image_ids = []
        final_images = []
        for image in images:
            if image.id not in image_ids:
                image_ids.append(image.id)
                final_images.append(image)
        return [image for image in final_images
                if image.container_format not in ('aki', 'ari')]

    def populate_image_id_choices(self, request, context):
        images = self._get_available_images(request, context)
        choices = [(image.id, image.name)
                   for image in images
                   if image.properties.get("servicevm", '') == "yes"]

        if choices:
            choices.insert(0, ("", _("Select Image")))
        else:
            choices.insert(0, ("", _("No images available.")))
        return choices

    def populate_flavor_choices(self, request, context):
        try:
            flavors = api.nova.flavor_list(request)
            flavor_list = [(flavor.id, "%s" % flavor.name)
                           for flavor in flavors]
        except:
            flavor_list = []
            exceptions.handle(request,
                              _('Unable to retrieve instance flavors.'))
        choices = sorted(flavor_list)
        if choices:
            choices.insert(0, ("", _("Select Flavour")))
        else:
            choices.insert(0, ("", _("No Flavours available.")))
        return choices

    def populate_security_group_choices(self, request, context):
        try:
            security_groups = api.network.security_group_list(request)
            security_group_list = [(security_group.id, "%s" % security_group.name)
                                   for security_group in security_groups]
        except:
            security_group_list = []
            exceptions.handle(request,
                              _('Unable to retrieve instance Security Groups.'))
        choices = sorted(security_group_list)
        if choices:
            choices.insert(0, ("", _("Select Security Group")))
        else:
            choices.insert(0, ("", _("No Security Group available.")))
        return choices

    def populate_category_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            categories = api.sfc.category_list_for_tenant(request, tenant_id)
            category_list = [(category.id, "%s" % category.name)
                             for category in categories]
        except:
            category_list = []
            exceptions.handle(request,
                              _('Unable to retrieve categories.'))
        choices = sorted(category_list)
        if choices:
            choices.insert(0, ("", _("Select Category")))
        else:
            choices.insert(0, ("", _("No Categories available.")))
        return choices

    def populate_vendor_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            vendors = api.sfc.vendor_list_for_tenant(request, tenant_id)
            vendor_list = [(vendor.id, "%s" % vendor.name)
                           for vendor in vendors]
        except:
            vendor_list = []
            exceptions.handle(request,
                              _('Unable to retrieve vendors.'))
        choices = sorted(vendor_list)
        if choices:
            choices.insert(0, ("", _("Select Vendor")))
        else:
            choices.insert(0, ("", _("No Vendors available.")))
        return choices
    
    def populate_config_handle_id_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            config_handles = api.sfc.config_handle_list_for_tenant(request, tenant_id)
            config_handle_list = [(config_handle.id, "%s" % config_handle.name)
                           for config_handle in config_handles]
        except:
            config_handle_list = []
            exceptions.handle(request,
                              _('Unable to retrieve Config Handles.'))
        choices = sorted(config_handle_list)
        if choices:
            choices.insert(0, ("", _("Select Config Handle")))
        else:
            choices.insert(0, ("", _("No Config Handles available.")))
        return choices


class CreateImageInfo(workflows.Step):
    action_class = CreateImageInfoAction
    contributes = ("appliance_name", "image_id", "flavor",
                   "category", "vendor", "security_group", "form_factor_type",
                   "config_handle_id", "appliance_type")

class CreateLoadbalancerInfoAction(workflows.Action):
    load_share_algorithm = (
        ("", _("Select")),
        ("Round Robin", _("Round Robin")),
        ("Hash Based", _("Hash Based")),
        ("Least Connection", _("Least Connection")),
    )
    load_indication_type = (
        ("", _("Select")),
        ("CONNECTION_BASED", _("CONNECTION_BASED")),
        ("TRAFFIC_BASED", _("TRAFFIC_BASED")),
    )
    
    load_share_algorithm = forms.ChoiceField(label=_("Load Share Algorithm"),
                                             required=True,
                                             choices=load_share_algorithm)
    high_threshold = forms.CharField(label=_("High Threshold"),
                                     required=True,)
    low_threshold = forms.CharField(label=_("Low Threshold"),
                                    required=True,)
    pkt_field_to_hash = forms.CharField(label=_("Packet Filed To Hash"),
                                        required=True,)
    load_indication_type = forms.ChoiceField(label=_("Load Indication Type"),
                                             required=True,
                                             choices=load_indication_type)

    class Meta:
        name = ("Loadbalancer Info")
        help_text = _("Loadbalancer Information.\n")
    
class LoadbalancerInfo(workflows.Step):
    action_class = CreateLoadbalancerInfoAction
    contributes = ("load_share_algorithm", "high_threshold", "low_threshold",
                   "pkt_field_to_hash", "load_indication_type")

class CreateImage(workflows.Workflow):
    slug = "create_appliance"
    name = _("Create Appliance")
    finalize_button_name = _("Create")
    success_message = _('Created appliance "%s".')
    failure_message = _('Unable to create appliance "%s".')
    success_url = "horizon:project:appliances:index"
    default_steps = (CreateImageInfo,
                     LoadbalancerInfo)

    def format_status_message(self, message):
        name = self.context.get('name') or self.context.get('id', '')
        return message % name

    def handle(self, request, data):
        # create the image map
        try:
            appliance = api.sfc.appliance_create(request,
                                                 name=data['appliance_name'],
                                                 image_id=data['image_id'],
                                                 flavor_id=data['flavor'],
                                                 category_id=data['category'],
                                                 vendor_id=data['vendor'],
                                                 security_group_id=data['security_group'],
                                                 form_factor_type=data['form_factor_type'],
                                                 config_handle_id=data['config_handle_id'],
                                                 load_share_algorithm=data['load_share_algorithm'],
                                                 high_threshold=data['high_threshold'],
                                                 low_threshold=data['low_threshold'],
                                                 pkt_field_to_hash=data['pkt_field_to_hash'],
                                                 load_indication_type=data['load_indication_type'],
                                                 type=data['appliance_type'])
            appliance.set_id_as_name_if_empty()
            self.context['id'] = appliance.id
            msg = _(
                'Appliance "%s" was successfully created.') % appliance.name
            LOG.debug(msg)
        except:
            msg = _('Failed to create Appliance "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse('horizon:project:appliances:index')
            exceptions.handle(request, msg, redirect=redirect)
            return False

        return True
