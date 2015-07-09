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
from horizon import forms
from horizon import messages


LOG = logging.getLogger(__name__)


class BaseApplianceForm(forms.SelfHandlingForm):

    def __init__(self, request, *args, **kwargs):
        super(BaseApplianceForm, self).__init__(request, *args, **kwargs)
        tenant_id = self.request.user.tenant_id
        # Populate Flavor choices
        flavor_choices = [('', _("Select a Flavor"))]
        for fl in api.nova.flavor_list(request):
            flavor_choices.append((fl.id, fl.name))
            self.fields['flavor_id'].choices = flavor_choices

        # Populate Security Group choices
        sg_choices = [('', _("Select a Security Group"))]
        for sg in api.network.security_group_list(request):
            sg_choices.append((sg.id, sg.name))
            self.fields['security_group_id'].choices = sg_choices

        # Populate Category choices
        cat_choices = [('', _("Select a Category"))]
        for cat in api.sfc.category_list_for_tenant(request, tenant_id):
            cat_choices.append((cat.id, cat.name))
            self.fields['category_id'].choices = cat_choices

        # Populate Vendor choices
        ven_choices = [('', _("Select a Vendor"))]
        for ven in api.sfc.vendor_list_for_tenant(request, tenant_id):
            ven_choices.append((ven.id, ven.name))
            self.fields['vendor_id'].choices = ven_choices

        # Populate Images
        img_choices = [('', _("Select an Image"))]
        images = self._get_available_images(request)
        for img in images:
            if img.properties.get("servicevm", '') == "yes":
                img_choices.append((img.id, img.name))
        self.fields['image_id'].choices = img_choices
        
        # Populate Config Handles
        config_handle_choices = []
        for config in api.sfc.config_handle_list_for_tenant(request, tenant_id):
            config_handle_choices.append((config.id, config.name))
        self.fields['config_handle_id'].choices = config_handle_choices

    def _get_available_images(self, request):
        project_id = self.request.user.tenant_id
        #project_id = context.get('project_id', None)
        if not hasattr(self, "_public_images"):
            public = {"is_public": True,
                      "status": "active"}
            try:
                (public_images, _more, _prev) = api.glance.image_list_detailed(request,
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
                (owned_images, _more, _prev) = api.glance.image_list_detailed(request,
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


class UpdateImage(BaseApplianceForm):
    form_factor_type = (
        ("", _("Select")),
        ("Virtual", _("Virtual")),
        ("Physical", _("Physical")),
    )
    
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
    
    appliance_id = forms.CharField(label=_("ID"),
                                   widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Name"),
                           widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    image_id = forms.ChoiceField(label=_("Image"))
    flavor_id = forms.ChoiceField(label=_("Flavor"),
                                  help_text=_("Size of image to launch."))
    security_group_id = forms.ChoiceField(label=_("Security Group"))
    category_id = forms.ChoiceField(label=_("Category"),
                                    help_text=_("To which Category it belongs."))
    vendor_id = forms.ChoiceField(label=_("Vendor"),
                                  help_text=_("Who is the Vendor."))
    form_factor_type = forms.ChoiceField(label=_("Form Factor Type"),
                                         required=True,
                                         choices=form_factor_type)
    config_handle_id = forms.ChoiceField(label=_("Config Handles"),
                                  help_text=_("Config Handle to Map."))
    load_share_algorithm = forms.ChoiceField(label=_("Load Share Algorithm"),
                                             required=True,
                                             choices=load_share_algorithm)
    high_threshold = forms.CharField(label=_("High Threshold"))
    low_threshold = forms.CharField(label=_("Low Threshold"))
    pkt_field_to_hash = forms.CharField(label=_("Packet Filed To Hash"))
    load_indication_type = forms.ChoiceField(label=_("Load Indication Type"),
                                             required=True,
                                             choices=load_indication_type)
    tenant_id = forms.CharField(widget=forms.HiddenInput)

    failure_url = 'horizon:project:appliances:index'

    def handle(self, request, data):
        try:
            appliance = api.sfc.appliance_modify(request, data['appliance_id'],
                                                 name=data['name'],
                                                 image_id=data['image_id'],
                                                 flavor_id=data['flavor_id'],
                                                 category_id=data[
                                                     'category_id'],
                                                 vendor_id=data['vendor_id'],
                                                 form_factor_type=data[
                                                     'form_factor_type'],
                                                 security_group_id=data['security_group_id'],
                                                 load_share_algorithm=data['load_share_algorithm'],
                                                 high_threshold=data['high_threshold'],
                                                 low_threshold=data['low_threshold'],
                                                 pkt_field_to_hash=data['pkt_field_to_hash'],
                                                 load_indication_type=data['load_indication_type'],)
            msg = _('Appliance %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return appliance
        except:
            msg = _('Failed to update appliance %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)