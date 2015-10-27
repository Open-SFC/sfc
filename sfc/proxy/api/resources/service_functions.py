import copy

from wsme import types as wtypes, wsattr
from novaclient.v2.client import Client as nc
from pecan import request, response, rest
from oslo_config import cfg as ocfg
from oslo_log import log as logging
from oslo_i18n._i18n import _
from oslo_utils import uuidutils
from m2client.v1_0.client import Client as m2c
from neutronclient.v2_0.client import Client as neutron

from nscs_firewall.crdclient.v2_0 import client as fwclient
from sfc.proxy.api import expose
from sfc.proxy.api.resources.base import BaseController
from sfc.proxy.api.resources.types import _Base, \
    uuid, IPAddressType, MACAddressType
from sfc.proxy.common import exceptions as sfcexc 

LOG = logging.getLogger(__name__)


class ServiceFunction(_Base):
    """
    Representation of Service Function Structure.
    """

    id = uuid
    "The UUID of the Service Function."

    name = wtypes.StringType(max_length=255)
    "The name for the Service Function."
    
    description = wtypes.text
    "The description for the Service Function."

    tenant_id = uuid
    "Owner of the Service Function."

    type = wsattr(wtypes.Enum(str, 'FW', 'IDS', 'NAT', 'DPI'))
    "Service Function Type."

    sch_type = wsattr(wtypes.Enum(str, None, 'SCH', 'MAC'))
    "Service Chain Header Type"

    locators = [uuid]
    "Locator Information."

    mgmt_address = IPAddressType()
    "Management Address for Service Function."

    flavor = wsattr(wtypes.text)
    "Service Capability Information."

    sf_group = uuid
    "Service Function Group."

    def as_dict(self):
        return self.as_dict_from_keys(['id', 'name', 'description',
                                       'tenant_id', 'type', 'sch_type',
                                       'locators', 'mgmt_address', 'flavor',
                                       'sf_group'])


class ServiceFunctionsResp(_Base):
    """
    Representation of Chains list Response
    """
    service_functions = [ServiceFunction]


class ServiceFunctionResp(_Base):
    """
    Representation of Chain Response
    """
    service_function = ServiceFunction


class ServiceFunctionController(rest.RestController):

    SF_SLUG_MAP = {"fw": "firewall",
                   "lb": "loadbalancer"}

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
        self.nova = nc(username=ocfg.CONF.nova.username,
                       api_key=ocfg.CONF.nova.password,
                       tenant_id=tenant_id,
                       auth_url=ocfg.CONF.nova.auth_url)
        return self.nova.servers.get(instance_id)

    def _fetch_image_details(self, image_id):
        return self.nova.images.get(image_id)

    @staticmethod
    def _fetch_sf_group(service_group_id, tenant_id):
        if not service_group_id:
            return None
        m2 = m2c(username=ocfg.CONF.neutron.username,
                 password=ocfg.CONF.neutron.password,
                 tenant_id=tenant_id,
                 auth_url=ocfg.CONF.neutron.auth_url)
        return m2.show_service_function_group(service_group_id)

    @staticmethod
    def _fetch_security_group(security_group_name, tenant_id):
        if not security_group_name:
            return None
        nec = neutron(username=ocfg.CONF.neutron.username,
                      password=ocfg.CONF.neutron.password,
                      tenant_id=tenant_id,
                      auth_url=ocfg.CONF.neutron.auth_url)
        return nec.list_security_groups(name=security_group_name,
                                       tenant_id=tenant_id)['security_groups']

    @staticmethod
    def _format_uuid_string(string):
        return (string.replace('urn:', '')
                      .replace('uuid:', '')
                      .strip('{}')
                      .replace('-', '')
                      .lower())

    @expose.expose(ServiceFunctionResp, ServiceFunction)
    def post(self, service_function):
        """
        This function implements create record functionality of the
        Service Function Instance.

        :return: Dictionary of the added record.
        """
        LOG.debug(_("####################################################"))
        LOG.debug(_("Service Function create: %s"), str(service_function.as_dict()))
        LOG.debug(_("####################################################"))
        tenant_id = self._format_uuid_string(service_function.tenant_id)
        flavor_attr = self._parse_flavor(service_function.flavor)
        instance_id = flavor_attr.get('instance_id', None)
        if not instance_id:
            raise sfcexc.InstanceNotFound(instance_id=instance_id)
        instance = self._fetch_instance_details(instance_id, tenant_id)

        print instance.to_dict()

        app_details = self._fetch_image_details(instance.image['id'])

        print app_details.to_dict()

        # Create Network Function with type if the same does not exist in
        # CRD.
        nf = request.crdclient.list_networkfunctions(
            name=service_function.type.lower(),
            tenant_id=tenant_id)['networkfunctions']
        if not nf:
            nf = {'networkfunction': {
                'name': service_function.type.lower(),
                'description': service_function.type.lower(),
                'tenant_id': tenant_id}}
            nf = request.crdclient.create_networkfunction(body=nf)
            nf = nf['networkfunction']['id']
        else:
            nf = nf[0]['id']

        # Create a default Category
        ctg = request.crdclient.list_categories(
            name=app_details.metadata['category'],
            tenant_id=tenant_id)['categories']
        if not ctg:
            ctg = {"category": {
                "name": app_details.metadata['category'],
                "description": app_details.metadata['category'],
                'tenant_id': tenant_id,
                "category_networkfunctions": [nf]}}
            ctg = request.crdclient.create_category(body=ctg)
            ctg = ctg['category']['id']
        else:
            ctg = ctg[0]['id']

        # Create Configuration
        cfg = request.crdclient.list_config_handles(
            networkfunction_id=nf,
            tenant_id=tenant_id)['config_handles']

        if not cfg:
            cfg_name = flavor_attr['config'] + uuidutils.generate_uuid()[:13]
            if not cfg_name:
                raise sfcexc.InvalidName(name='config')
            cfg = {"config_handle": {
                "name": cfg_name,
                'tenant_id': tenant_id,
                "status": True,
                "slug": self.SF_SLUG_MAP[service_function.type.lower()],
                "config_mode": "NFV"}}
            cfg = request.crdclient.create_config_handle(body=cfg)
            cfg = cfg['config_handle']['id']
        else:
            cfg = cfg[0]['id']

        # Map Firewall
        if service_function.type.lower() == 'fw':
            fwc = fwclient.Client(username=ocfg.CONF.crd.username,
                                  password=ocfg.CONF.crd.password,
                                  tenant_name=
                                  ocfg.CONF.crd.tenant_name,
                                  auth_url=ocfg.CONF.crd.auth_url)
            fws = fwc.list_firewalls(name=flavor_attr.get('config', ''),
                                     tenant_id=tenant_id)
            if fws:
                fw_id = fws['firewalls'][0]['id']
                fwc.update_firewall(fw_id, body={'firewall': {
                    'config_handle_id': cfg}})
                
        # Map Loadbalancer
        if service_function.type.lower() == 'lb':
            lbc = lbclient.Client(username=ocfg.CONF.crd.username,
                                  password=ocfg.CONF.crd.password,
                                  tenant_name=
                                  ocfg.CONF.crd.tenant_name,
                                  auth_url=ocfg.CONF.crd.auth_url)
            pools = lbc.list_pools(name=flavor_attr.get('config', ''),
                                     tenant_id=tenant_id)
            if pools:
                pool_id = pools['pools'][0]['id']
                lbc.update_pool(pool_id, body={'loadbalancer': {
                    'config_handle_id': cfg}})

        # Create Vendor
        vendor = request.crdclient.list_vendors(
            name=app_details.metadata['vendor'],
            tenant_id=tenant_id)['vendors']

        if not vendor:
            vendor = {'vendor': {
                'name': app_details.metadata['vendor'],
                'description': app_details.metadata['vendor'],
                'tenant_id': tenant_id}}
            vendor = request.crdclient.create_vendor(body=vendor)['vendor']
        else:
            vendor = vendor[0]
        print vendor

        sf_group = self._fetch_sf_group(service_function.sf_group,
                                        tenant_id)['service_group']
        print sf_group
        sec_group = self._fetch_security_group(
            instance.security_groups[0]['name'],
            tenant_id)[0]['id']

        load_share_algorithm = ''
        if sf_group['algorithm'] == 'round-robin':
            load_share_algorithm = 'Round Robin'
        appliance = dict({'name': app_details.name[:6] + sf_group['id'][:10],
                          'tenant_id': tenant_id,
                          'category_id': ctg,
                          'vendor_id': vendor['id'],
                          'image_id': app_details.id,
                          'flavor_id': instance.flavor['id'],
                          'security_group_id': sec_group,
                          'form_factor_type': 'virtual',
                          'type': 'L2',
                          'load_share_algorithm': load_share_algorithm,
                          'high_threshold': 100,
                          'low_threshold': 1,
                          'pkt_field_to_hash': sf_group['hash_field'],
                          'load_indication_type': 'connection_based',
                          'config_handle_id': cfg})
        appliances = request.crdclient.list_appliances(name=appliance['name'],
                                                       config_handle_id=cfg)

        if not appliances['appliances']:
            app = request.crdclient.create_appliance(body={
                'appliance': appliance})

        #print app
        return ServiceFunctionResp(**({'service_function': service_function}))

    @expose.expose(ServiceFunctionResp, wtypes.text, ServiceFunction)
    def put(self, sf_id, service_function):
        """
        This function implements update record functionality of the 
        Service Function Instance.

        :return: Dictionary of the updated record.
        """
        service_function.id = sf_id

        return ServiceFunctionResp(**({'service_function': service_function}))

    @expose.expose(None, wtypes.text, status_code=204)
    def delete(self, sf_id):
        """Delete this Service Function Instance."""
        pass


