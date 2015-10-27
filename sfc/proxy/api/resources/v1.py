"""Version 1 of the API.
"""
import os
import sys
from pecan import expose, abort
import wsmeext.pecan as wsme_pecan
from pecan.rest import RestController

from oslo_log import log as logging

from .chains import ChainController, ClassifierController, \
    FlowDescriptorController

from .service_functions import ServiceFunctionController
from .locators import ServiceLocatorController
from .chain_functions import ChainFunctionController
from .service_groups import ServiceGroupController

LOG = logging.getLogger(__name__)


class V1Controller(RestController):
    """Version 1 API controller root."""

    service_function_chains = ChainController()
    classifiers = ClassifierController()
    #flows = FlowDescriptorController()
    service_flows = FlowDescriptorController()
    service_functions = ServiceFunctionController()
    chain_functions = ChainFunctionController()
    service_locators = ServiceLocatorController()
    service_groups = ServiceGroupController()
