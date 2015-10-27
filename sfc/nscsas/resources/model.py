# -*- encoding: utf-8 -*-
#
# Author: Purandhar Sairam Mannidi <sairam.mp@freescale.com>
#
"""
Model classes for use in the SFC storage API.
"""

from nscs.nscsas.storage.base import Model


class Chain(Model):
    """
    Chains details.

    :param id: UUID of the chain
    :param name: The chain name
    :param tenant: Tenant Name to which this chain belongs
    :param admin_status: Admin Status (Enable / Disable)
    """

    def __init__(self, id, name, tenant, admin_status):
        Model.__init__(
            self,
            id=id,
            name=name,
            tenant=tenant,
            admin_status=admin_status
        )


class ChainBypassRule(Model):
    """
    Chain Bypass Rule details.

    :param id: UUID of the chain Bypass Rule
    :param name: The rule name
    :param tenant: Tenant Name to which this chain rule belongs
    :param eth_type: Ethernet Type (Any / Single)
    :param eth_value: Ethernet Value
    :param src_mac_type: Source MAC Type (Any / Single)
    :param src_mac: Source MAC Address
    :param dst_mac_type: Destination MAC Type (Any / Single)
    :param dst_mac: Destination MAC Address
    :param sip_type: Source IP Type (Any / Single / Range / Subnet)
    :param sip_start: Source IP address for type single or Start IP Address in case of Range
                       or IP Network part in case of subnet
    :param sip_end: Source IP address for type single or End IP Address in case of Range
                       or IP Mask digits part in case of subnet
    :param dip_type: Destination IP Type (Any / Single / Range / Subnet)
    :param dip_start: Destination IP address for type single or Start IP Address in case of Range
                       or IP Network part in case of subnet
    :param dip_end: Destination IP address for type single or End IP Address in case of Range
                       or IP Mask digits part in case of subnet
    :param sp_type: Source Port Type (Any / Single / Range)
    :param sp_start: Source Port Number for type single or Start Port number in case of Range
    :param sp_end: Source Port Number for type single or End Port number in case of Range
    :param dp_type: Destination Port Type (Any / Single / Range)
    :param dp_start: Destination Port Number for type single or Start Port number in case of Range
    :param dp_end: Destination Port Number for type single or End Port number in case of Range
    :param protocol: IP Protocol Number
    :param nwservice_count: Network services count
    :param nwservice_names: Network Services names
    :param chain_id: Chain ID to which this rule belongs
    :param admin_status: Admin Status (Enable / Disable)
    """

    def __init__(self, id, name, tenant,
                 eth_type, src_mac_type, dst_mac_type,
                 sip_type,  dip_type,
                 sp_type, dp_type, protocol,
                 nwservice_count, nwservice_names, chain_id, admin_status, sip_start='0.0.0.0',
                 sip_end='0.0.0.0', sp_start=1, sp_end=65535, dp_start=1, dp_end=65535,
                 dip_start='0.0.0.0', dip_end='0.0.0.0', src_mac='00:00:00:00:00:00', dst_mac='00:00:00:00:00:00',
                 eth_value=0x800):
        Model.__init__(
            self,
            id=id,
            name=name,
            tenant=tenant,
            eth_type=eth_type,
            eth_value=eth_value,
            src_mac_type=src_mac_type,
            src_mac=src_mac,
            dst_mac_type=dst_mac_type,
            dst_mac=dst_mac,
            sip_type=sip_type,
            sip_start=sip_start,
            sip_end=sip_end,
            dip_type=dip_type,
            dip_start=dip_start,
            dip_end=dip_end,
            sp_type=sp_type,
            sp_start=sp_start,
            sp_end=sp_end,
            dp_type=dp_type,
            dp_start=dp_start,
            dp_end=dp_end,
            protocol=protocol,
            nwservice_count=nwservice_count,
            nwservice_names=nwservice_names,
            chain_id=chain_id,
            admin_status=admin_status
        )


class Service(Model):
    """
    Services details.

    :param id: UUID of the services
    :param name: The Service name
    :param tenant: Tenant Name to which this chain belongs
    :param form_factor_type: Form Factor of the service (Physical / Virtual Machine)
    :param type: type of the appliance (L2 / L3)
    :param load_share_algorithm: Load Sharing Algorithm
    :param load_indication_type: Load Indication type (Connection based / Traffic based)
    :param high_threshold: High Threshold Value
    :param low_threshold: Low Threshold Value
    :param pkt_field_to_hash: Packet Field to Hash
    :param admin_status: Admin Status (Enable / Disable)
    """

    def __init__(self, id, name, tenant, form_factor_type, type,
                 load_share_algorithm, load_indication_type,
                 high_threshold, low_threshold, pkt_field_to_hash,
                 admin_status):
        Model.__init__(
            self,
            id=id,
            name=name,
            tenant=tenant,
            form_factor_type=form_factor_type,
            type=type,
            load_share_algorithm=load_share_algorithm,
            load_indication_type=load_indication_type,
            high_threshold=high_threshold,
            low_threshold=low_threshold,
            pkt_field_to_hash=pkt_field_to_hash,
            admin_status=admin_status
        )


class ChainService(Model):
    """
    Chain Services Map details.

    :param id: UUID of the Chain services
    :param sequence_number: Sequence number of the service
    :param chain_id: Chain id to map
    :param service_id: service id to map
    """

    def __init__(self, id, sequence_number, chain_id, service_id):
        Model.__init__(
            self,
            id=id,
            sequence_number=sequence_number,
            chain_id=chain_id,
            service_id=service_id
        )


class ChainServiceInstance(Model):
    """
    Chain Service Instance details.

    :param id: UUID of the Chain service Instance
    :param instance_id: Instance ID to map
    :param vlan_in: Data Port Input VLAN ID
    :param vlan_out: Data Port Output VLAN ID
    :param chain_id: Chain id to map
    :param chain_service_id: chain service id to map
    """

    def __init__(self, id, instance_id, vlan_in, vlan_out, chain_id, chain_service_id):
        Model.__init__(
            self,
            id=id,
            instance_id=instance_id,
            vlan_in=vlan_in,
            vlan_out=vlan_out,
            chain_id=chain_id,
            chain_service_id=chain_service_id
        )


class ChainSet(Model):
    """
    Chain Set details.

    :param id: UUID of the chain set
    :param name: The chain set name
    :param tenant: Tenant Name to which this chain set belongs
    :param type: Type of chain set (L2 / L3)
    :param admin_status: Admin Status (Enable / Disable)
    """

    def __init__(self, id, name, tenant, admin_status, zonefull=False,
                 direction=1):
        Model.__init__(
            self,
            id=id,
            name=name,
            tenant=tenant,
            admin_status=admin_status,
            zonefull=zonefull,
            direction=direction
        )


class ChainSetZone(Model):
    """
    Chain Set Zone details.

    :param id: UUID of the chain set
    :param name: The chain set Zone name
    :param direction: Direction to which this chain set belongs

    """

    def __init__(self, id, name, direction, chain_set_id):
        Model.__init__(
            self,
            id=id,
            name=name,
            direction=direction,
            chain_set_id=chain_set_id
        )


class ChainSelRule(Model):
    """
    Chain Bypass Rule details.

    :param id: UUID of the chain Selection Rule
    :param name: The rule name
    :param tenant: Tenant Name to which this chain selection rule belongs
    :param eth_type: Ethernet Type (Any / Single)
    :param eth_value: Ethernet Value
    :param src_mac_type: Source MAC Type (Any / Single)
    :param src_mac: Source MAC Address
    :param dst_mac_type: Destination MAC Type (Any / Single)
    :param dst_mac: Destination MAC Address
    :param sip_type: Source IP Type (Any / Single / Range / Subnet)
    :param sip_start: Source IP address for type single or Start IP Address
                      in case of Range or IP Network part in case of subnet
    :param sip_end: Source IP address for type single or End IP Address in
                    case of Range or IP Mask digits part in case of subnet
    :param dip_type: Destination IP Type (Any / Single / Range / Subnet)
    :param dip_start: Destination IP address for type single or Start IP
                      Address in case of Range or IP Network part in case of
                      subnet
    :param dip_end: Destination IP address for type single or End IP Address in
                    case of Range or IP Mask digits part in case of subnet
    :param sp_type: Source Port Type (Any / Single / Range)
    :param sp_start: Source Port Number for type single or Start Port number in
                     case of Range
    :param sp_end: Source Port Number for type single or End Port number in
                   case of Range
    :param dp_type: Destination Port Type (Any / Single / Range)
    :param dp_start: Destination Port Number for type single or Start Port
                     number in case of Range
    :param dp_end: Destination Port Number for type single or End Port number
                   in case of Range
    :param protocol: IP Protocol Number
    :param chain_set_id: Chain Set ID to which this rule belongs
    :param chain_id: Chain ID to which this rule belongs
    :param admin_status: Admin Status (Enable / Disable)
    """

    def __init__(self, id, name, tenant,
                 eth_type, src_mac_type, dst_mac_type,
                 sip_type,  dip_type,
                 sp_type, dp_type, protocol, chain_id, chain_set_id,
                 admin_status, sip_start='0.0.0.0', sip_end='0.0.0.0',
                 sp_start=1, sp_end=65535, dp_start=1, dp_end=65535,
                 dip_start='0.0.0.0', dip_end='0.0.0.0',
                 src_mac='00:00:00:00:00:00', dst_mac='00:00:00:00:00:00',
                 eth_value=0x800):
        Model.__init__(
            self,
            id=id,
            name=name,
            tenant=tenant,
            eth_type=eth_type,
            eth_value=eth_value,
            src_mac_type=src_mac_type,
            src_mac=src_mac,
            dst_mac_type=dst_mac_type,
            dst_mac=dst_mac,
            sip_type=sip_type,
            sip_start=sip_start,
            sip_end=sip_end,
            dip_type=dip_type,
            dip_start=dip_start,
            dip_end=dip_end,
            sp_type=sp_type,
            sp_start=sp_start,
            sp_end=sp_end,
            dp_type=dp_type,
            dp_start=dp_start,
            dp_end=dp_end,
            protocol=protocol,
            chain_id=chain_id,
            chain_set_id=chain_set_id,
            admin_status=admin_status
        )


class ChainNetworkMap(Model):
    """
    Chain Network Map details.

    :param id: UUID of the chain network map
    :param name: The chain network map name
    :param tenant: Tenant Name to which this chain network map belongs
    :param type: Type of chain network map (L2 / L3)
    :param inbound_network: Inbound Networks list
    :param outbound_network: Outbound Networks list
    :param chain_set_id: Chain Selection Rule ID
    :param admin_status: Admin Status (Enable / Disable)
    """

    def __init__(self, id, name, tenant, inbound_network,
                 chain_set_id, admin_status, outbound_network=''):
        Model.__init__(
            self,
            id=id,
            name=name,
            tenant=tenant,
            inbound_network=inbound_network,
            outbound_network=outbound_network,
            chain_set_id=chain_set_id,
            admin_status=admin_status
        )


class Attributes(Model):
    """
    Attributes details.

    :param id: UUID of the attribute
    :param name: The attribute name
    :param value: Attribute Value
    :param table_name: Table name to which this attribute belongs
    :param table_id: Table record id to which this attribute is mapped
    """

    def __init__(self, id, name, value, table_name, table_id):
        Model.__init__(
            self,
            id=id,
            name=name,
            value=value,
            table_name=table_name,
            table_id=table_id
        )
