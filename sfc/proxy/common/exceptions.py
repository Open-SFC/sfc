from oslo_config import cfg
from oslo_log import log as logging
import six

from oslo_i18n._i18n import _, _translators

_LE = _translators.log_error

LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='Used if there is a formatting error when generating an '
                     'exception message (a programming error). If True, '
                     'raise an exception; if False, use the unformatted '
                     'message.'),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


def _cleanse_dict(original):
    """Strip all admin_password, new_pass, rescue_pass keys from a dict."""
    return dict((k, v) for k, v in original.iteritems() if "_pass" not in k)


class SFCException(Exception):
    """Base SFC Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.message % kwargs

            except Exception as e:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception(_LE('Exception in string format operation'))
                for name, value in kwargs.items():
                    LOG.error("%s: %s" % (name, value))

                if CONF.fatal_exception_format_errors:
                    raise e
                else:
                    # at least get the core message out if something happened
                    message = self.message

        super(SFCException, self).__init__(message)

    def __str__(self):
        """Encode to utf-8 then wsme api can consume it as well."""
        if not six.PY3:
            return unicode(self.args[0]).encode('utf-8')

        return self.args[0]

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return six.text_type(self)


class NotAuthorized(SFCException):
    message = _("Not authorized.")
    code = 403


class OperationNotPermitted(NotAuthorized):
    message = _("Operation not permitted.")


class Invalid(SFCException):
    message = _("Unacceptable parameters.")
    code = 400


class Conflict(SFCException):
    message = _('Conflict.')
    code = 409


class TemporaryFailure(SFCException):
    message = _("Resource temporarily unavailable, please retry.")
    code = 503


class NotAcceptable(SFCException):
    # TODO(deva): We need to set response headers in the API for this exception
    message = _("Request not acceptable.")
    code = 406


class InvalidUUID(Invalid):
    message = _("Expected a uuid but received %(uuid)s.")


class InvalidUuidOrName(Invalid):
    message = _("Expected a logical name or uuid but received %(name)s.")


class InvalidName(Invalid):
    message = _("Expected a logical name but received %(name)s.")


class InvalidMAC(Invalid):
    message = _("Expected a MAC address but received %(mac)s.")


# Cannot be templated as the error syntax varies.
# msg needs to be constructed when raised.
class InvalidParameterValue(Invalid):
    message = _("%(err)s")


class MissingParameterValue(InvalidParameterValue):
    message = _("%(err)s")


class Duplicate(SFCException):
    message = _("Resource already exists.")


class NotFound(SFCException):
    message = _("Resource could not be found.")
    code = 404
    
class ChainNotFound(SFCException):
    message = _("Chain %(id)s could not be found.")
    code = 404
    
class AppliancesNotFound(SFCException):
    message = _("Appliance with the name %(name)s could not be found.")
    code = 404
    
class ChainDeleteNotPermitted(SFCException):
    message = _("Chain %(id)s could not be deleted, as Instances are referenced.")
    code = 404
    
class ChainSelectionRuleNotFound(SFCException):
    message = _("Chain Selection Rule %(id)s could not be found.")
    code = 404


class ChainsetNotFound(SFCException):
    message = _("Chainset %(id)s could not be found.")
    code = 404


class InstanceNotFound(SFCException):
    message = _("Instance with give id '%(instance_id)s' could not be found")
    code = 404