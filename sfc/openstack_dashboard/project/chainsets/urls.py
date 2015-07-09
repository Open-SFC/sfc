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


from .views import IndexView, CreateChainsetView, UpdateChainsetView, DetailChainsetView
from .rules.views import Addruleview, EditruleView, LaunchChainView, RuleDetailView
from .rules import urls as rule_urls
CHAINSET = r'^(?P<chainset_id>[^/]+)/%s$'


urlpatterns = patterns('',
                       url(r'^$', IndexView.as_view(), name='index'),
                       url(r'^create/$', CreateChainsetView.as_view(),
                           name='create'),
                       url(CHAINSET %
                           'update', UpdateChainsetView.as_view(), name='update'),
                       url(CHAINSET %
                           'detail', DetailChainsetView.as_view(), name='detail'),
                       url(CHAINSET % 'rules/addrule',
                           Addruleview.as_view(), name='addrule'),
                       url(r'^(?P<chainset_id>[^/]+)/rules/(?P<rule_id>[^/]+)/editrule$',
                           EditruleView.as_view(), name='editrule'),
                       url(r'^(?P<chainset_id>[^/]+)/rules/(?P<rule_id>[^/]+)/launch$',
                           LaunchChainView.as_view(), name='launch'),
                       url(r'^(?P<chainset_id>[^/]+)/rules/(?P<rule_id>[^/]+)/ruledetail$', RuleDetailView.as_view(), name='ruledetail'),)
