import copy
from oslo.config import cfg
from oslo_i18n._i18n import _
from oslo_log import log as logging
from oslo_utils import uuidutils
from pecan import request, response, rest
from wsme import types as wtypes, wsattr

from sfc.proxy.api import expose
from sfc.proxy.api.resources.base import BaseController
from sfc.proxy.api.resources.types import _Base, \
    uuid, MACAddressType, IPAddressType


LOG = logging.getLogger(__name__)

class ServiceGroup(_Base):
    """
    Representation of Service Group Structure.
    """

    id = uuid
    "The UUID of the Service Group."

    name = wtypes.StringType(max_length=255)
    "The name for the Service Group."
    
    description = wtypes.text
    "The description for the Service Group."

    type = wsattr(wtypes.Enum(str, 'FW', 'IPS', 'NAT', 'DPI', 'LB'))
    "Owner of the Service Group."

    algorithm = wsattr(wtypes.Enum(str, 'random', 'round-robin', 'hash'))
    "Algorithm to use for Loadbalancing the SF Instance."

    hash_field = wsattr(wtypes.Enum(str, 'SIP', 'DIP', 'SPORT',
                                         'DPORT', 'SPORT+DPORT', 
                                         'SMAC'))
    "Packet Field to use for hashing."

    service_functions = [uuid]
    "Service Function Instance UUIDs using this SF Group."

    def as_dict(self):
        return self.as_dict_from_keys(['id', 'name', 'description', 'type', 
                                       'algorithm', 'hash_field', 
                                       'service_functions'])


class ServiceGroupsResp(_Base):
    """
    Representation of Service groups list Response
    """
    service_groups = [ServiceGroup]


class ServiceGroupResp(_Base):
    """
    Representation of Service Group Response
    """
    service_group = ServiceGroup


class ServiceGroupController(rest.RestController):

    @expose.expose(ServiceGroupResp, ServiceGroup)
    def post(self, service_group):
        """
        This function implements create record functionality of the
        Service Group attributes of Service Group.

        :return: Dictionary of the added record.
        """
        
        LOG.debug(_("Service Group create: %s"), str(service_group))
        return ServiceGroupResp(**({'service_group': service_group}))

    @expose.expose(ServiceGroupResp, wtypes.text, ServiceGroup)
    def put(self, sg_id, service_group):
        """
        This function implements update record functionality of the 
        Service Group attributes of Service Group.

        :return: Dictionary of the updated record.
        """
        service_group.id = sg_id

        return ServiceGroupResp(**({'service_group': service_group}))

    @expose.expose(None, wtypes.text, status_code=204)
    def delete(self, sg_id):
        """Delete this Service Group."""
        pass


