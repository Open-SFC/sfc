import collections

from oslo_log import log as logging
from nscsas.api import constants


LOG = logging.getLogger(__name__)
BOOL_SYN = ['active', 'enable', 'up', 'true']


def verify_attributes(body, attributes):
    """
        Verify whether Request has the attributes required for processing the record.
    """
    error = []
    for attr_name, attr_val in attributes.iteritems():
        if attr_val['mandatory'] and (not attr_name in body):
            LOG.info(_("Attribute %s not found in request body"), str(attr_name))
            error.append(attr_name)
    if error:
        raise AttributeError("Attributes %s missing" % ', '.join(error))


def convert(data):
    """
        converts data from unicode format to string format.
    """
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return str(data)


def populate_dmpath(dm_path, args):
    return str(constants.PATH_PREFIX + '.' + dm_path % args)


def get_key_param(attributes):
    not_found = True
    key_attrs = []
    for attr_name, attr_value in attributes.iteritems():
        if 'key' in attr_value:
            key_attrs.append(attr_name)
            not_found = False
    if not_found:
        raise AttributeError("Unable to find Key Parameter.")
    else:
        return key_attrs
