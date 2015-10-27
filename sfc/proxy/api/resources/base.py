from pecan import expose, abort, response
from pecan.rest import RestController
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class EntityNotFound(Exception):
    code = 404

    def __init__(self, entity, id):
        super(EntityNotFound, self).__init__(
            _("%(entity)s '%(id)s' Not Found") % {'entity': entity,
                                                  'id': id})


class BaseController(RestController):
    """
    This class implements base functions for handling REST requests
    """

    @expose('json')
    def get_all(self):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")

    @expose('json')
    def get_one(self, *args):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")

    @expose('json')
    def post(self, *args):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")

    @expose('json')
    def put(self, *args):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")

    @expose('json')
    def delete(self, *args):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")
