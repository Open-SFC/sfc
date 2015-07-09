# Author: Purandhar Sairam Mannidi <sairam.mp@freescale.com>

"""
SQLAlchemy models for Network Service Resource Manager.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, \
    SmallInteger

from nscs.ocas_utils.openstack.common.db.sqlalchemy import session as sa_session
from nscs.nscsas.api.resources.sfc import model as api_model

from nscs.nscsas.storage.sqlalchemy.models import Base


class Chains(Base):
    """SFC Chains"""
    __tablename__ = 'sfc_chains'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    tenant = Column(String(36), nullable=False)
    admin_status = Column(Boolean)


class ChainBypassRules(Base):
    """SFC Chain Bypass rules"""
    __tablename__ = 'sfc_chain_bypass_rules'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    tenant = Column(String(36))
    eth_type = Column(String(10))
    eth_value = Column(Integer)
    src_mac_type = Column(String(10))
    src_mac = Column(String(32))
    dst_mac_type = Column(String(10))
    dst_mac = Column(String(32))
    sip_type = Column(String(10))
    sip_start = Column(String(50))
    sip_end = Column(String(50))
    dip_type = Column(String(10))
    dip_start = Column(String(50))
    dip_end = Column(String(50))
    sp_type = Column(String(10))
    sp_start = Column(Integer)
    sp_end = Column(Integer)
    dp_type = Column(String(10))
    dp_start = Column(Integer)
    dp_end = Column(Integer)
    protocol = Column(Integer)
    nwservice_count = Column(Integer)
    nwservice_names = Column(String(2048))
    admin_status = Column(Boolean)
    chain_id = Column(String(36), ForeignKey('sfc_chains.id'))


class Services(Base):
    """SFC Network Services"""
    __tablename__ = 'sfc_services'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    tenant = Column(String(36))
    form_factor_type = Column(String(36))
    type = Column(String(10), nullable=False)
    load_share_algorithm = Column(String(32))
    load_indication_type = Column(String(32))
    high_threshold = Column(BigInteger)
    low_threshold = Column(BigInteger)
    pkt_field_to_hash = Column(String(255))
    admin_status = Column(Boolean)


class ChainServices(Base):
    """SFC Chain Services Mapping"""
    __tablename__ = 'sfc_chain_services'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    sequence_number = Column(Integer)
    chain_id = Column(String(36), ForeignKey('sfc_chains.id'))
    service_id = Column(String(36), ForeignKey('sfc_services.id'))


class ChainServiceInstances(Base):
    """SFC Chain Service Instances"""
    __tablename__ = 'sfc_chain_service_instances'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    instance_id = Column(String(36))
    vlan_in = Column(SmallInteger)
    vlan_out = Column(SmallInteger)
    chain_id = Column(String(36), ForeignKey('sfc_chains.id'))
    chain_service_id = Column(String(36), ForeignKey('sfc_chain_services.id'))


class ChainSet(Base):
    """SFC Chain Set"""
    __tablename__ = 'sfc_chain_set'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    tenant = Column(String(36))
    admin_status = Column(Boolean)


class ChainSelectionRules(Base):
    """SFC Chain selection rules"""
    __tablename__ = 'sfc_chain_selection_rules'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    tenant = Column(String(36))
    eth_type = Column(String(10))
    eth_value = Column(Integer)
    src_mac_type = Column(String(10))
    src_mac = Column(String(32))
    dst_mac_type = Column(String(10))
    dst_mac = Column(String(32))
    sip_type = Column(String(10))
    sip_start = Column(String(50))
    sip_end = Column(String(50))
    dip_type = Column(String(10))
    dip_start = Column(String(50))
    dip_end = Column(String(50))
    sp_type = Column(String(10))
    sp_start = Column(Integer)
    sp_end = Column(Integer)
    dp_type = Column(String(10))
    dp_start = Column(Integer)
    dp_end = Column(Integer)
    protocol = Column(Integer)
    admin_status = Column(Boolean)
    chain_id = Column(String(36), ForeignKey('sfc_chains.id'))
    chain_set_id = Column(String(36), ForeignKey('sfc_chain_set.id'))


class ChainNetworkMaps(Base):
    """SFC Network Maps"""
    __tablename__ = 'sfc_chain_network_maps'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    tenant = Column(String(36))
    inbound_network = Column(String(255))
    outbound_network = Column(String(255))
    admin_status = Column(Boolean)
    chain_set_id = Column(String(36), ForeignKey('sfc_chain_set.id'))


class SFCAttributes(Base):
    """SFC Attributes"""
    __tablename__ = 'sfc_attributes'
    __table_args__ = {'useexisting': True}

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    table_name = Column(String(255))
    table_id = Column(String(255))


class SFCDBMixin(object):

    @staticmethod
    def _row_to_chain(row):
        return api_model.Chain(id=row.id,
                               name=row.name,
                               tenant=row.tenant,
                               admin_status=row.admin_status)

    def create_chain(self, chain):
        """
        Insert Chain record into database

        :return:
                Chain data if the insertion is successful
                revoke transaction and raise exception
        """
        session = sa_session.get_session()
        with session.begin():
            chain_row = Chains(id=chain.id)
            chain_row.update(chain.as_dict())
            session.add(chain_row)
            session.flush()
        return self._row_to_chain(chain_row)

    def get_chains(self, chain_id=None, name=None, pagination=None):
        """
        Yields a lists of Chains that match filters

        :param name: Optional name to return one chain.
        :param chain_id: Optional chain_id to return one chain.
        :param pagination: Optional pagination query.
        """
        session = sa_session.get_session()
        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        query = session.query(Chains)
        if name is not None:
            query = query.filter(Chains.name == name)
        if chain_id is not None:
            query = query.filter(Chains.id == chain_id)

        return (self._row_to_chain(x) for x in query.all())

    def update_chain(self, chain):
        """
        Update an Chain.
        """
        session = sa_session.get_session()
        with session.begin():
            chain_row = session.merge(Chains(id=chain.id))
            chain_row.update(chain.as_dict())
            session.flush()

        return self._row_to_chain(chain_row)

    @staticmethod
    def delete_chain(chain_id):
        """
        Delete a Chain
        """
        session = sa_session.get_session()
        with session.begin():
            session.query(Chains).filter(Chains.id == chain_id).delete()
            session.flush()

    @staticmethod
    def _row_to_chain_bypass_rule(row):
        return api_model.ChainBypassRule(id=row.id,
                                         name=row.name,
                                         tenant=row.tenant,
                                         eth_type=row.eth_type,
                                         eth_value=row.eth_value,
                                         src_mac_type=row.src_mac_type,
                                         src_mac=row.src_mac,
                                         dst_mac_type=row.dst_mac_type,
                                         dst_mac=row.dst_mac,
                                         sip_type=row.sip_type,
                                         sip_start=row.sip_start,
                                         sip_end=row.sip_end,
                                         dip_type=row.dip_type,
                                         dip_start=row.dip_start,
                                         dip_end=row.dip_end,
                                         sp_type=row.sp_type,
                                         sp_start=row.sp_start,
                                         sp_end=row.sp_end,
                                         dp_type=row.dp_type,
                                         dp_start=row.dp_start,
                                         dp_end=row.dp_end,
                                         protocol=row.protocol,
                                         nwservice_count=row.nwservice_count,
                                         nwservice_names=row.nwservice_names,
                                         chain_id=row.chain_id,
                                         admin_status=row.admin_status)

    def create_chain_bypass_rule(self, chain_bypass_rule):
        """
        Insert Chain Bypass Rule record into database

        :return:
                Chain Bypass Rule if the insertion is successful
                revoke transaction and raise exception
        """
        session = sa_session.get_session()
        with session.begin():
            rule_row = ChainBypassRules(id=chain_bypass_rule.id)
            rule_row.update(chain_bypass_rule.as_dict())
            session.add(rule_row)
            session.flush()
        return self._row_to_chain_bypass_rule(rule_row)

    def get_chain_bypass_rules(self, chain_id=None, rule_id=None, name=None, pagination=None):
        """
        Yields a lists of Chains that match filters

        :param name: Optional name to return one chain.
        :param chain_id: Optional chain_id to return rules in one chain.
        :param rule_id: Optional rule_id to return one rule
        :param pagination: Optional pagination query.
        """
        session = sa_session.get_session()
        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        query = session.query(ChainBypassRules)
        if chain_id is not None:
            query = query.filter(ChainBypassRules.chain_id == chain_id)
        if name is not None:
            query = query.filter(ChainBypassRules.name == name)
        if rule_id is not None:
            query = query.filter(ChainBypassRules.id == rule_id)

        return (self._row_to_chain_bypass_rule(x) for x in query.all())

    def update_chain_bypass_rule(self, chain_bypass_rule):
        """
        Update an Chain Bypass Rule.
        """
        session = sa_session.get_session()
        with session.begin():
            rule_row = session.merge(ChainBypassRules(id=chain_bypass_rule.id))
            rule_row.update(chain_bypass_rule.as_dict())
            session.flush()

        return self._row_to_chain_bypass_rule(rule_row)

    @staticmethod
    def delete_chain_bypass_rule(rule_id):
        """
        Delete a Chain
        """
        session = sa_session.get_session()
        with session.begin():
            session.query(ChainBypassRules).filter(ChainBypassRules.id == rule_id).delete()
            session.flush()

    @staticmethod
    def _row_to_service(row):
        return api_model.Service(id=row.id,
                                 name=row.name,
                                 tenant=row.tenant,
                                 form_factor_type=row.form_factor_type,
                                 type=row.type,
                                 load_share_algorithm=row.load_share_algorithm,
                                 load_indication_type=row.load_indication_type,
                                 high_threshold=row.high_threshold,
                                 low_threshold=row.low_threshold,
                                 pkt_field_to_hash=row.pkt_field_to_hash,
                                 admin_status=row.admin_status)

    def create_service(self, service):
        """
        Insert Network Service record into database

        :return:
                Network Service data if the insertion is successful
                revoke transaction and raise exception
        """
        session = sa_session.get_session()
        with session.begin():
            service_row = Services(id=service.id)
            service_row.update(service.as_dict())
            session.add(service_row)
            session.flush()
        return self._row_to_service(service_row)

    def get_services(self, service_id=None, name=None, pagination=None):
        """
        Yields a lists of Network services that match filters

        :param name: Optional name to return one network service.
        :param service_id: Optional service_id to return one Network Service.
        :param pagination: Optional pagination query.
        """
        session = sa_session.get_session()
        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        query = session.query(Services)
        if name is not None:
            query = query.filter(Services.name == name)
        if service_id is not None:
            query = query.filter(Services.id == service_id)

        return (self._row_to_service(x) for x in query.all())

    def update_service(self, service):
        """
        Update an Network Service.
        """
        session = sa_session.get_session()
        with session.begin():
            service_row = session.merge(Services(id=service.id))
            service_row.update(service.as_dict())
            session.flush()

        return self._row_to_service(service_row)

    @staticmethod
    def delete_service(service_id=None, name=None):
        """
        Delete a Network Service
        """
        session = sa_session.get_session()
        with session.begin():
            if service_id is not None:
                session.query(Services).\
                    filter(Services.id == service_id).delete()
            elif name is not None:
                session.query(Services).\
                    filter(Services.name == name).delete()
            session.flush()

    @staticmethod
    def _row_to_chain_service(row):
        return api_model.ChainService(id=row.id,
                                      sequence_number=row.sequence_number,
                                      chain_id=row.chain_id,
                                      service_id=row.service_id)

    def create_chain_service(self, chain_service):
        """
        Insert Chain Service record into database

        :return:
                Chain Service data if the insertion is successful
                revoke transaction and raise exception
        """
        session = sa_session.get_session()
        with session.begin():
            service_row = ChainServices(id=chain_service.id)
            service_row.update(chain_service.as_dict())
            session.add(service_row)
            session.flush()
        return self._row_to_chain_service(service_row)

    def get_chain_services(self, chain_id=None, chain_service_id=None, service_id=None,
                           pagination=None):
        """
        Yields a lists of Chain services that match filters

        :param chain_id: Optional chain_id to return one Chain Service.
        :param chain_service_id: Optional service_id to return one Chain Service.
        :param pagination: Optional pagination query.
        """
        session = sa_session.get_session()
        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        query = session.query(ChainServices)
        if chain_id is not None:
            query = query.filter(ChainServices.chain_id == chain_id)
        if service_id is not None:
            query = query.filter(ChainServices.service_id == service_id)
        if chain_service_id is not None:
            query = query.filter(ChainServices.id == chain_service_id)

        return (self._row_to_chain_service(x) for x in query.all())

    def update_chain_service(self, chain_service):
        """
        Update an Chain Service.
        """
        session = sa_session.get_session()
        with session.begin():
            service_row = session.merge(ChainServices(id=chain_service.id))
            service_row.update(chain_service.as_dict())
            session.flush()

        return self._row_to_chain_service(service_row)

    @staticmethod
    def delete_chain_service(chain_service_id):
        """
        Delete a Chain Service
        """
        session = sa_session.get_session()
        with session.begin():
            if chain_service_id is not None:
                session.query(ChainServices).\
                    filter(ChainServices.id == chain_service_id).delete()
            session.flush()

    @staticmethod
    def _row_to_chain_service_instance(row):
        return api_model.ChainServiceInstance(id=row.id,
                                              instance_id=row.instance_id,
                                              vlan_in=row.vlan_in,
                                              vlan_out=row.vlan_out,
                                              chain_id=row.chain_id,
                                              chain_service_id=row.chain_service_id)

    def create_chain_service_instance(self, service_instance):
        """
        Insert Chain Service Instance record into database

        :return:
                Chain Service Instance data if the insertion is successful
                revoke transaction and raise exception
        """
        session = sa_session.get_session()
        with session.begin():
            service_instance_row = ChainServiceInstances(id=service_instance.id)
            service_instance_row.update(service_instance.as_dict())
            session.add(service_instance_row)
            session.flush()
        return self._row_to_chain_service_instance(service_instance_row)

    def get_chain_service_instances(self, chain_id=None, chain_service_id=None, service_instance_id=None,
                           pagination=None):
        """
        Yields a lists of Chain services that match filters

        :param chain_id: Optional chain_id to return one Chain Service Instance.
        :param chain_service_id: Optional service_id to return one Chain Service Instance.
        :param service_instance_id: Optional service_instance_id to return one Chain Service Instance.
        :param pagination: Optional pagination query.
        """
        session = sa_session.get_session()
        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        query = session.query(ChainServiceInstances)
        if chain_id is not None:
            query = query.filter(ChainServiceInstances.chain_id == chain_id)
        if chain_service_id is not None:
            query = query.filter(ChainServiceInstances.chain_service_id == chain_service_id)
        if service_instance_id is not None:
            query = query.filter(ChainServiceInstances.id == service_instance_id)

        return (self._row_to_chain_service_instance(x) for x in query.all())

    def update_chain_service_instance(self, service_instance):
        """
        Update an Chain Service Instance.
        """
        session = sa_session.get_session()
        with session.begin():
            service_row = session.merge(ChainServiceInstances(id=service_instance.id))
            service_row.update(service_instance.as_dict())
            session.flush()

        return self._row_to_chain_service_instance(service_row)

    @staticmethod
    def delete_chain_service_instance(service_instance_id):
        """
        Delete a Chain Service Instance
        """
        session = sa_session.get_session()
        with session.begin():
            if service_instance_id is not None:
                session.query(ChainServiceInstances).\
                    filter(ChainServiceInstances.id == service_instance_id).delete()
            session.flush()

    @staticmethod
    def _row_to_chain_set(row):
        return api_model.ChainSet(id=row.id,
                                  name=row.name,
                                  tenant=row.tenant,
                                  admin_status=row.admin_status)

    def create_chain_set(self, chain_set):
        """
        Insert Chain Set record into database

        :return:
                Chain data if the insertion is successful
                revoke transaction and raise exception
        """
        session = sa_session.get_session()
        with session.begin():
            chain_set_row = ChainSet(id=chain_set.id)
            chain_set_row.update(chain_set.as_dict())
            session.add(chain_set_row)
            session.flush()
        return self._row_to_chain_set(chain_set_row)

    def get_chain_sets(self, chain_set_id=None, name=None, pagination=None):
        """
        Yields a lists of Chain Sets that match filters

        :param name: Optional name to return one chain.
        :param chain_set_id: Optional chain_set_id to return one chain Set.
        :param pagination: Optional pagination query.
        """
        session = sa_session.get_session()
        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        query = session.query(ChainSet)
        if name is not None:
            query = query.filter(ChainSet.name == name)
        if chain_set_id is not None:
            query = query.filter(ChainSet.id == chain_set_id)

        return (self._row_to_chain_set(x) for x in query.all())

    def update_chain_set(self, chain_set):
        """
        Update an Chain Set.
        """
        session = sa_session.get_session()
        with session.begin():
            chain_set_row = session.merge(ChainSet(id=chain_set.id))
            chain_set_row.update(chain_set.as_dict())
            session.flush()

        return self._row_to_chain_set(chain_set_row)

    @staticmethod
    def delete_chain_set(chain_set_id):
        """
        Delete a Chain Set
        """
        session = sa_session.get_session()
        with session.begin():
            session.query(ChainSet).filter(ChainSet.id == chain_set_id).delete()
            session.flush()

    @staticmethod
    def _row_to_chain_sel_rule(row):
        return api_model.ChainSelRule(id=row.id,
                                      name=row.name,
                                      tenant=row.tenant,
                                      eth_type=row.eth_type,
                                      eth_value=row.eth_value,
                                      src_mac_type=row.src_mac_type,
                                      src_mac=row.src_mac,
                                      dst_mac_type=row.dst_mac_type,
                                      dst_mac=row.dst_mac,
                                      sip_type=row.sip_type,
                                      sip_start=row.sip_start,
                                      sip_end=row.sip_end,
                                      dip_type=row.dip_type,
                                      dip_start=row.dip_start,
                                      dip_end=row.dip_end,
                                      sp_type=row.sp_type,
                                      sp_start=row.sp_start,
                                      sp_end=row.sp_end,
                                      dp_type=row.dp_type,
                                      dp_start=row.dp_start,
                                      dp_end=row.dp_end,
                                      protocol=row.protocol,
                                      chain_id=row.chain_id,
                                      chain_set_id=row.chain_set_id,
                                      admin_status=row.admin_status)

    def create_chain_sel_rule(self, chain_sel_rule):
        """
        Insert Chain Selection Rule record into database

        :return:
                Chain Selection Rule if the insertion is successful
                revoke transaction and raise exception
        """
        session = sa_session.get_session()
        with session.begin():
            rule_row = ChainSelectionRules(id=chain_sel_rule.id)
            rule_row.update(chain_sel_rule.as_dict())
            session.add(rule_row)
            session.flush()
        return self._row_to_chain_sel_rule(rule_row)

    def get_chain_sel_rules(self, chain_set_id=None, rule_id=None, name=None, pagination=None):
        """
        Yields a lists of Chain Selection rules that match filters

        :param name: Optional name to return one chain.
        :param chain_set_id: Optional chain_id to return rules in one chain.
        :param rule_id: Optional rule_id to return one rule
        :param pagination: Optional pagination query.
        """
        session = sa_session.get_session()
        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        query = session.query(ChainSelectionRules)
        if chain_set_id is not None:
            query = query.filter(ChainSelectionRules.chain_set_id == chain_set_id)
        if name is not None:
            query = query.filter(ChainSelectionRules.name == name)
        if rule_id is not None:
            query = query.filter(ChainSelectionRules.id == rule_id)

        return (self._row_to_chain_sel_rule(x) for x in query.all())

    def update_chain_sel_rule(self, chain_sel_rule):
        """
        Update an Chain Selection Rule.
        """
        session = sa_session.get_session()
        with session.begin():
            rule_row = session.merge(ChainSelectionRules(id=chain_sel_rule.id))
            rule_row.update(chain_sel_rule.as_dict())
            session.flush()

        return self._row_to_chain_sel_rule(rule_row)

    @staticmethod
    def delete_chain_sel_rule(rule_id):
        """
        Delete a Chain Selection rule
        """
        session = sa_session.get_session()
        with session.begin():
            session.query(ChainSelectionRules).filter(ChainSelectionRules.id == rule_id).delete()
            session.flush()

    @staticmethod
    def _row_to_chain_nw_map(row):
        return api_model.ChainNetworkMap(id=row.id,
                                         name=row.name,
                                         tenant=row.tenant,
                                         chain_set_id=row.chain_set_id,
                                         inbound_network=row.inbound_network,
                                         outbound_network=row.outbound_network,
                                         admin_status=row.admin_status)

    def create_chain_network_map(self, chain_nw_map):
        """
        Insert Chain Network Map record into database

        :return:
                Chain data if the insertion is successful
                revoke transaction and raise exception
        """
        session = sa_session.get_session()
        with session.begin():
            chain_nw_row = ChainNetworkMaps(id=chain_nw_map.id)
            chain_nw_row.update(chain_nw_map.as_dict())
            session.add(chain_nw_row)
            session.flush()
        return self._row_to_chain_nw_map(chain_nw_row)

    def get_chain_network_maps(self, chain_network_id=None, name=None, pagination=None):
        """
        Yields a lists of Chain Network Maps that match filters

        :param name: Optional name to return one chain.
        :param chain_network_id: Optional chain_set_id to return one chain Set.
        :param pagination: Optional pagination query.
        """
        session = sa_session.get_session()
        if pagination:
            raise NotImplementedError(_('Pagination not implemented'))

        query = session.query(ChainNetworkMaps)
        if name is not None:
            query = query.filter(ChainNetworkMaps.name == name)
        if chain_network_id is not None:
            query = query.filter(ChainNetworkMaps.id == chain_network_id)

        return (self._row_to_chain_nw_map(x) for x in query.all())

    def update_chain_network_map(self, chain_nw_map):
        """
        Update an Chain Network Map.
        """
        session = sa_session.get_session()
        with session.begin():
            chain_nw_row = session.merge(ChainNetworkMaps(id=chain_nw_map.id))
            chain_nw_row.update(chain_nw_map.as_dict())
            session.flush()

        return self._row_to_chain_nw_map(chain_nw_row)

    @staticmethod
    def delete_chain_network_map(chain_network_id):
        """
        Delete a Chain Network Map
        """
        session = sa_session.get_session()
        with session.begin():
            session.query(ChainNetworkMaps).filter(ChainNetworkMaps.id == chain_network_id).delete()
            session.flush()
