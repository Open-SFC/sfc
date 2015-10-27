# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
from sfc.proxy.client import client

_logger = logging.getLogger(__name__)

class Client(object):
    """
    SFC related Proxy Client Functions
    """
    
    def __init__(self, **kwargs):
        self.proxy_client = client.Client(**kwargs)
        self.format = 'json'
        url = self.proxy_client.url
        
        chains = 'service_function_chains'
        chain_functions = 'chain_functions'
        service_functions = 'service_functions'
        
        #SFC Proxy URLs
        self.chains_path = "%s/%s" % (url, chains)
        self.chain_path = "%s/%s" % (url, chains) + "/%s"
        
        self.chain_functions_path = "%s/%s" % (url, chain_functions)
        self.chain_function_path = "%s/%s" % (url, chain_functions) + "/%s"
        
        self.service_functions_path = "%s/%s" % (url, service_functions)
        self.service_function_path = "%s/%s" % (url, service_functions) + "/%s"
    
    ##Chains
    def create_chain(self, body=None):
        """
        Creates a new chain
        """
        return self.proxy_client.post(self.chains_path, body=body)
        
    def delete_chain(self, chain):
        """
        Deletes the specified chain
        """
        return self.proxy_client.delete(self.chain_path % (chain))
        
    def update_chain(self, chain, body=None):
        """
        Updates the specified chain
        """
        return self.proxy_client.put(self.chain_path % (chain), body=body)
        
    def list_chains(self, **_params):
        """
        Fetches a list of all chains
        """
        return self.proxy_client.list('chains', self.chains_path, True, **_params)
        
    def show_chain(self, chain, **_params):
        """
        Fetches information of a Chain
        """
        return self.proxy_client.get(self.chain_path % (chain), params=_params)
    
    ##Chain Function Associations
    def create_chain_function(self, body=None):
        """
        Creates a new chain_function
        """
        return self.proxy_client.post(self.chain_functions_path, body=body)
        
    def delete_chain_function(self, chain_function):
        """
        Deletes the specified chain_function
        """
        return self.proxy_client.delete(self.chain_function_path % (chain_function))
        
    def update_chain_function(self, chain_function, body=None):
        """
        Updates the specified chain_function
        """
        return self.proxy_client.put(self.chain_function_path % (chain_function), body=body)
        
    def list_chain_functions(self, **_params):
        """
        Fetches a list of all chain_functions
        """
        return self.proxy_client.list('chain_functions', self.chain_functions_path, True, **_params)
        
    def show_chain_function(self, chain_function, **_params):
        """
        Fetches information of a Chain
        """
        return self.proxy_client.get(self.chain_function_path % (chain_function), params=_params)
    
    ##Service Function Instances
    def create_service_function(self, body=None):
        """
        Creates a new service_function
        """
        return self.proxy_client.post(self.service_functions_path, body=body)
        
    def delete_service_function(self, service_function):
        """
        Deletes the specified service_function
        """
        return self.proxy_client.delete(self.service_function_path % (service_function))
        
    def update_service_function(self, service_function, body=None):
        """
        Updates the specified service_function
        """
        return self.proxy_client.put(self.service_function_path % (service_function), body=body)
        
    def list_service_functions(self, **_params):
        """
        Fetches a list of all service_functions
        """
        return self.proxy_client.list('service_functions', self.service_functions_path, True, **_params)
        
    def show_service_function(self, service_function, **_params):
        """
        Fetches information of a Chain
        """
        return self.proxy_client.get(self.service_function_path % (service_function), params=_params)    
    