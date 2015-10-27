import inspect
from pecan import expose, abort, response
from pecan.rest import RestController
import six
import wsme
from wsme import types as wtypes
import netaddr
from netaddr.ip import IPNetwork, IPAddress
from oslo_utils import strutils
from oslo_utils import uuidutils
from oslo_log import log as logging

from sfc.proxy.common import exceptions

LOG = logging.getLogger(__name__)


class BooleanType(wtypes.UserType):
    """A simple boolean type."""
    
    basetype = wtypes.text
    name = 'boolean'
    
    @staticmethod
    def validate(value):
        try:
            return strutils.bool_from_string(value, strict=True)
        except ValueError as e:
            # raise Invalid to return 400 (BadRequest) in the API
            raise exceptions.Invalid(e)
        
    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return BooleanType.validate(value)


class CIDR(wtypes.wsproperty):

    def __init__(self, name, **kwargs):
        self._name = '_CIDR_%s' % name
        mandatory = kwargs.pop('mandatory', False)
        super(CIDR, self).__init__(datatype=wtypes.text, fget=self._get,
                                   fset=self._set, mandatory=mandatory)

    def _get(self, parent):
        if hasattr(parent, self._name):
            value = getattr(parent, self._name)
            return value or wsme.Unset
        return wsme.Unset

    def _set(self, parent, value):
        try:
            if value and IPNetwork(value):
                setattr(parent, self._name, value)
        except netaddr.AddrFormatError:
            error = _('Value %(value)s is not a valid IP Address') % dict(value=value)
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))


class MACAddressType(wtypes.UserType):
        """
        A simple MAC Address Type
        """
        basetype = six.string_types
        name = "macaddress"
        
        @staticmethod
        def validate(value):
            try:
                netaddr.valid_mac(value)
            except netaddr.AddrFormatError:
                error = 'value should be MAC format.'
                raise ValueError(error)
            else:
                return value


class IPAddressType(wtypes.UserType):
    """
    A simple IPAddress Type irrespective of addressing mode
    IPv4 or IPv6.
    """
    basetype = six.string_types
    name = "ipaddress"

    @staticmethod
    def validate(value):
        print value
        netaddr.IPAddress(value, flags=netaddr.INET_PTON)
        try:
            netaddr.IPAddress(value, flags=netaddr.INET_PTON)
        except netaddr.AddrFormatError:
            error = 'value should be in IP Address format.'
            raise ValueError(error)
        else:
            return value


class AdvEnum(wtypes.wsproperty):
    """Handle default and mandatory for wtypes.Enum
    """
    def __init__(self, name, *args, **kwargs):
        self._name = '_advenum_%s' % name
        mandatory = kwargs.pop('mandatory', False)
        if kwargs.pop('capitalize', False):
            arg_caps = [args[0]]
            for a in args[1:]:
                arg_caps.append(a.capitalize())
            args = arg_caps
        enum = wtypes.Enum(*args, **kwargs)
        super(AdvEnum, self).__init__(datatype=enum, fget=self._get,
                                      fset=self._set, mandatory=mandatory)

    def _get(self, parent):
        if hasattr(parent, self._name):
            value = getattr(parent, self._name)
            return value or wsme.Unset
        return wsme.Unset

    def _set(self, parent, value):
        if self.datatype.validate(value):
            setattr(parent, self._name, value)


class _Base(wtypes.DynamicBase):

    def as_dict_from_keys(self, keys):
        return dict((k, getattr(self,k))
                    for k in keys
                    if hasattr(self,k) and
                    getattr(self,k) != wsme.Unset)


uuid = wtypes.UuidType()

