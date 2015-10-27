# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Nicira Networks, Inc
# All Rights Reserved.
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
Crd base exception handling.
"""

from nscs.crdservice.openstack.common.exception import Error
from nscs.crdservice.openstack.common.exception import OpenstackException
from nscs.crdservice.common.exceptions import CrdException, BadRequest, InUse

class NotFound(CrdException):
    pass


class Conflict(CrdException):
    pass


class NotAuthorized(CrdException):
    message = _("Not authorized.")


class ServiceUnavailable(CrdException):
    message = _("The service is unavailable")

class AdminRequired(NotAuthorized):
    message = _("User does not have admin privileges: %(reason)s")


class PolicyNotAuthorized(NotAuthorized):
    message = _("Policy doesn't allow %(action)s to be performed.")


class ClassNotFound(NotFound):
    message = _("Class %(class_name)s could not be found")


###Modifications by Srikanth
class ChainApplianceNotFound(NotFound):
    message = _("Chain Appliance Map for the Chain %(chain_id) and Appliance %(appliance_id) could not be found")
    
class ChainRefExists(InUse):
    message = _("There are some dependencies still there for the Chain %(chain_id)s")
    
class chainset_zones_deltaNotFound(NotFound):
    message = _("There is NO Chainset Zone Delta found for the ID %(chainset_zones_delta_id)s")
    
class ChainSetNotFound(NotFound):
    message = _("Chainset %(chainset_id)s could not be found")
