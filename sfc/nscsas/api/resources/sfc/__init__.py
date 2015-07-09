from pecan.rest import RestController

from .chains import ChainController
from .services import ServiceController
from .chainsets import ChainSetController, ChainNetworkMapController


class SFCController(RestController):

    chains = ChainController()
    services = ServiceController()
    chainsets = ChainSetController()
    chainnetworks = ChainNetworkMapController()
