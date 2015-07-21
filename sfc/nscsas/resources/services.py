import wsme
from pecan import response
from wsme import types as wtypes
from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _

import wsmeext.pecan as wsme_pecan
from nscs.nscsas.api.resources.base import BaseController, _Base, \
    BoundedStr, EntityNotFound
from . import model as api_models
from . import db as sfc_db
from nscs.nscsas.api import utils, constants


LOG = logging.getLogger(__name__)

#UCM Support Start
UCM_LOADED = False
if cfg.CONF.api.ucm_support:
    try:
        import _ucm as ucm
        UCM_LOADED = True
    except ImportError:
        LOG.info(_("Unable to Load UCM"))
#UCM Support End


class Service(_Base):
    """
    Representation of Service Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the Network Service"

    name = BoundedStr(maxlen=255)
    "The name for the Network Service"

    tenant = BoundedStr(minlen=32, maxlen=32)
    "The Tenant UUID to which the Virtual machine belongs"

    form_factor_type = BoundedStr(maxlen=10)
    "Network Service form factor type. physical or virtual"

    type = BoundedStr(maxlen=10)
    "Appliance Type"

    load_share_algorithm = BoundedStr(maxlen=32)
    "Load Sharing Algorithm. Hash based, round robin or least connections"

    load_indication_type = BoundedStr(maxlen=32)
    "Load indication type. Connection based or traffic based"

    high_threshold = long
    "High Threshold Value"

    low_threshold = long
    "Low Threshold Value"

    pkt_field_to_hash = BoundedStr(maxlen=255)
    "Packet field to hash"

    admin_status = bool
    "Admin status"


class ServicesResp(_Base):
    """
    Representation of Network Services list Response
    """
    services = [Service]


class ServiceResp(_Base):
    """
    Representation of Network Service Response
    """
    service = Service


class ServiceController(BaseController):

    ATTRIBUTES = {
        'name': ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'tenant': ['tenant', {'type': 'string', 'mandatory': True,
                              'key': True}],
        'formfactortype': ['form_factor_type', {'type': 'string',
                                                'mandatory': False,
                                                'default': 'Virtual'}],
        'enabled': ['admin_status', {'type': 'boolean', 'mandatory': False}],
    }
    dmpath = 'nsrm.service'

    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()

    @wsme_pecan.wsexpose(ServiceResp, Service)
    def post(self, service):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = service.as_dict(api_models.Service)

        services = list(self.conn.get_services(service_id=service.id))

        if len(services) > 0:
            error = _("Network Service with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        if change['form_factor_type'].lower() == 'physical':
            change['form_factor_type'] = 'Physical'
        elif change['form_factor_type'].lower() == 'virtual':
            change['form_factor_type'] = 'Virtual'

        change['type'] = change['type'].capitalize()
        if change['load_share_algorithm'].lower() == 'round_robin':
            change['load_share_algorithm'] = 'Round_Robin'
        elif change['load_share_algorithm'].lower() == 'hash_based':
            change['load_share_algorithm'] = 'Hash_Based'
        elif change['load_share_algorithm'].lower() == 'least_connections':
            change['load_share_algorithm'] = 'Least_Connections'

        if change['load_indication_type'].lower() == 'connection_based':
            change['load_indication_type'] = 'Connection_Based'
        elif change['load_indication_type'].lower() == 'traffic_based':
            change['load_indication_type'] = 'Traffic_Based'

        try:
            service_in = api_models.Service(**change)
        except Exception:
            LOG.exception("Error while posting Network Service: %s" % change)
            error = _("Network service incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service_out = self.conn.create_service(service_in)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = service_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    ret_val = ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except ucm.UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add chain record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return ServiceResp(**(
            {'service': Service.from_db_model(service_out)}))

    @wsme_pecan.wsexpose(ServicesResp, [Service])
    def get_all(self):
        """Return all Network Services, based on the query provided.

        :param q: Filter rules for the Network services to be returned.
        """
        #TODO: Need to handle Query filters
        return ServicesResp(**(
            {'services': [Service.from_db_model(m)
                          for m in self.conn.get_services()]}))

    @wsme_pecan.wsexpose(Service, wtypes.text)
    def get_one(self, service_id):
        """Return this Network Service."""
        services = list(self.conn.get_services(service_id=service_id))

        if len(services) < 1:
            services = list(self.conn.get_services(name=service_id))
            if len(services) < 1:
                raise EntityNotFound(_('Service'), service_id)

        return ServiceResp(**(
            {'service': Service.from_db_model(services[0])}))

    @wsme_pecan.wsexpose(ServiceResp, wtypes.text, Service)
    def put(self, service_id, service):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        services = list(self.conn.get_services(service_id=service_id))

        if len(services) < 1:
            services = list(self.conn.get_services(name=service_id))
            if len(services) < 1:
                raise EntityNotFound(_('Service'), services)
            else:
                service.name = service_id
        else:
            service.id = service_id

        old_service = Service.from_db_model(services[0]).\
            as_dict(api_models.Service)
        updated_service = service.as_dict(api_models.Service)
        old_service.update(updated_service)
        try:
            service_in = api_models.Service(**old_service)
        except Exception:
            LOG.exception("Error while putting service: %s" % old_service)
            error = _("Network Service incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        service_out = self.conn.update_service(service_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = service_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(service_out.name)},
                           'tenant': {'type': constants.DATA_TYPES['string'], 'value': str(service_out.tenant)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find service record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except ucm.UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find service record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add service record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except ucm.UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update service record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return ServiceResp(**(
            {'service': Service.from_db_model(service_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, service_id):
        """Delete this Network Service."""
        # ensure service exists before deleting
        services = list(self.conn.get_services(service_id=service_id))

        if len(services) < 1:
            services = list(self.conn.get_services(name=service_id))
            if len(services) < 1:
                raise EntityNotFound(_('Service'), service_id)
            else:
                self.conn.delete_service(name=service_id)
        else:
            self.conn.delete_service(service_id=service_id)

        #UCM Configuration Start
        service = services[0]
        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(service.name)},
                  'tenant': {'type': constants.DATA_TYPES['string'], 'value': str(service.tenant)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = ucm.delete_record(record)
            if ret_val != 0:
                error = _("Unable to delete service record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except ucm.UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete service record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End

