import copy

import wsme
from pecan import request, response, rest
from wsme import types as wtypes
from oslo.config import cfg
from oslo_log import log as logging
from oslo_i18n._i18n import _

from sfc.proxy.api import expose
from sfc.proxy.api.resources.base import BaseController
from sfc.proxy.api.resources.types import _Base, \
    uuid, AdvEnum, IPAddressType

from sfc.proxy.common import exceptions as sfcexc
from novaclient.v2.client import Client as nc
from oslo_utils import uuidutils
import re

LOG = logging.getLogger(__name__)

class Chain(_Base):
    """
    Representation of Chain Structure
    """
    id = uuid
    "The UUID of the chain"

    name = wtypes.StringType(max_length=255)
    "The name for the chain"
    
    description = wsme.wsattr(wtypes.text)
    "The description for the chain"

    tenant_id = uuid
    "The Tenant UUID to which the Service Function Chain belongs"

    classifiers = [uuid]

    operation_mode = int
    "Operation Mode Value"

    def as_dict(self):
        return self.as_dict_from_keys(['id', 'name', 'description',
                                       'tenant_id', 'operation_mode',
                                       'classifiers'])


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


class ChainController(rest.RestController):

    @expose.expose(ChainResp, Chain)
    def post(self, chain):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body.

        :return: Dictionary of the added record.
        """
        
        chain_id = None
        LOG.debug(_("Chain create: %s"), str(chain))
        print chain.as_dict()
        tenant_id = uuidutils._format_uuid_string(chain.tenant_id)
        classifiers = chain.classifiers
        classifier_str = ''
        for classifier in classifiers:
            classifier_str = classifier + ','
        
        chain_name = re.sub(r"\s+", '_', chain.name)
        chain_data = {
            'chain': {
                'name': chain_name,
                'tenant_id': tenant_id,
                'auto_boot': False,
                'extras': classifier_str
                }
                }
        if chain.id:
            if request.crdclient.list_chains(id=chain.id)['chains']:
                #raise sfcexc.Duplicate()
                chain_id = chain.id
            else:
                chain_data['chain'].update({'id': chain.id})
        
                LOG.debug(_("Creating Chain in CRD ... with Data: %s"), str(chain_data))
                chain_resp = request.crdclient.create_chain(body=chain_data)
                LOG.debug(_("Creating Chain Response from CRD: %s"), str(chain_resp))
                chain_id = chain_resp['chain']['id']
        
        for classifier in classifiers:
            try:
                ### Get Classifier(Chainset) Details from CRD
                chainset_details = request.crdclient.show_chainset(classifier)
                ### Get Flows(Selection Rules) from CRD for the given
                ### Classifier(Chainset)
                rules = request.crdclient.list_rules(classifier,
                                                     tenant_id=tenant_id)
                for rule in rules['rules']:
                    ###Create Selection Rule with Chain ID and Chainset ID
                    ###And, Delete old one which don't have Chain ID earlier
                    chain_sel_rule_data = {
                        'rule':
                            {
                                'chain_id': chain_id,
                                'tenant_id': tenant_id,
                                'src_mac_type': rule['src_mac_type'] or 'any',
                                'dest_mac_type': rule['dest_mac_type'] or 'any',
                                'src_mac': rule['src_mac'] or '',
                                'dest_mac': rule['dest_mac'] or '',
                                'eth_type': rule['eth_type'] or '',
                                'eth_value': str(rule['eth_value'] or ''),
                                'sip_type': rule['sip_type'] or '',
                                'dip_type': rule['dip_type'] or '',
                                'sip_start': rule['sip_start'] or '',
                                'sip_end': rule['sip_end'] or '',
                                'dip_start': rule['dip_start'] or '',
                                'dip_end': rule['dip_end'] or '',
                                'sp_type': rule['sp_type'] or '',
                                'dp_type': rule['dp_type'] or '',
                                'sp_start': str(rule['sp_start'] or ''),
                                'sp_end': str(rule['sp_end'] or ''),
                                'dp_start': str(rule['dp_start'] or ''),
                                'dp_end': str(rule['dp_end'] or ''),
                                'ip_protocol': str(rule['ip_protocol'] or '')
                            }
                    }
                    
                    request.crdclient.create_rule(classifier, body=chain_sel_rule_data)
                    request.crdclient.delete_rule(classifier, rule['id'])
            except:
                LOG.error(_("Chainset %s is NOT found!!!"), str(classifier))
                raise sfcexc.ChainsetNotFound(id=classifier)
        return ChainResp(**({'chain': chain}))

    @expose.expose(ChainResp, wtypes.text, Chain)
    def put(self, chain_id, chain):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body.

        :return: Dictionary of the added record.
        """
        chain.id = chain_id

        return ChainResp(**({'chain': chain}))

    @expose.expose(None, wtypes.text, status_code=204)
    def delete(self, chain_id):
        """Delete this Chain."""
        ### Delete Selection Rules attached to the Chain...First
        ### Get Chainset with name 'Default Chainset'
        ### Search 'Default Chainset' exists in CRD...
        chains = request.crdclient.list_chains()
        
        
        chain_details = request.crdclient.show_chain(chain_id)
        LOG.debug(_("Chain Details: %s"), str(chain_details))
        
        tenant_id = chain_details['chain']['tenant_id']

        ### Delete Chain Appliance Associations
        ### Get Chain Appliance Association of the chain
        instance_ref = False
        chain_app_maps = request.crdclient.list_appliance_maps(chain_id)
        LOG.debug(_("Chain Appliances: %s"), str(chain_app_maps))
        for chain_app in chain_app_maps['appliances']:
            chain_app_id = chain_app['id']
            appliance_id = chain_app['appliance_id']
            
            chain_app_insts = request.crdclient.list_appliance_map_instances(chain_id,
                                                                             appliance_id)
            LOG.debug(_("Chain Appliances Instances: %s"), str(chain_app_insts))
            if chain_app_insts['instances']:
                for app_inst in chain_app_insts['instances']:
                    app_inst_id = app_inst['id']
                    instance_uuid = app_inst['instance_uuid']
                    nova = nc(cfg.CONF.nova.username,
                    cfg.CONF.nova.password,
                    cfg.CONF.nova.tenant_name,
                    cfg.CONF.nova.auth_url)
                    try:
                        instance = nova.servers.get(instance_uuid)
                        instance_ref = True
                        break
                    except:
                        instance_ref = False
                        ### Delete Chain Appliance Instance Associations
                        request.crdclient.delete_appliance_map_instance(app_inst_id,
                                                                        chain_app_id,
                                                                        chain_id)

        chainsets = request.crdclient.list_chainsets(tenant_id=tenant_id)
        for chainset in chainsets['chainsets']:
            chainset_id = chainset['id']

            ### Get Selection Rules with the given chain_id
            if not instance_ref:
                sel_rules = request.crdclient.list_rules(chainset_id,
                                                         chain_id=chain_id)
                for rule in sel_rules['rules']:
                    rule_id = rule['id']
                    ### Delete Selection Rule
                    if rule_id:
                        request.crdclient.delete_rule(chainset_id, rule_id)
                    
                ### Delete Chain
                try:
                    request.crdclient.delete_chain(chain_id)
                except:
                    LOG.warning(_("Chain %s is already deleted"), str(chain_id))
            else:
                LOG.error(_("Instance references are still there for the Chain ID: %s"), str(chain_id))
                raise sfcexc.ChainDeleteNotPermitted(id=chain_id)
            
class Classifier(_Base):
    """
    Representation of Traffic Classifier Structure
    """
    id = uuid
    "The UUID of the Traffic Classifier"

    description = wsme.wsattr(wtypes.text)
    "The description for the Classifier"

    tenant_id = uuid
    "The Tenant UUID to which the Classifier belongs"
    
    sch_type = AdvEnum("sch_type", str, 'SCH', 'MAC')
    "SCH Type. Allowed values are SCH / MAC."

    flows = [uuid]

    def as_dict(self):
        return self.as_dict_from_keys(['id', 'description',
                                       'tenant_id', 'sch_type',
                                       'flows'])
    

class ClassifiersResp(_Base):
    """
    Representation of Classifiers list Response
    """
    classifiers = [Classifier]


class ClassifierResp(_Base):
    """
    Representation of Classifier Response
    """
    classifier = Classifier


class ClassifierController(rest.RestController):

    @expose.expose(ClassifierResp, Classifier)
    def post(self, classifier):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body.

        :return: Dictionary of the added record.
        """
        
        LOG.debug(_("Classifier create: %s"), str(classifier))
        print classifier.as_dict()
        tenant_id = uuidutils._format_uuid_string(classifier.tenant_id)
        
        ### Search 'Default Chainset' exists in CRD...
        def_chainset_id = None
        chainsets = request.crdclient.list_chainsets(tenant_id=tenant_id,
                                                     name='Default Chainset')
        if not chainsets['chainsets']:
            ### Create 'Default Chainset' in CRD
            chainset_data = {'chainset': {'tenant_id': tenant_id, 'name': 'Default Chainset'}}
            LOG.debug(_("Creating Chainset in CRD ... with Data: %s"), str(chainset_data))
            chainset = request.crdclient.create_chainset(body=chainset_data)
            LOG.debug(_("Created Chainset in CRD: %s"), str(chainset))
            def_chainset_id = chainset['chainset']['id']
        else:
            chainset = chainsets['chainsets'][0]
            def_chainset_id = chainset['id']
        
        
        
        ### Create Chainset for the classifier, as CRD doesn't have any
        ### Classifier details
        chainset_name = 'Chainset'+ classifier.id[:13]
        #chainset_name = 'CS1'
        
        ### Check for Chainset with the given Classifier ID
        try:
            chainset_details = request.crdclient.show_chainset(classifier.id)
        except:
            ### Chainset NOT found!!!. So, create it.
            chainset_data = { 'chainset': {
                    'id': classifier.id,
                    'tenant_id': tenant_id,
                    'name': chainset_name
                }
            }
            chainset_details = request.crdclient.create_chainset(chainset_data)
        
        if chainset_details and classifier.flows:
            chainset_id = chainset_details['chainset']['id']
            
            flow_descriptors = classifier.flows
            for flow in flow_descriptors:
                ### Check if Selection Rule exists with the given flow id
                try:
                    rule = request.crdclient.show_rule(def_chainset_id, flow)
                    ### Update Chainset ID of this Selection Rule
                    ### with the actual inserted classifier ID(ChainsetID)
                    update_rule = {'rule':{'chainset_id': chainset_id}}
                    request.crdclient.update_rule(chainset_id, flow, update_rule)
                except:
                    ### Chain selection rule NOT found!!!. So, create it.
                    LOG.error(_("Chian Selection Rule with the ID: %s NOT Found!!!"), str(flow))
                    raise sfcexc.ChainSelectionRuleNotFound(id=flow)
                    
        return ClassifierResp(**({'classifier': classifier}))

    @expose.expose(ClassifierResp, wtypes.text, Classifier)
    def put(self, classifier_id, classifier):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body.

        :return: Dictionary of the added record.
        """
        classifier.id = classifier_id

        return ClassifierResp(**({'classifier': classifier}))

    @expose.expose(None, wtypes.text, status_code=204)
    def delete(self, classifier_id):
        """Delete this Classifier."""
        pass

class FlowDescriptor(_Base):
    """
    Representation of Flow Descriptor Structure
    """
    id = uuid
    "The UUID of the Flow Descriptor"

    description = wsme.wsattr(wtypes.text)
    "The description for the Flow Descriptor"

    tenant_id = uuid
    "The Tenant UUID to which the Classifier belongs"
    
    eth_type = wtypes.StringType(max_length=10)
    "Eth Type. Allowed values are Any / Single."
    
    eth_value = int
    "Ethernet Protocol Value."
    
    src_mac_type = wtypes.StringType(max_length=10)
    "Source MAC Type. Allowed values are Any / Single."
    
    src_mac = wtypes.StringType(max_length=32)
    "Source MAC Address"
    
    dst_mac_type = wtypes.StringType(max_length=10)
    "Destination MAC Type. Allowed values are Any / Single."
    
    dst_mac = wtypes.StringType(max_length=32)
    "Destination MAC Address"
    
    vlan_id = int
    "VLAN Identifier."
    
    vlan_priority = int
    "VLAN Priority."
    
    sip_type = wtypes.StringType(max_length=10)
    "Source IP Type. Allowed values are any / single / range / subnet."
    
    #sip_start = wtypes.StringType(max_length=15)
    sip_start = IPAddressType()
    "Source IP address or start IP Address"
    
    #sip_end = wtypes.StringType(max_length=15)
    sip_end = IPAddressType()
    "Source end IP Address or network mask or prefix"
    
    dip_type = wtypes.StringType(max_length=10)
    "Destination IP Type. Allowed values are any / single / range / subnet."
    
    dip_start = wtypes.StringType(max_length=15)
    "Destination IP Address or start IP address"
    
    dip_end = wtypes.StringType(max_length=15)
    "Destination End IP address or network mask or prefix"
    
    sp_type = wtypes.StringType(max_length=10)
    "Source Port Type. Allowed values are any / single / range."
    
    sp_start = int
    "Source port number or start port number"
    
    sp_end = int
    "Source End Port number"
    
    dp_type = wtypes.StringType(max_length=10)
    "Destination Port Type. Allowed values are any / single / range."
    
    dp_start = int
    "Destination port number or start port number"
    
    dp_end = int
    "Destination End Port number"
    
    ip_protocol = int
    "IP Protocol"
    
    ip_dscp = int
    "IP DSCP"
    
    ip_ecn = int
    "IP ECN"

    def as_dict(self):
        return self.as_dict_from_keys(['id', 'description',
                                       'tenant_id', 'eth_type', 'eth_value',
                                       'src_mac_type', 'src_mac', 'dst_mac_type',
                                       'dst_mac', 'vlan_id', 'vlan_priority',
                                       'sip_type', 'sip_start', 'sip_end',
                                       'dip_type', 'dip_start', 'dip_end',
                                       'sp_type', 'sp_start', 'sp_end',
                                       'dp_type', 'dp_start', 'dp_end',
                                       'ip_protocol', 'ip_dscp', 'ip_ecn'])
    
class FlowDescriptorsResp(_Base):
    """
    Representation of FlowDescriptors list Response
    """
    flow_descriptors = [FlowDescriptor]


class FlowDescriptorResp(_Base):
    """
    Representation of FlowDescriptor Response
    """
    flow_descriptor = FlowDescriptor


class FlowDescriptorController(rest.RestController):

    @expose.expose(FlowDescriptorResp, FlowDescriptor)
    def post(self, flow_descriptor):
        """
        This function implements create record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the POST request body.

        :return: Dictionary of the added record.
        """
        
        LOG.debug(_("FlowDescriptor create: %s"), str(flow_descriptor))
        print str(request.body)
        fd = flow_descriptor.as_dict()
        print "FD dict ==================================>", fd
        tenant_id = uuidutils._format_uuid_string(flow_descriptor.tenant_id)
        
        ### Search 'Default Chainset' exists in CRD...
        chainset_id = None
        chainsets = request.crdclient.list_chainsets(tenant_id=tenant_id,
                                                     name='Default Chainset')
        if not chainsets['chainsets']:
            ### Create 'Default Chainset' in CRD
            chainset_data = {'chainset': {'tenant_id': tenant_id, 'name': 'Default Chainset'}}
            LOG.debug(_("Creating Chainset in CRD ... with Data: %s"), str(chainset_data))
            chainset = request.crdclient.create_chainset(body=chainset_data)
            LOG.debug(_("Created Chainset in CRD: %s"), str(chainset))
            chainset_id = chainset['chainset']['id']
        else:
            chainset = chainsets['chainsets'][0]
            chainset_id = chainset['id']
        
        if chainset_id:
            chain_sel_rule_data = {
                'rule':
                    {
                        #'name':flow_details['name'],
                        #'chain_id': chain_id,
                        'tenant_id': tenant_id,
                        'src_mac_type': fd.get('src_mac_type') or 'any',
                        'dest_mac_type': fd.get('dst_mac_type') or 'any',
                        'src_mac': fd.get('src_mac') or '',
                        'dest_mac': fd.get('dst_mac') or '',
                        'eth_type': fd.get('eth_type') or '',
                        'eth_value': str(fd.get('eth_value') or ''),
                        'sip_type': fd.get('sip_type') or '',
                        'dip_type': fd.get('dip_type') or '',
                        'sip_start': fd.get('sip_start') or '',
                        'sip_end': fd.get('sip_end') or '',
                        'dip_start': fd.get('dip_start') or '',
                        'dip_end': fd.get('dip_end') or '',
                        'sp_type': fd.get('sp_type') or '',
                        'dp_type': fd.get('dp_type') or '',
                        'sp_start': str(fd.get('sp_start') or ''),
                        'sp_end': str(fd.get('sp_end') or ''),
                        'dp_start': str(fd.get('dp_start') or ''),
                        'dp_end': str(fd.get('dp_end') or ''),
                        'ip_protocol': str(fd.get('ip_protocol') or '')
                    }
            }
            
            if flow_descriptor.id:
                chain_sel_rule_data['rule'].update({'id': fd['id']})
            
            LOG.debug(_("Creating Chain Selection Rule in CRD ... with Data: %s"), str(chain_sel_rule_data))
            sel_rule_resp = request.crdclient.create_rule(chainset_id, body=chain_sel_rule_data)
            LOG.debug(_("Creating Chain Selection Rule Response from CRD: %s"), str(sel_rule_resp))
        
        return FlowDescriptorResp(**({'flow_descriptor': flow_descriptor}))

    @expose.expose(FlowDescriptorResp, wtypes.text, FlowDescriptor)
    def put(self, flow_descriptor_id, flow_descriptor):
        """
        This function implements update record functionality of the RESTful request.
        It converts the requested body in JSON format to dictionary in string representation and verifies whether
        required ATTRIBUTES are present in the PUT request body.

        :return: Dictionary of the added record.
        """
        flow_descriptor.id = flow_descriptor_id

        return FlowDescriptorResp(**({'flow_descriptor': flow_descriptor}))

    @expose.expose(None, wtypes.text, status_code=204)
    def delete(self, flow_descriptor_id):
        """Delete this FlowDescriptor."""
        chainsets = request.crdclient.list_chainsets()
        for chainset in chainsets['chainsets']:
            chainset_id = chainset['id']
            flow_details = None
            try:
                flow_details = request.crdclient.show_rule(chainset_id, flow_descriptor_id)
                break
            except:
                pass
            
        if flow_details:
            print "##########"
            print flow_details
            print "##########"
            #request.crdclient.delete_rule(chainset_id, flow_descriptor_id)
        else:
            LOG.error(_("Unable to find Selection Rule ID %s"), str(flow_descriptor_id))
