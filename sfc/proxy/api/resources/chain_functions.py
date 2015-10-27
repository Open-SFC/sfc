import copy

import wsme
from pecan import request, response, rest
from wsme import types as wtypes
from novaclient.v2.client import Client as nc
from oslo_config import cfg
from oslo_log import log as logging
from oslo_i18n._i18n import _
from oslo_utils import uuidutils

from sfc.proxy.api import expose
from sfc.proxy.api.resources.base import BaseController
from sfc.proxy.api.resources.types import _Base, \
    uuid, AdvEnum, IPAddressType

from m2client.v1_0.client import Client as m2c

from sfc.proxy.common import exceptions as sfcexc

LOG = logging.getLogger(__name__)

class ChainFunction(_Base):
    """
    Representation of Chain Function Structure
    """
    id = uuid
    "The UUID of the chain function association"

    name = wtypes.StringType(max_length=255)
    "The name for the chain function association"
    
    description = wsme.wsattr(wtypes.text)
    "The description for the chain function association"

    service_chain_id = uuid
    "The Chain UUID to which the Chain Function belongs"

    service_instance_id = uuid
    "The Service Function Instance UUID to which the Chain Function belongs"

    tenant_id = uuid
    "Tenant UUID to which chain function belongs"

    order = int
    "Order in which Service Function Instance started"

    def as_dict(self):
        return self.as_dict_from_keys(['id', 'name', 'description',
                                       'service_chain_id',
                                       'service_instance_id',
                                       'order', 'tenant_id'])


class ChainFunctionsResp(_Base):
    """
    Representation of ChainFunctions list Response
    """
    chain_functions = [ChainFunction]


class ChainFunctionResp(_Base):
    """
    Representation of ChainFunction Response
    """
    chain_function = ChainFunction


class ChainFunctionController(rest.RestController):

    @staticmethod
    def _parse_flavor(flavor):

        attrs = dict()
        flavor_attr = flavor.split(',')
        for attr in flavor_attr:
            k, v = attr.split(':')
            attrs[k.strip()] = v.strip()
        return attrs

    def _fetch_instance_details(self, instance_id, tenant_id):
        """
        Fetch Instance details required and return instance object.
        """
        if not instance_id:
            return None
        # Create Appliance
        # Fetch Appliance details from Nova
        if not hasattr(self, 'nova'):
            self.nova = nc(username=cfg.CONF.nova.username,
                           api_key=cfg.CONF.nova.password,
                           tenant_id=tenant_id,
                           auth_url=cfg.CONF.nova.auth_url)
        return self.nova.servers.get(instance_id)

    def _fetch_image_details(self, image_id):
        return self.nova.images.get(image_id)

    def _fetch_sf_details(self, service_function_id, tenant_id):
        if not hasattr(self, 'm2'):
            self.m2 = m2c(username=cfg.CONF.neutron.username,
                          password=cfg.CONF.neutron.password,
                          tenant_id=tenant_id,
                          auth_url=cfg.CONF.neutron.auth_url)
        return self.m2.show_service_function(service_function_id)

    def _fetch_sf_group(self, service_group_id):
        if not service_group_id:
            return None
        return self.m2.show_service_function_group(service_group_id)[
            'service_group']

    def _fetch_locators(self, service_function_id):
        return self.m2.list_service_locators(sf_id=service_function_id)[
            'service_locators']
    @staticmethod
    def _format_uuid_string(string):
        return (string.replace('urn:', '')
                      .replace('uuid:', '')
                      .strip('{}')
                      .replace('-', '')
                      .lower())

    @staticmethod
    def _map_chain_service_function(chain_id, chain_app_id,
                                    chain_function):
        if chain_app_id:
            chain_function['appliance'].update({'id': chain_app_id})
        return request.crdclient.create_appliance_map(
            chain_id,
            body=chain_function)

    @expose.expose(ChainFunctionResp, ChainFunction)
    def post(self, chain_function):
        """
        This function implements create record functionality of the RESTful
        request.
        It converts the requested body in JSON format to dictionary in string
        representation and verifies whether
        required ATTRIBUTES are present in the POST request body.

        :return: Dictionary of the added record.
        """
        LOG.debug(_("ChainFunction create: %s"), str(chain_function.as_dict()))
        print chain_function.as_dict()
        tenant_id = self._format_uuid_string(chain_function.tenant_id)

        ### Check if the Chain Exists in CRD Service...
        chain_details = request.crdclient.show_chain(chain_function.service_chain_id)
        if chain_details:
            ### If Chain Exists...Add Chain - Appliances association
            ### Get Appliance ID from the combination of Service Function
            ### Instance Image Name and Service Function Group UUID
            ### (first 11 chars)
            sf_details = self._fetch_sf_details(
                chain_function.service_instance_id,
                tenant_id)

            print sf_details
            sf_details = sf_details['reg_service_function']
            sf_group_details = self._fetch_sf_group(sf_details['sf_group_id'])

            print sf_group_details
            
            ### Fetch Service Function Instance Details from Nova
            flavor = self._parse_flavor(sf_details['flavor'])
            instance_id = flavor.get('instance_id', None)
            if not instance_id:
                raise sfcexc.InstanceNotFound(instance_id=instance_id)
            instance_details = self._fetch_instance_details(instance_id,
                                                            tenant_id)
            intf = instance_details.interface_list()[0]
            instance_details = instance_details.to_dict()
            
            image_details = self._fetch_image_details(instance_details[
                'image']['id']
            ).to_dict()

            image_name = image_details.get('name')
            appliance_name = image_name[:6] + sf_group_details['id'][:10]
            LOG.debug(_("Appliance Name: %s"), str(appliance_name))
            
            appliances = request.crdclient.list_appliances(
                name=appliance_name, tenant_id=tenant_id)
            appliances = appliances['appliances']
            if appliances:
                appliance_details = appliances[0]
                appliance_id = appliance_details['id']
            else:
                raise sfcexc.AppliancesNotFound(name=appliance_name)
            
            seq_number = chain_function.order + 1
            if chain_function.service_chain_id and appliance_id:
                chain_function_data = {
                    'appliance': {
                        'name': chain_function.name,
                        'tenant_id': sf_details['tenant_id'],
                        'appliance_id': appliance_id,
                        #'sequence_number': chain_function.order,
                        'sequence_number': seq_number,
                    }
                }
                
                if chain_function.id:
                    chain_function_data['appliance'].update(
                        {'id': chain_function.id})
                    
                ### Create CRD Chain Appliance Association....
                chain_function_resp = self._map_chain_service_function(
                    chain_function.service_chain_id,
                    chain_function.id, chain_function_data)
                LOG.debug(_("Chain Appliance Association Response: %s"),
                          str(chain_function_resp))
                
                ### Get Locators information from Service Function Instances
                ### to get VLAN IN and VLAN OUT
                locators = self._fetch_locators(sf_details['id'])
                LOG.debug(_("Locators List: %s"), str(locators))
                print locators[0]
                print locators[1]
                print "****************************************"
                ### TODO:: Get locator information from Huawei Neutron
                ### extension
                
                ### Sample vlan_in and vlan_out locators for
                ### the time being
                vlan_in = None
                vlan_out = None

                for lc in locators:
                    if lc['direction'] == 'ingress' and not vlan_in:
                        vlan_in = int(lc['vlan_id'])
                    elif lc['direction'] == 'egress' and not vlan_out:
                        vlan_out = int(lc['vlan_id'])
                
                LOG.debug(_("VLAN IN: %s"), str(vlan_in))
                LOG.debug(_("##################"))
                LOG.debug(_("VLAN OUT: %s"), str(vlan_out))
                
                if vlan_in and vlan_out and chain_function_resp and intf.net_id:
                    ### Insert SFC Appliance-Instances mapping ...
                    appliance_instance_data = {
                        'instance': {
                            'tenant_id': sf_details['tenant_id'],
                            'instance_uuid': instance_id,
                            'vlan_in': str(vlan_in),
                            'vlan_out': str(vlan_out),
                            'network_id': intf.net_id
                        }
                    }
                    
                    LOG.debug(_("Appliance - Instance Association Body: %s"), str(appliance_instance_data))
                    appliance_instance_resp = request.crdclient.create_appliance_map_instance(
                        chain_function.service_chain_id,
                        appliance_id,
                        body=appliance_instance_data)
                    LOG.debug(_("Appliance - Instance Association Response: %s"), str(appliance_instance_resp))
                
                ### Insert Chainset Network Map, only when chainset exists
                classifier_str = chain_details['chain']['extras']
                if classifier_str:
                    chainsets = classifier_str.split(',')
                    for chainset in chainsets:
                        if chainset:
                            name = 'chainmap_' + chainset[:11]
                            chainmaps = request.crdclient.list_chainmaps(
                                inbound_network_id=intf.net_id,
                                chainset_id=chainset)['chainmaps']
                            LOG.debug(_("##################################"))
                            LOG.debug(_("ChainMaps: %s"), str(chainmaps))
                            LOG.debug(_("##################################"))
                            if not chainmaps:
                                chainset_network_data = {
                                    'chainmap': {
                                        'name': name,
                                        'chainset_id': chainset,
                                        'inbound_network_id': intf.net_id,
                                        #'outbound_network_id': intf.net_id
                                        }
                                }
                                
                                LOG.debug(_("Chainset - Network Map body: %s"), str(chainset_network_data))
                                chainset_network_resp = request.crdclient.create_chainmap(
                                    body=chainset_network_data)
                                LOG.debug(_("Chainset - Network Map Association Response: %s"), str(chainset_network_resp))
                
            else:
                LOG.error(_("Either Chain ID %s or Appliance ID %s is INVALID"), str(chain_function.service_chain_id), str(appliance_id))
                raise sfcexc.NotAcceptable()
        else:
            raise sfcexc.ChainNotFound()

        return ChainFunctionResp(**({'chain_function': chain_function}))

    @expose.expose(ChainFunctionResp, wtypes.text, ChainFunction)
    def put(self, chain_function_id, chain_function):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body.

        :return: Dictionary of the added record.
        """
        chain_function.id = chain_function_id

        return ChainFunctionResp(**({'chain_function': chain_function}))

    @expose.expose(None, wtypes.text, status_code=204)
    def delete(self, chain_function_id):
        """Delete this ChainFunction."""
        pass
