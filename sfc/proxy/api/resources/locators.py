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

class ServiceLocator(_Base):
    """
    Representation of Service Locator Structure.
    """

    id = uuid
    "The UUID of the Service Locator."

    name = wtypes.StringType(max_length=255)
    "The name for the Service Locator."
    
    description = wtypes.text
    "The description for the Service Locator."

    tenant_id = uuid
    "Tenant UUID"

    type = wsattr(wtypes.Enum(str, 'l2-address', 'l3-address'))
    "Owner of the Service Locator."

    ethernet_port = int
    "Ethernet Port number."

    l2_address = MACAddressType()
    "MAC Address."

    vlan_id = int
    "VLAN ID."

    l3_address = IPAddressType()
    "IP Address"

    l4_port = int
    "L4 Port number. TCP/UDP Port number"

    direction = wsattr(wtypes.Enum(str, 'ingress', 'egress', 'both'))
    "Hardware Interface Direction for packets."

    def as_dict(self):
        return self.as_dict_from_keys(['id', 'name', 'description', 'type', 
                                       'ethernet_port', 'l2_address',
                                       'tenant_id','vlan_id', 'l3_address',
                                       'l4_port', 'direction'])


class ServiceLocatorsResp(_Base):
    """
    Representation of Service locators list Response
    """
    service_locators = [ServiceLocator]


class ServiceLocatorResp(_Base):
    """
    Representation of Service Locator Response
    """
    service_locator = ServiceLocator


class ServiceLocatorController(rest.RestController):

    @expose.expose(ServiceLocatorResp, ServiceLocator)
    def post(self, service_locator):
        """
        This function implements create record functionality of the
        Service Locator attributes of Service Locator.

        :return: Dictionary of the added record.
        """
        
        LOG.debug(_("Service Locator create: %s"), str(service_locator))
        return ServiceLocatorResp(**({'service_locator': service_locator}))

    @expose.expose(ServiceLocatorResp, wtypes.text, ServiceLocator)
    def put(self, sl_id, service_locator):
        """
        This function implements update record functionality of the 
        Service Locator attributes of Service Locator.

        :return: Dictionary of the updated record.
        """
        service_locator.id = sl_id

        return ServiceLocatorResp(**({'service_locator': service_locator}))

    @expose.expose(None, wtypes.text, status_code=204)
    def delete(self, sl_id):
        """Delete this Service Locator."""
        pass


