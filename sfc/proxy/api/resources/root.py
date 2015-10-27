from pecan import expose

from sfc.proxy import version
from . import v1


class RootController(object):

    @expose('json')
    def index(self):
        # FIXME: Return version information
        return dict({'version':version.version})

    v1 = v1.V1Controller()
setattr(RootController, 'v1.0', v1.V1Controller())
