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

from django.conf.urls import patterns, url, include


from .views import IndexView, CreateChainView, UpdateChainView, DetailChainView, BypassChainView
from .appliance_maps.views import MapimgView, EditChain_imageView, DetailChainImageView, ListInstancesView
from .bypass_rules.views import Addl2ruleview, Editl2ruleView, RuleDetailView
from .appliance_maps.configurations.views import MapconfView
from .appliance_maps import urls as appliance_map_urls


CHAINS = r'^(?P<chain_id>[^/]+)/%s$'


urlpatterns = patterns('',
                       url(r'^$', IndexView.as_view(), name='index'),
                       url(r'^create/$', CreateChainView.as_view(),
                           name='create'),
                       url(CHAINS %
                           'update', UpdateChainView.as_view(), name='update'),
                       url(CHAINS %
                           'detail', DetailChainView.as_view(), name='detail'),
                       url(CHAINS %
                           'bypass', BypassChainView.as_view(), name='bypass'),
                       url(CHAINS % 'appliance_maps/mapimg',
                           MapimgView.as_view(), name='mapimg'),
                       url(CHAINS % 'bypass_rules/bypassrules',
                           Addl2ruleview.as_view(), name='bypassrules'),
                       url(r'^(?P<chain_id>[^/]+)/bypass_rules/(?P<rule_id>[^/]+)/editl2rule$',
                           Editl2ruleView.as_view(), name='editl2rule'),
                       url(r'^(?P<chain_id>[^/]+)/bypass_rules/(?P<rule_id>[^/]+)/ruledetail$', RuleDetailView.as_view(), name='ruledetail'),
                       url(r'^(?P<chain_id>[^/]+)/appliance_maps/(?P<appliance_map_id>[^/]+)/listinstances$',
                           ListInstancesView.as_view(), name='listinstances'),)
