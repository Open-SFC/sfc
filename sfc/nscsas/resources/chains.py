import copy

import wsme
from pecan import request, response
from wsme import types as wtypes
from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _

import wsmeext.pecan as wsme_pecan
from nscs.nscsas.api.resources.base import BaseController, _Base, \
    BoundedStr, EntityNotFound
from . import model as api_models
from . import db as sfc_db
from cns.nscsas.resources import db as cns_db
from nscs.nscsas.api import utils, constants


LOG = logging.getLogger(__name__)

#UCM Support Start
UCM_LOADED = False
if cfg.CONF.api.ucm_support:
    try:
        import _ucm
        from _ucm import UCMException
        UCM_LOADED = True
    except ImportError:
        LOG.info(_("Unable to Load UCM"))
#UCM Support End


class ChainServiceInstance(_Base):
    """
    Representation of Chain Network Service Instance Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the service map"

    instance_id = BoundedStr(minlen=36, maxlen=36)
    "Network service instance UUID"

    vlan_in = int
    "Input Vlan ID"

    vlan_out = int
    "Output Vlan ID"

    chain_service_id = BoundedStr(minlen=36, maxlen=36)
    "Service id of network service"


class ChainServiceInstancesResp(_Base):
    """
    Representation of Chain Service Instances list Response
    """
    service_instances = [ChainServiceInstance]


class ChainServiceInstanceResp(_Base):
    """
    Representation of Chain Service Instance Response
    """
    service_instance = ChainServiceInstance


class ChainServiceInstancesController(BaseController):
    ATTRIBUTES = {
        'instance_name': ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'vm_name': ['name', {'type': 'string', 'mandatory': True}],
        'vlanid_in': ['vlan_in', {'type': 'int', 'mandatory': True}],
        'vlanid_out': ['vlan_out', {'type': 'int', 'mandatory': True}]
    }
    dmpath = 'nsrm.chain{name=%s,tenant=%s}.services{%s}.service_instance'

    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()
        self.cns_conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(ChainServiceInstanceResp, wtypes.text, wtypes.text, ChainServiceInstance)
    def post(self, chain_id, chain_service_id, service_instance):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = service_instance.as_dict(api_models.ChainServiceInstance)
        change['chain_id'] = chain_id
        change['chain_service_id'] = chain_service_id

        service_instances = list(self.conn.get_chain_service_instances(service_instance_id=service_instance.id,
                                                                       chain_id=chain_id,
                                                                       chain_service_id=chain_service_id))

        if len(service_instances) > 0:
            error = _("Service Instance with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chains = list(self.conn.get_chains(chain_id=chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), chain_id)

        chain_service = list(self.conn.get_chain_services(chain_service_id=chain_service_id,
                                                          chain_id=chain_id))

        if len(chain_service) < 1:
            error = _("Chain Service with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service = list(self.conn.get_services(service_id=chain_service[0].service_id))

        if len(service) < 1:
            error = _("Network Service with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        instance = list(self.cns_conn.get_virtualmachines(vm_id=service_instance.instance_id))
        if len(instance) < 1:
            error = _("instance with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            service_in = api_models.ChainServiceInstance(**change)
        except Exception:
            LOG.exception("Error while posting Network Service: %s" % change)
            error = _("Network service incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service_out = self.conn.create_chain_service_instance(service_in)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = service_out.as_dict()

            body['name'] = str(instance[0].name)
            ucm_record = utils.generate_ucm_data(self, body,
                                                 (str(chains[0].name),
                                                  str(chains[0].tenant),
                                                 str(service[0].name)))
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add service instance record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to service instance record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return ChainServiceInstanceResp(**(
            {'service_instance': ChainServiceInstance.from_db_model(service_out)}))

    @wsme_pecan.wsexpose(ChainServiceInstancesResp, wtypes.text, wtypes.text)
    def get_all(self, chain_id, chain_service_id):
        """Return all Service Instances, based on the query provided.

        :param q: Filter rules for the chains to be returned.
        """
        #TODO: Need to handle Query filters
        return ChainServiceInstancesResp(**(
            {'service_instances': [ChainServiceInstance.from_db_model(m)
                                   for m in self.conn.get_chain_service_instances(chain_id=chain_id,
                                                                                  chain_service_id=chain_service_id)]}))

    @wsme_pecan.wsexpose(ChainServiceInstanceResp, wtypes.text, wtypes.text, wtypes.text)
    def get_one(self, chain_id, chain_service_id, service_instance_id):
        """Return this Chain Network Service Instance."""
        service_instances = list(self.conn.get_chain_service_instances(chain_id=chain_id,
                                                                       chain_service_id=chain_service_id,
                                                                       service_instance_id=service_instance_id))

        if len(service_instances) < 1:
            raise EntityNotFound(_('Chain Service'), chain_service_id)

        return ChainServiceInstanceResp(**(
            {'service_instance': ChainServiceInstance.from_db_model(service_instances[0])}))

    @wsme_pecan.wsexpose(ChainServiceInstanceResp, wtypes.text, wtypes.text, wtypes.text, ChainServiceInstance)
    def put(self, chain_id, chain_service_id, service_instance_id, service_instance):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the updated record.
        """
        service_instances = list(self.conn.get_chain_service_instances(service_instance_id=service_instance_id,
                                                                       chain_service_id=chain_service_id,
                                                                       chain_id=chain_id))
        if len(service_instances) < 1:
            raise EntityNotFound(_('Service Instance'), service_instance_id)
        else:
            service_instance.id = service_instance_id
            service_instance.chain_id = chain_id
            service_instance.chain_service_id = chain_service_id

        old_service = ChainServiceInstance.from_db_model(service_instances[0]).\
            as_dict(api_models.ChainServiceInstance)
        updated_service = service_instance.as_dict(api_models.ChainServiceInstance)
        old_service.update(updated_service)
        try:
            service_in = api_models.ChainServiceInstance(**old_service)
        except Exception:
            LOG.exception("Error while putting service: %s" % old_service)
            error = _("Network Service incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service_out = self.conn.update_chain_service_instance(service_in)
        chains = list(self.conn.get_chains(chain_id=chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), chain_id)

        chain_service = list(self.conn.get_chain_services(chain_service_id=chain_service_id,
                                                          chain_id=chain_id))

        if len(chain_service) < 1:
            error = _("Chain Service with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service = list(self.conn.get_services(service_id=chain_service[0].service_id))

        if len(service) < 1:
            error = _("Network Service with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        instance = list(self.cns_conn.get_virtualmachines(vm_id=service_instance.instance_id))
        if len(instance) < 1:
            error = _("instance with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            chain = chains[0]
            body = service_out.as_dict()
            body['name'] = instance[0].name

            ucm_record = utils.generate_ucm_data(self, body, (str(chain.name),
                                                              str(chain.tenant),
                                                              str(service[0].name)))
            if UCM_LOADED:
                try:
                    req = {'instance_name': {'type': constants.DATA_TYPES['string'], 'value': str(instance[0].name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain.name),
                                                                                  str(chain.tenant),
                                                                                  str(service[0].name))}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find service instance record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find service instance record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to update service instance record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update service instance record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return ChainServiceInstanceResp(**(
            {'service_instance': ChainServiceInstance.from_db_model(service_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, wtypes.text, wtypes.text, status_code=204)
    def delete(self, chain_id, chain_service_id, service_instance_id):
        """Delete this Network Service Instance."""
        # ensure service instance exists before deleting
        service_instances = list(self.conn.get_chain_service_instances(
            chain_service_id=chain_service_id,
            chain_id=chain_id,
            service_instance_id=service_instance_id))

        if len(service_instances) < 1:
            raise EntityNotFound(_('Chain Service'), chain_service_id)

        chains = list(self.conn.get_chains(chain_id=chain_id))
        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), chain_id)

        chain_service = list(self.conn.get_chain_services(chain_service_id=chain_service_id,
                                                          chain_id=chain_id))

        if len(chain_service) < 1:
            error = _("Chain Service with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service = list(self.conn.get_services(service_id=chain_service[0].service_id))

        if len(service) < 1:
            error = _("Network Service with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        instance = list(self.cns_conn.get_virtualmachines(vm_id=service_instances[0].instance_id))
        if len(instance) < 1:
            error = _("instance with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        self.conn.delete_chain_service_instance(service_instance_id=service_instance_id)

        #UCM Configuration Start
        chain = chains[0]
        record = {'instance_name': {'type': constants.DATA_TYPES['string'], 'value': str(instance[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain.name),
                                                                         str(chain.tenant),
                                                                         str(service[0].name))}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete service instance record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete service instance record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End


class ChainService(_Base):
    """
    Representation of Chain Network Service Map Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the service map"

    name = BoundedStr(maxlen=255)
    "The name for the network service"

    sequence_number = int
    "Sequence Number of the network service"

    chain_id = BoundedStr(minlen=36, maxlen=36)
    "chain id to which this bypass rule belongs"

    service_id = BoundedStr(minlen=36, maxlen=36)
    "Service id of network service"


class ChainServicesResp(_Base):
    """
    Representation of Chain Service Map list Response
    """
    chain_services = [ChainService]


class ChainServiceResp(_Base):
    """
    Representation of Chain Service Map Response
    """
    chain_service = ChainService


class ChainServicesController(BaseController):
    ATTRIBUTES = {
        'srvname': ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'sequencenumber': ['sequence_number', {'type': 'uint', 'mandatory': False}]
    }
    dmpath = 'nsrm.chain{name=%s,tenant=%s}.services'
    instance = ChainServiceInstancesController()

    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()

    @wsme_pecan.wsexpose(ChainServiceResp, wtypes.text, ChainService)
    def post(self, chain_id, chain_service):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = chain_service.as_dict(api_models.ChainService)
        change['chain_id'] = chain_id

        chain_services = list(self.conn.get_chain_services(chain_service_id=chain_service.id,
                                                           chain_id=chain_id))

        if len(chain_services) > 0:
            error = _("Chain Service with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chains = list(self.conn.get_chains(chain_id=chain_id))

        service = list(self.conn.get_services(service_id=chain_service.service_id))

        if len(service) < 1:
            error = _("Network Service with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            service_in = api_models.ChainService(**change)
        except Exception:
            LOG.exception("Error while posting Network Service: %s" % change)
            error = _("Network service incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service_out = self.conn.create_chain_service(service_in)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = service_out.as_dict()
            body['name'] = str(service[0].name)
            ucm_record = utils.generate_ucm_data(self, body,
                                                 (str(chains[0].name),
                                                  str(chains[0].tenant)))
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain services record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add chain services record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return ChainServiceResp(**(
            {'chain_service': ChainService.from_db_model(service_out)}))

    @wsme_pecan.wsexpose(ChainServicesResp, wtypes.text)
    def get_all(self, chain_id):
        """Return all Network Services, based on the query provided.

        :param q: Filter rules for the chains to be returned.
        """
        #TODO: Need to handle Query filters
        return ChainServicesResp(**(
            {'chain_services': [ChainService.from_db_model(m)
                                for m in self.conn.get_chain_services(chain_id=chain_id)]}))

    @wsme_pecan.wsexpose(ChainServiceResp, wtypes.text, wtypes.text)
    def get_one(self, chain_id, chain_service_id):
        """Return this Chain Network Service."""
        chain_services = list(self.conn.get_chain_services(chain_service_id=chain_service_id))

        if len(chain_services) < 1:
            chain_services = list(self.conn.get_chain_services(chain_service_id=chain_service_id, chain_id=chain_id))
            if len(chain_services) < 1:
                raise EntityNotFound(_('Chain Service'), chain_service_id)

        return ChainServiceResp(**(
            {'chain_service': ChainService.from_db_model(chain_services[0])}))

    @wsme_pecan.wsexpose(ChainServiceResp, wtypes.text, wtypes.text, ChainService)
    def put(self, chain_id, chain_service_id, chain_service):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the updated record.
        """
        chain_services = list(self.conn.get_chain_services(chain_service_id=chain_service_id))
        srvs = list(self.conn.get_services(name=chain_service_id))

        if len(chain_services) < 1:
            chain_services = list(self.conn.get_chain_services(service_id=srvs[0].id, chain_id=chain_id))
            if len(chain_services) < 1:
                raise EntityNotFound(_('Chain Service'), chain_services)
            else:
                chain_service.name = chain_service_id
        else:
            chain_service.id = chain_service_id

        old_service = ChainService.from_db_model(chain_services[0]).\
            as_dict(api_models.ChainService)
        updated_service = chain_service.as_dict(api_models.ChainService)
        old_service.update(updated_service)
        try:
            service_in = api_models.ChainService(**old_service)
        except Exception:
            LOG.exception("Error while putting service: %s" % old_service)
            error = _("Network Service incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service_out = self.conn.update_chain_service(service_in)
        chains = list(self.conn.get_chains(chain_id=chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), chain_id)

        service = list(self.conn.get_services(service_id=service_out.service_id))

        if len(service) < 1:
            error = _("Network Service with the given id doesn't exist")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            chain = chains[0]
            body = service_out.as_dict()
            body['name'] = str(service[0].name)
            ucm_record = utils.generate_ucm_data(self, body, (str(chain.name),
                                                              str(chain.tenant)))
            if UCM_LOADED:
                try:
                    req = {'srvname': {'type': constants.DATA_TYPES['string'], 'value': str(service[0].name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain.name),
                                                                                  str(chain.tenant))}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find chain service record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find chain service record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to update chain service record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update chain service record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return ChainServiceResp(**(
            {'service': ChainService.from_db_model(service_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, wtypes.text, status_code=204)
    def delete(self, chain_id, chain_service_id):
        """Delete this Network Service."""
        # ensure service exists before deleting
        services = list(self.conn.get_chain_services(
            chain_service_id=chain_service_id,
            chain_id=chain_id))

        if len(services) < 1:
            srvs = list(self.conn.get_services(name=chain_service_id))
            if len(services) < 1:
                raise EntityNotFound(_('Chain Service'), chain_service_id)
            services = list(self.conn.get_chain_services(service_id=srvs[0].id, chain_id=chain_id))
            if len(services) < 1:
                raise EntityNotFound(_('Chain Service'), chain_service_id)
            else:
                self.conn.delete_chain_service(chain_service_id=services[0].id)
        else:
            srvs = list(self.conn.get_services(service_id=services[0].service_id))
            self.conn.delete_chain_service(chain_service_id=services[0].id)

        chains = list(self.conn.get_chains(chain_id=chain_id))

        #UCM Configuration Start
        chain = chains[0]
        record = {'srvname': {'type': constants.DATA_TYPES['string'], 'value': str(srvs[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain.name),
                                                                         str(chain.tenant))}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete chain record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete chain record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End


class ChainBypassRule(_Base):
    """
    Representation of Chain Bypass Rule Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the chain"

    name = BoundedStr(maxlen=255)
    "The name for the chain"

    tenant = BoundedStr(minlen=32, maxlen=32)
    "The Tenant UUID to which the Virtual machine belongs"

    eth_type = BoundedStr(maxlen=10)
    "Ethernet Type. values supported are Any or Single"

    eth_value = int
    "Ethernet protocol value"

    src_mac_type = BoundedStr(maxlen=10)
    "Source MAC Address type. Values supported are Any or Single"

    src_mac = BoundedStr(maxlen=32)
    "Source MAC Address"

    dst_mac_type = BoundedStr(maxlen=10)
    "Destination MAC Address type (Any or single)."

    dst_mac = BoundedStr(maxlen=32)
    "Destination MAC Address"

    sip_type = BoundedStr(maxlen=10)
    "Source IP Address type (Any, single, range, subnet)"

    sip_start = BoundedStr(maxlen=50)
    "Source IP Address or Start IP Address"

    sip_end = BoundedStr(maxlen=50)
    "Source End IP Address or Network mask"

    dip_type = BoundedStr(maxlen=10)
    "Destination IP Address type (Any, single, range, subnet)"

    dip_start = BoundedStr(maxlen=50)
    "Destination IP Address or Start IP Address"

    dip_end = BoundedStr(maxlen=50)
    "Destination End IP Address or Network mask"

    sp_type = BoundedStr(maxlen=10)
    "Source Port type (Any ,single, range)"

    sp_start = int
    "Source Port number or start port number"

    sp_end = int
    "Source End Port number"

    dp_type = BoundedStr(maxlen=10)
    "Destination Port type (Any ,single, range)"

    dp_start = int
    "Destination Port number or Destination starting port number"

    dp_end = int
    "Destination End port number"

    protocol = int
    "protocol value"

    nwservice_count = int
    "Network service appliances count"

    nwservice_names = wtypes.text
    "Network service appliance names (comma separated)"

    admin_status = bool
    "Admin status for this rule"

    chain_id = BoundedStr(minlen=36, maxlen=36)
    "chain id to which this bypass rule belongs"


class ChainBypassRulesResp(_Base):
    """
    Representation of Chain Bypass Rules list Response
    """
    chain_bypass_rules = [ChainBypassRule]


class ChainBypassRuleResp(_Base):
    """
    Representation of Chain Bypass Rule Response
    """
    chain_bypass_rule = ChainBypassRule


class ChainBypassRuleController(BaseController):
    ATTRIBUTES = {
        'bypassname': ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'location': ['location', {'type': 'string', 'mandatory': True}],
        'relative_name': ['name', {'type': 'string', 'mandatory': False}],
        'srcmactype': ['src_mac_type', {'type': 'string', 'mandatory': False}],
        'srcmac': ['src_mac', {'type': 'string', 'mandatory': False}],
        'dstmactype': ['dst_mac_type', {'type': 'string', 'mandatory': False}],
        'dstmac': ['dst_mac', {'type': 'string', 'mandatory': False}],
        'ethtype': ['eth_type', {'type': 'string', 'mandatory': False}],
        'ethtypevalue': ['eth_value', {'type': 'string', 'mandatory': False}],
        'siptype': ['sip_type', {'type': 'string', 'mandatory': False}],
        'sipstart': ['sip_start', {'type': 'ipaddr', 'mandatory': False}],
        'sipend': ['sip_end', {'type': 'ipaddr', 'mandatory': False}],
        'diptype': ['dip_type', {'type': 'string', 'mandatory': False}],
        'dipstart': ['dip_start', {'type': 'ipaddr', 'mandatory': False}],
        'dipend': ['dip_end', {'type': 'ipaddr', 'mandatory': False}],
        'sptype': ['sp_type', {'type': 'string', 'mandatory': False}],
        'spstart': ['sp_start', {'type': 'uint', 'mandatory': False}],
        'spend': ['sp_end', {'type': 'uint', 'mandatory': False}],
        'dptype': ['dp_type', {'type': 'string', 'mandatory': False}],
        'dpstart': ['dp_start', {'type': 'uint', 'mandatory': False}],
        'dpend': ['dp_end', {'type': 'uint', 'mandatory': False}],
        'protocol': ['protocol', {'type': 'uint', 'mandatory': False}],
        'enabled': ['admin_status', {'type': 'boolean', 'mandatory': False}],
    }
    dmpath = 'nsrm.chain{name=%s,tenant=%s}.bypassrule'

    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()

    @wsme_pecan.wsexpose(ChainBypassRuleResp, wtypes.text, ChainBypassRule)
    def post(self, chain_id, chain_bypass_rule):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        change = chain_bypass_rule.as_dict(api_models.ChainBypassRule)

        rules = list(self.conn.get_chain_bypass_rules(chain_id=chain_id,
                                                      rule_id=change['id'],
                                                      name=change['name']))

        if len(rules) > 0:
            error = _("Chain Bypass rule with the given id and name exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        change['chain_id'] = chain_id

        try:
            rule_in = api_models.ChainBypassRule(**change)
        except Exception:
            LOG.exception("Error while posting Chain Bypass rule: %s" % change)
            error = _("Chain Bypass rule incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        rule_out = self.conn.create_chain_bypass_rule(rule_in)

        chains = list(self.conn.get_chains(chain_id=chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), chain_id)
        chain = chains[0]
        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = rule_out.as_dict()
            body['location'] = 'LAST'
            ucm_record = utils.generate_ucm_data(self, body, (str(chain.name),
                                                              str(chain.tenant)))
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain bypass rule to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add chain bypass rule to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))

                try:
                    for srv in body['nwservice_names'].split(','):
                        chain_service = list(self.conn.get_chain_services(chain_id=str(chain.id),
                                                                          chain_service_id=str(srv)))[0]
                        service = list(self.conn.get_services(service_id=chain_service.service_id))[0]
                        record = {'servicename': {'type': constants.DATA_TYPES['string'], 'value': str(service.name)},
                                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain.name),
                                                                                         str(chain.tenant))
                                            + '{' + body['name'] + '}.bypass_services'}
                        ret_val = _ucm.add_record(record)
                        if ret_val != 0:
                            error = _("Unable to add chain bypass service to UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add chain bypass service to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return ChainBypassRuleResp(**(
            {'chain_bypass_rule': ChainBypassRule.from_db_model(rule_out)}))

    @wsme_pecan.wsexpose(ChainBypassRulesResp, wtypes.text, [ChainBypassRule])
    def get_all(self, chain_id):
        """Return all chain Bypass rules for a particular chain, based on the query provided.

        :param q: Filter rules for the chains to be returned.
        """
        #TODO: Need to handle Query filters
        rules = [ChainBypassRule.from_db_model(m)
                 for m in self.conn.get_chain_bypass_rules(chain_id=chain_id)]
        return ChainBypassRulesResp(**(
            {'chain_bypass_rules': rules}))

    @wsme_pecan.wsexpose(ChainBypassRuleResp, wtypes.text, wtypes.text)
    def get_one(self, chain_id, rule_id):
        """Return this chain Bypass Rule."""
        rules = list(self.conn.get_chain_bypass_rules(chain_id=chain_id,
                                                      rule_id=rule_id))

        if len(rules) < 1:
            raise EntityNotFound(_('Chain Bypass Rule'), rule_id)

        return ChainBypassRuleResp(**(
            {'chain_bypass_rule': ChainBypassRule.from_db_model(rules[0])}))

    @wsme_pecan.wsexpose(ChainBypassRuleResp, wtypes.text, wtypes.text, ChainBypassRule)
    def put(self, chain_id, rule_id, chain_bypass_rule):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the updated record.
        """
        chain_bypass_rule.chain_id = chain_id
        chain_bypass_rule.id = rule_id
        rules = list(self.conn.get_chain_bypass_rules(chain_id=chain_id,
                                                      rule_id=rule_id))

        if len(rules) < 1:
            raise EntityNotFound(_('Chain Bypass Rule'), rule_id)

        old_rule = ChainBypassRule.from_db_model(rules[0]).\
            as_dict(api_models.ChainBypassRule)
        updated_rule = chain_bypass_rule.as_dict(api_models.ChainBypassRule)
        old_rule.update(updated_rule)
        try:
            rule_in = api_models.ChainBypassRule(**old_rule)
        except Exception:
            LOG.exception("Error while putting chain bypass rule: "
                          "%s" % old_rule)
            error = _("Chain Bypass Rule incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        rule_out = self.conn.update_chain_bypass_rule(rule_in)
        chains = list(self.conn.get_chains(chain_id=chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain Bypass rule'), chain_id)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            chain = chains[0]
            body = rule_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, (str(chain.name),
                                                              str(chain.tenant)))
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(rule_out.name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain.name),
                                                                                  str(chain.tenant))}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find chain bypass rule in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find chain bypass rule in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain bypass rule to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update chain bypass rule to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return ChainBypassRuleResp(**(
            {'chain_bypass_rule': ChainBypassRule.from_db_model(rule_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, wtypes.text, status_code=204)
    def delete(self, chain_id, rule_id):
        """Delete this Chain Bypass Rule."""
        # ensure rule exists before deleting
        rules = list(self.conn.get_chain_bypass_rules(chain_id=chain_id,
                                                      rule_id=rule_id))

        if len(rules) < 1:
            rules = list(self.conn.get_chain_bypass_rules(chain_id=chain_id,
                                                          name=rule_id))
            if len(rules) < 1:
                raise EntityNotFound(_('Chain Bypass Rule'), rule_id)

        self.conn.delete_chain_bypass_rule(rules[0].id)

        chains = list(self.conn.get_chains(chain_id=chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), chain_id)

        #UCM Configuration Start
        chain = chains[0]
        record = {'bypassname': {'type': constants.DATA_TYPES['string'], 'value': str(rules[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain.name),
                                                                         str(chain.tenant))}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete chain bypass rule from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete chain bypass rule from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End


class Chain(_Base):
    """
    Representation of Chain Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the chain"

    name = BoundedStr(maxlen=255)
    "The name for the chain"

    tenant = BoundedStr(minlen=32, maxlen=32)
    "The Tenant UUID to which the Virtual machine belongs"

    admin_status = bool
    "Admin status"


class ChainsResp(_Base):
    """
    Representation of Chains list Response
    """
    chains = [Chain]


class ChainResp(_Base):
    """
    Representation of Chain Response
    """
    chain = Chain


class ChainController(BaseController):
    ATTRIBUTES = {
        'name': ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'tenant': ['tenant', {'type': 'string', 'mandatory': True, 'key': True}],
        'enabled': ['admin_status', {'type': 'boolean', 'mandatory': False}],
    }
    dmpath = 'nsrm.chain'
    bypassrules = ChainBypassRuleController()
    services = ChainServicesController()

    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()

    @wsme_pecan.wsexpose(ChainResp, Chain)
    def post(self, chain):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = chain.as_dict(api_models.Chain)

        chains = list(self.conn.get_chains(chain_id=chain.id))

        if len(chains) > 0:
            error = _("Chain with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            chain_in = api_models.Chain(**change)
        except Exception:
            LOG.exception("Error while posting Chain: %s" % change)
            error = _("Chain incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chain_out = self.conn.create_chain(chain_in)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = chain_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(chain_out.tenant)},
                       'dmpath': constants.PATH_PREFIX + '.crm.tenant'}
                try:
                    comp_req = copy.deepcopy(req)
                    rec = _ucm.get_exact_record(req)
                    if not rec:
                        ret_val = _ucm.add_record(comp_req)
                        if ret_val != 0:
                            error = _("Unable to add tenant record to UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to find chain record in UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))

                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add chain record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
                    # UCM Configuration End

        return ChainResp(**({'chain': Chain.from_db_model(chain_out)}))

    @wsme_pecan.wsexpose(ChainsResp, [Chain])
    def get_all(self):
        """Return all chains, based on the query provided.

        :param q: Filter rules for the chains to be returned.
        """
        #TODO: Need to handle Query filters
        return ChainsResp(**({'chains': [Chain.from_db_model(m)
                                         for m in self.conn.get_chains()]}))

    @wsme_pecan.wsexpose(ChainResp, wtypes.text)
    def get_one(self, chain_id):
        """Return this chain."""
        chains = list(self.conn.get_chains(chain_id=chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), chain_id)

        return ChainResp(**({'chain': Chain.from_db_model(chains[0])}))

    @wsme_pecan.wsexpose(ChainResp, wtypes.text, Chain)
    def put(self, chain_id, chain):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        chain.id = chain_id
        chains = list(self.conn.get_chains(chain_id=chain.id))

        if len(chains) < 1:
            raise EntityNotFound(_('Chain'), chain_id)

        old_chain = Chain.from_db_model(chains[0]).as_dict(api_models.Chain)
        updated_chain = chain.as_dict(api_models.Chain)
        old_chain.update(updated_chain)
        try:
            chain_in = api_models.Chain(**old_chain)
        except Exception:
            LOG.exception("Error while putting chain: %s" % old_chain)
            error = _("Chain incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chain_out = self.conn.update_chain(chain_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = chain_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(chain_out.name)},
                           'tenant': {'type': constants.DATA_TYPES['string'], 'value': str(chain_out.tenant)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find chain record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find chain record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update chain record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return ChainResp(**({'chain': Chain.from_db_model(chain_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, chain_id):
        """Delete this Chain."""
        # ensure chain exists before deleting
        chains = list(self.conn.get_chains(chain_id=chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), chain_id)

        self.conn.delete_chain(chains[0].id)

        #UCM Configuration Start
        chain = chains[0]
        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(chain.name)},
                  'tenant': {'type': constants.DATA_TYPES['string'], 'value': str(chain.tenant)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete chain record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete chain record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
            #UCM Configuration End

