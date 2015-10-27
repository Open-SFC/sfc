import wsme
from pecan import request, response
from wsme import types as wtypes
from oslo_config import cfg
from oslo_log import log as logging
from oslo_log._i18n import _

import wsmeext.pecan as wsme_pecan
from nscs.nscsas.api import utils, constants
from nscs.nscsas.api.resources.base import BaseController, _Base, \
    BoundedStr, EntityNotFound
from . import db as sfc_db
from . import model as api_models
from cns.nscsas.resources import db as cns_db


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


class ChainSelRule(_Base):
    """
    Representation of Chain Selection Rule Structure
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

    admin_status = bool
    "Admin status for this rule"

    chain_id = BoundedStr(minlen=36, maxlen=36)
    "chain id to which this bypass rule belongs"

    chain_set_id = BoundedStr(minlen=36, maxlen=36)
    "chain id to which this bypass rule belongs"


class ChainSelRulesResp(_Base):
    """
    Representation of Chain Bypass Rules list Response
    """
    chain_selection_rules = [ChainSelRule]


class ChainSelRuleResp(_Base):
    """
    Representation of Chain Bypass Rule Response
    """
    chain_selection_rule = ChainSelRule


class ChainSelRuleController(BaseController):
    ATTRIBUTES = {
        'selname': ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'location': ['location', {'type': 'string', 'mandatory': True}],
        'chain': ['chain', {'type': 'string', 'mandatory': True}],
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
    dmpath = 'nsrm.chainset{name=%s,tenant=%s}.chainselrule'

    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()
        self.cns_conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(ChainSelRuleResp, wtypes.text, ChainSelRule)
    def post(self, chain_set_id, chain_selection_rule):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        change = chain_selection_rule.as_dict(api_models.ChainSelRule)

        rules = list(self.conn.get_chain_sel_rules(chain_set_id=chain_set_id,
                                                   rule_id=change['id'],
                                                   name=change['name']))

        if len(rules) > 0:
            error = _("Chain Selection rule with the given id and name exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        change['chain_set_id'] = chain_set_id

        try:
            rule_in = api_models.ChainSelRule(**change)
        except Exception:
            LOG.exception("Error while posting Chain Selection rule: %s" % change)
            error = _("Chain Selection rule incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        rule_out = self.conn.create_chain_sel_rule(rule_in)

        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('Chain Set'), chain_set_id)

        chains = list(self.conn.get_chains(chain_id=rule_out.chain_id))

        if len(chains) < 1:
            chains = list(self.conn.get_chains(name=rule_out.chain_id))
            if len(chains) < 1:
                raise EntityNotFound(_('Chain'), rule_out.chain_id)
        chain = chains[0]
        chain_set = chain_sets[0]
        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = rule_out.as_dict()
            body['location'] = 'LAST'
            body['chain'] = chain.name
            ucm_record = utils.generate_ucm_data(self, body, (str(chain_set.name),
                                                              str(chain_set.tenant)))
            if UCM_LOADED:
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

        return ChainSelRuleResp(**(
            {'chain_selection_rule': ChainSelRule.from_db_model(rule_out)}))

    @wsme_pecan.wsexpose(ChainSelRulesResp, wtypes.text, [ChainSelRule])
    def get_all(self, chain_set_id):
        """Return all chain Bypass rules for a particular chain, based on the query provided.

        :param q: Filter rules for the chains to be returned.
        """
        #TODO: Need to handle Query filters
        rules = [ChainSelRule.from_db_model(m)
                 for m in self.conn.get_chain_sel_rules(chain_set_id=chain_set_id)]
        return ChainSelRulesResp(**(
            {'chain_selection_rules': rules}))

    @wsme_pecan.wsexpose(ChainSelRuleResp, wtypes.text, wtypes.text)
    def get_one(self, chain_set_id, rule_id):
        """Return this chain Bypass Rule."""
        rules = list(self.conn.get_chain_sel_rules(chain_set_id=chain_set_id,
                                                   rule_id=rule_id))

        if len(rules) < 1:
            rules = list(self.conn.get_chain_sel_rules(chain_set_id=chain_set_id,
                                                       name=rule_id))
            if len(rules) < 1:
                raise EntityNotFound(_('Chain Selection Rule'), rule_id)

        return ChainSelRuleResp(**(
            {'chain_selection_rule': ChainSelRule.from_db_model(rules[0])}))

    @wsme_pecan.wsexpose(ChainSelRuleResp, wtypes.text, wtypes.text, ChainSelRule)
    def put(self, chain_set_id, rule_id, chain_selection_rule):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the updated record.
        """

        rules = list(self.conn.get_chain_sel_rules(chain_set_id=chain_set_id,
                                                   rule_id=rule_id))

        if len(rules) < 1:
            rules = list(self.conn.get_chain_sel_rules(chain_set_id=chain_set_id,
                                                       name=rule_id))
            if len(rules) < 1:
                raise EntityNotFound(_('Chain Selection Rule'), rule_id)

        chain_selection_rule.chain_set_id = chain_set_id
        chain_selection_rule.id = rules[0].id

        old_rule = ChainSelRule.from_db_model(rules[0]).\
            as_dict(api_models.ChainSelRule)
        updated_rule = chain_selection_rule.as_dict(api_models.ChainSelRule)
        old_rule.update(updated_rule)
        try:
            rule_in = api_models.ChainSelRule(**old_rule)
        except Exception:
            LOG.exception("Error while putting chain selection rule: "
                          "%s" % old_rule)
            error = _("Chain Selection Rule incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        rule_out = self.conn.update_chain_sel_rule(rule_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

            if len(chain_sets) < 1:
                chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
                if len(chain_sets) < 1:
                    raise EntityNotFound(_('Chain Set'), chain_set_id)
            chains = list(self.conn.get_chains(chain_id=rule_out.chain_id))

            if len(chains) < 1:
                chains = list(self.conn.get_chains(name=rule_out.chain_id))
                if len(chains) < 1:
                    raise EntityNotFound(_('Chain'), rule_out.chain_id)
            chain = chains[0]

            chain_set = chain_sets[0]
            body = rule_out.as_dict()
            body['location'] = 'LAST'
            body['chain'] = chain.name
            ucm_record = utils.generate_ucm_data(self, body, (str(chain_set.name),
                                                              str(chain_set.tenant)))
            if UCM_LOADED:
                try:
                    req = {'selname': {'type': constants.DATA_TYPES['string'], 'value': str(rule_out.name)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain_set.name),
                                                                                  str(chain_set.tenant))}
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

        return ChainSelRuleResp(**(
            {'chain_selection_rule': ChainSelRule.from_db_model(rule_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, wtypes.text, status_code=204)
    def delete(self, chain_set_id, rule_id):
        """Delete this Chain Bypass Rule."""
        # ensure rule exists before deleting
        rules = list(self.conn.get_chain_sel_rules(chain_set_id=chain_set_id,
                                                   rule_id=rule_id))

        if len(rules) < 1:
            rules = list(self.conn.get_chain_sel_rules(chain_set_id=chain_set_id,
                                                       name=rule_id))
            if len(rules) < 1:
                raise EntityNotFound(_('Chain Bypass Rule'), rule_id)

        self.conn.delete_chain_sel_rule(rules[0].id)

        #UCM Configuration Start
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('Chain Set'), chain_set_id)

        chain_set = chain_sets[0]
        record = {'selname': {'type': constants.DATA_TYPES['string'], 'value': str(rules[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (str(chain_set.name),
                                                                         str(chain_set.tenant))}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete chain Selection rule from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete chain Selection rule from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End


class ChainSetZone(_Base):
    """
    Representation of Chain Set Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the chain set"

    name = BoundedStr(maxlen=255)
    "The name for the chain set"

    direction = int
    "zone Direction. (1-left, 2-right)"


class ChainSetZonesResp(_Base):
    """
    Representation of Chain set Zones list Response
    """
    chainset_zones = [ChainSetZone]


class ChainSetZoneResp(_Base):
    """
    Representation of Chain Set Zone Response
    """
    chainset_zone = ChainSetZone


class ChainSetZoneController(BaseController):
    ATTRIBUTES = {
        'zone_name': ['name', {'type': 'string', 'mandatory': True,
                               'key': True}],
        'zone_direction': ['direction', {'type': 'uint', 'mandatory': False}],
    }
    dmpath = 'nsrm.chainset{name=%s,tenant=%s}.chainsetzonerule'


    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()

    @wsme_pecan.wsexpose(ChainSetZoneResp, wtypes.text, ChainSetZone)
    def post(self, chain_set_id, chainset_zone):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = chainset_zone.as_dict(api_models.ChainSetZone)

        chain_set_zones = list(self.conn.get_chain_set_zones(
            chain_set_id=chain_set_id,
            chain_set_zone_id=chainset_zone.id
            ))

        if len(chain_set_zones) > 0:
            error = _("Chain Set Zone with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        change['chain_set_id'] = chain_set_id
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('Chain Set'), chain_set_id)

        try:
            chain_set_zone_in = api_models.ChainSetZone(**change)
        except Exception:
            LOG.exception("Error while posting Chain Set Zone: %s" % change)
            error = _("Chain Set incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chain_set_zone_out = self.conn.create_chain_set_zone(chain_set_zone_in)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = chain_set_zone_out.as_dict()
            chain_set = chain_sets[0]
            ucm_record = utils.generate_ucm_data(self, body,
                                                 (str(chain_set.name),
                                                  str(chain_set.tenant)))
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain set zone record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add chain set zone record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return ChainSetZoneResp(**(
            {'chainset_zone': ChainSetZone.from_db_model(chain_set_zone_out)}))

    @wsme_pecan.wsexpose(ChainSetZonesResp, wtypes.text)
    def get_all(self, chain_set_id):
        """Return all chains, based on the query provided.

        :param q: Filter rules for the chains to be returned.
        """
        #TODO: Need to handle Query filters
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('Chain'), chain_set_id)

        chain_set_zones = []
        for m in self.conn.get_chain_set_zones(chain_set_id=chain_set_id):
            chain_set_zones.append(ChainSetZone.from_db_model(m))
        return ChainSetZonesResp(**(
            {'chainset_zones': chain_set_zones}))

    @wsme_pecan.wsexpose(ChainSetZoneResp, wtypes.text, wtypes.text)
    def get_one(self, chain_set_id, cs_zone_id):
        """Return this chain."""
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('Chain'), chain_set_id)

        cs_zone = self.conn.get_chain_set_zones(chain_set_id=chain_set_id,
                                                chain_set_zone_id=cs_zone_id)

        return ChainSetZoneResp(**(
            {'chainset_zone': ChainSetZone.from_db_model(cs_zone)}))

    @wsme_pecan.wsexpose(ChainSetZoneResp, wtypes.text, wtypes.text,
                         ChainSetZone)
    def put(self, chain_set_id, cs_zone_id, chainset_zone):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        chainset_zone.id = cs_zone_id
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            raise EntityNotFound(_('Chain Set'), chain_set_id)

        chain_set_zones = list(self.conn.get_chain_set_zones(
            chain_set_id=chain_set_id,
            chain_set_zone_id=cs_zone_id))

        if len(chain_set_zones) < 1:
            raise EntityNotFound(_('Chain Set Zone'), cs_zone_id)

        chainset_zone.chain_set_id = chain_set_id
        old_cs_zone = ChainSetZone.from_db_model(chain_set_zones[0]).as_dict(
            api_models.ChainSetZone)
        updated_cs_zone = chainset_zone.as_dict(api_models.ChainSetZone)
        old_cs_zone.update(updated_cs_zone)
        try:
            cs_zone_in = api_models.ChainSetZone(**old_cs_zone)
        except Exception:
            LOG.exception("Error while putting chain Set Zone: %s" %
                          old_cs_zone)
            error = _("Chain Set Zone incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        cs_zone_out = self.conn.update_chain_set_zone(cs_zone_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = cs_zone_out.as_dict()
            chain_set = chain_sets[0]
            ucm_record = utils.generate_ucm_data(self, body,
                                                 (str(chain_set.name),
                                                  str(chain_set.tenant)))

            if UCM_LOADED:
                try:
                    req = {'zone_name':
                                  {'type': constants.DATA_TYPES['string'],
                                   'value': str(cs_zone_out.name)},
                              'dmpath': constants.PATH_PREFIX + '.' +
                                        self.dmpath % (str(chain_set.name),
                                                       str(chain_set.tenant))}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find chain set record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find chain set record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain set record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update chain set record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return ChainSetZoneResp(**(
            {'chainset_zone': ChainSetZone.from_db_model(cs_zone_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, wtypes.text, status_code=204)
    def delete(self, chain_set_id, cs_zone_id):
        """Delete this Chain set zone."""
        # ensure chain set zone and chain set  exists before deleting
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('ChainSet'), chain_set_id)

        cs_zones = list(self.conn.get_chain_set_zones(
            chain_set_id=chain_set_id,
            chain_set_zone_id=cs_zone_id))

        if len(cs_zones) < 1:
            cs_zones = list(self.conn.get_chain_set_zones(
                chain_set_id=chain_set_id,name=cs_zone_id))
            if len(cs_zones) < 1:
                raise EntityNotFound(_('ChainSet'), chain_set_id)
        self.conn.delete_chain_set_zone(cs_zones[0].id)

        #UCM Configuration Start
        chain_set = chain_sets[0]
        record = {'zone_name': {'type': constants.DATA_TYPES['string'],
                                'value': str(cs_zones[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' +
                            self.dmpath % (str(chain_set.name),
                                           str(chain_set.tenant))}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete chain set zone record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete chain set  zone record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End


class ChainSet(_Base):
    """
    Representation of Chain Set Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the chain set"

    name = BoundedStr(maxlen=255)
    "The name for the chain set"

    tenant = BoundedStr(minlen=32, maxlen=32)
    "The Tenant UUID to which the chain set belongs"

    admin_status = bool
    "Admin status"

    zonefull = bool
    "Zone / Zone less status"

    direction = int
    "Default zone Direction. (1-left, 2-right)"


class ChainSetsResp(_Base):
    """
    Representation of Chains list Response
    """
    chain_sets = [ChainSet]


class ChainSetResp(_Base):
    """
    Representation of Chain Response
    """
    chain_set = ChainSet


class ChainSetController(BaseController):
    ATTRIBUTES = {
        'name': ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'tenant': ['tenant', {'type': 'string', 'mandatory': True,
                              'key': True}],
        'enabled': ['admin_status', {'type': 'boolean', 'mandatory': False}],
        'zone': ['zonefull', {'type': 'boolean', 'mandatory': True}],
        'zone_direction': ['direction', {'type': 'uint', 'mandatory': True}],
    }
    dmpath = 'nsrm.chainset'

    selectionrules = ChainSelRuleController()
    zones = ChainSetZoneController()

    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()

    @wsme_pecan.wsexpose(ChainSetResp, ChainSet)
    def post(self, chain_set):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = chain_set.as_dict(api_models.ChainSet)

        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set.id))

        if len(chain_sets) > 0:
            error = _("Chain with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            chain_set_in = api_models.ChainSet(**change)
        except Exception:
            LOG.exception("Error while posting Chain Set: %s" % change)
            error = _("Chain Set incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chain_set_out = self.conn.create_chain_set(chain_set_in)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = chain_set_out.as_dict()

            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    print ucm_record
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain set record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add chain set record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return ChainSetResp(**({'chain_set': ChainSet.from_db_model(chain_set_out)}))

    @wsme_pecan.wsexpose(ChainSetsResp, [ChainSet])
    def get_all(self):
        """Return all chains, based on the query provided.

        :param q: Filter rules for the chains to be returned.
        """
        #TODO: Need to handle Query filters
        return ChainSetsResp(**({'chain_sets': [ChainSet.from_db_model(m)
                                                for m in self.conn.get_chain_sets()]}))

    @wsme_pecan.wsexpose(ChainSetResp, wtypes.text)
    def get_one(self, chain_set_id):
        """Return this chain."""
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('Chain'), chain_set_id)

        return ChainSetResp(**({'chain_set': ChainSet.from_db_model(chain_sets[0])}))

    @wsme_pecan.wsexpose(ChainSetResp, wtypes.text, ChainSet)
    def put(self, chain_set_id, chain_set):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        chain_set.id = chain_set_id
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set.id))

        if len(chain_sets) < 1:
            raise EntityNotFound(_('Chain Set'), chain_set_id)

        old_chain_set = ChainSet.from_db_model(chain_sets[0]).as_dict(api_models.ChainSet)
        updated_chain_set = chain_set.as_dict(api_models.ChainSet)
        old_chain_set.update(updated_chain_set)
        try:
            chain_set_in = api_models.ChainSet(**old_chain_set)
        except Exception:
            LOG.exception("Error while putting chain Set: %s" % old_chain_set)
            error = _("Chain Set incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chain_set_out = self.conn.update_chain_set(chain_set_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = chain_set_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(chain_set_out.name)},
                           'tenant': {'type': constants.DATA_TYPES['string'], 'value': str(chain_set_out.tenant)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find chain set record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find chain set record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to update chain set record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update chain set record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return ChainSetResp(**({'chain_set': ChainSet.from_db_model(chain_set_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, chain_set_id):
        """Delete this Chain."""
        # ensure chain exists before deleting
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('Chain'), chain_set_id)

        self.conn.delete_chain_set(chain_sets[0].id)

        #UCM Configuration Start
        chain_set = chain_sets[0]
        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(chain_set.name)},
                  'tenant': {'type': constants.DATA_TYPES['string'], 'value': str(chain_set.tenant)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete chain set record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete chain set record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End


class ChainNetworkMap(_Base):
    """
    Representation of Chain Network Map Structure
    """
    id = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the chain Network Map"

    name = BoundedStr(maxlen=255)
    "The name for the chain Network Map"

    tenant = BoundedStr(minlen=32, maxlen=32)
    "The Tenant UUID to which the chain Network Map belongs"

    inbound_network = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the Inbound network"

    outbound_network = BoundedStr(minlen=36, maxlen=36)
    "The UUID of the Outbound network"

    admin_status = bool
    "Admin status"

    chain_set_id = BoundedStr(minlen=36, maxlen=36)
    "Chain Set ID to which this Network Map is mapped"


class ChainNetworkMapsResp(_Base):
    """
    Representation of Chains list Response
    """
    chain_networks = [ChainNetworkMap]


class ChainNetworkMapResp(_Base):
    """
    Representation of Chain Response
    """
    chain_network = ChainNetworkMap


class ChainNetworkMapController(BaseController):
    ATTRIBUTES = {
        'name': ['name', {'type': 'string', 'mandatory': True, 'key': True}],
        'tenant': ['tenant', {'type': 'string', 'mandatory': True, 'key': True}],
        'vnname_in': ['inbound_nw_name', {'type': 'string', 'mandatory': True, 'key': True}],
        'vnname_out': ['outbound_nw_name', {'type': 'string', 'mandatory': True, 'key': True}],
        'chainset': ['chain_set_name', {'type': 'string', 'mandatory': False}],
        'enabled': ['admin_status', {'type': 'boolean', 'mandatory': False}],
    }
    dmpath = 'nsrm.networkmap'

    def __init__(self):
        self.conn = sfc_db.SFCDBMixin()
        self.cns_conn = cns_db.CNSDBMixin()

    @wsme_pecan.wsexpose(ChainNetworkMapResp, ChainNetworkMap)
    def post(self, chain_network):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body and adds the record to DB and UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """

        change = chain_network.as_dict(api_models.ChainNetworkMap)

        chain_networks = list(self.conn.get_chain_network_maps(chain_network_id=chain_network.id))

        if len(chain_networks) > 0:
            error = _("Chain Network map with the given id exists")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        try:
            chain_network_in = api_models.ChainNetworkMap(**change)
        except Exception:
            LOG.exception("Error while posting Chain Network Map: %s" % change)
            error = _("Chain Network Map incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chain_network_out = self.conn.create_chain_network_map(chain_network_in)
        chain_sets = list(self.conn.get_chain_sets(chain_set_id=chain_network_out.chain_set_id))

        if len(chain_sets) < 1:
            chain_sets = list(self.conn.get_chain_sets(name=chain_network_out.chain_set_id))
            if len(chain_sets) < 1:
                raise EntityNotFound(_('Chain set'), chain_network_out.chain_set_id)

        inbound_nws = list(self.cns_conn.get_virtualnetworks(nw_id=chain_network_out.inbound_network))

        if len(inbound_nws) < 1:
            inbound_nws = list(self.cns_conn.get_virtualnetworks(nw_id=chain_network_out.inbound_network))
            if len(inbound_nws) < 1:
                raise EntityNotFound(_('Inbound Network'), chain_network_out.inbound_network)
            
        outbound_nws = list(self.cns_conn.get_virtualnetworks(nw_id=chain_network_out.outbound_network))

        if len(outbound_nws) < 1:
            outbound_nws = list(self.cns_conn.get_virtualnetworks(nw_id=chain_network_out.outbound_network))
            if len(outbound_nws) < 1:
                raise EntityNotFound(_('Outbound Network'), chain_network_out.outbound_network)

        # UCM Configuration Start
        if cfg.CONF.api.ucm_support:
            body = chain_network_out.as_dict()
            body['chain_set_name'] = chain_sets[0].name
            body['inbound_nw_name'] = inbound_nws[0].name
            body['outbound_nw_name'] = outbound_nws[0].name
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    ret_val = _ucm.add_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to add chain Network Map record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to add chain Network map record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        # UCM Configuration End

        return ChainNetworkMapResp(**(
            {'chain_network': ChainNetworkMap.from_db_model(chain_network_out)}))

    @wsme_pecan.wsexpose(ChainNetworkMapsResp, [ChainNetworkMap])
    def get_all(self):
        """Return all chains, based on the query provided.

        :param q: Filter rules for the chains to be returned.
        """
        #TODO: Need to handle Query filters
        return ChainNetworkMapsResp(**({'chain_networks': [ChainNetworkMap.from_db_model(m)
                                                           for m in self.conn.get_chain_network_maps()]}))

    @wsme_pecan.wsexpose(ChainNetworkMapResp, wtypes.text)
    def get_one(self, chain_network_id):
        """Return this chain."""
        chain_networks = list(self.conn.get_chain_network_maps(chain_network_id=chain_network_id))

        if len(chain_networks) < 1:
            chain_networks = list(self.conn.get_chain_network_maps(name=chain_network_id))
            if len(chain_networks) < 1:
                raise EntityNotFound(_('Chain Network map'), chain_network_id)

        return ChainNetworkMapResp(**({'chain_network': ChainNetworkMap.from_db_model(chain_networks[0])}))

    @wsme_pecan.wsexpose(ChainNetworkMapResp, wtypes.text, ChainNetworkMap)
    def put(self, chain_network_id, chain_network):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body and adds the record to UCM if all the
        UCM_ATTRIBUTES are present.

        :return: Dictionary of the added record.
        """
        chain_network.id = chain_network_id
        chain_networks = list(self.conn.get_chain_network_maps(chain_network_id=chain_network.id))

        if len(chain_networks) < 1:
            raise EntityNotFound(_('Chain Network Map'), chain_network_id)

        old_chain_nw = ChainNetworkMap.from_db_model(chain_networks[0]).as_dict(api_models.ChainNetworkMap)
        updated_chain_nw = chain_network.as_dict(api_models.ChainNetworkMap)
        old_chain_nw.update(updated_chain_nw)
        try:
            chain_nw_in = api_models.ChainNetworkMap(**old_chain_nw)
        except Exception:
            LOG.exception("Error while putting chain Network Map: %s" % old_chain_nw)
            error = _("Chain Network Map incorrect")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        chain_nw_out = self.conn.update_chain_network_map(chain_nw_in)

        #UCM Support Start
        if cfg.CONF.api.ucm_support:
            body = chain_nw_out.as_dict()
            ucm_record = utils.generate_ucm_data(self, body, [])
            if UCM_LOADED:
                try:
                    req = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(chain_nw_out.name)},
                           'tenant': {'type': constants.DATA_TYPES['string'], 'value': str(chain_nw_out.tenant)},
                           'dmpath': constants.PATH_PREFIX + '.' + self.dmpath % (chain_nw_out.type.lower())}
                    try:
                        rec = _ucm.get_exact_record(req)
                        if not rec:
                            error = _("Unable to find network map record in UCM")
                            response.translatable_error = error
                            raise wsme.exc.ClientSideError(unicode(error))
                    except UCMException, msg:
                        LOG.info(_("UCM Exception raised. %s\n"), msg)
                        error = _("Unable to find network map record in UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))

                    ret_val = _ucm.update_record(ucm_record)
                    if ret_val != 0:
                        error = _("Unable to update network map record to UCM")
                        response.translatable_error = error
                        raise wsme.exc.ClientSideError(unicode(error))
                except UCMException, msg:
                    LOG.info(_("UCM Exception raised. %s\n"), msg)
                    error = _("Unable to Update network map record to UCM")
                    response.translatable_error = error
                    raise wsme.exc.ClientSideError(unicode(error))
        #UCM Support End

        return ChainNetworkMapResp(**({'chain_network': ChainNetworkMap.from_db_model(chain_nw_out)}))

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, chain_network_id):
        """Delete this Chain."""
        # ensure chain exists before deleting
        chain_networks = list(self.conn.get_chain_network_maps(chain_network_id=chain_network_id))

        if len(chain_networks) < 1:
            chain_networks = list(self.conn.get_chain_network_maps(name=chain_network_id))
            if len(chain_networks) < 1:
                raise EntityNotFound(_('Chain Network Map'), chain_network_id)

        self.conn.delete_chain_network_map(chain_networks[0].id)

        #UCM Configuration Start
        chain_network = chain_networks[0]

        inbound_nws = list(self.cns_conn.get_virtualnetworks(nw_id=chain_network.inbound_network))

        if len(inbound_nws) < 1:
            inbound_nws = list(self.cns_conn.get_virtualnetworks(name=chain_network.inbound_network))
            if len(inbound_nws) < 1:
                raise EntityNotFound(_('Inbound Network'), chain_network.inbound_network)
            
        outbound_nws = list(self.cns_conn.get_virtualnetworks(nw_id=chain_network.outbound_network))

        if len(outbound_nws) < 1:
            outbound_nws = list(self.cns_conn.get_virtualnetworks(name=chain_network.outbound_network))
            if len(outbound_nws) < 1:
                raise EntityNotFound(_('Outbound Network'), chain_network.outbound_network)

        record = {'name': {'type': constants.DATA_TYPES['string'], 'value': str(chain_network.name)},
                  'tenant': {'type': constants.DATA_TYPES['string'], 'value': str(chain_network.tenant)},
                  'vnname_in': {'type': constants.DATA_TYPES['string'], 'value': str(inbound_nws[0].name)},
                  'vnname_out': {'type': constants.DATA_TYPES['string'], 'value': str(outbound_nws[0].name)},
                  'dmpath': constants.PATH_PREFIX + '.' + self.dmpath}
        try:
            ret_val = _ucm.delete_record(record)
            LOG.debug(_("return value = %s"), str(ret_val))
            if ret_val != 0:
                error = _("Unable to delete chain Network record from UCM")
                response.translatable_error = error
                raise wsme.exc.ClientSideError(unicode(error))
        except UCMException, msg:
            LOG.info(_("UCM Exception raised. %s"), msg)
            error = _("Unable to delete chain Network record from UCM")
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        #UCM Configuration End
