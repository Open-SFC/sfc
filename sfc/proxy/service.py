import eventlet
import socket
import sys

from oslo.config import cfg

from oslo_i18n import _gettextutils as gettextutils
from oslo_i18n._i18n import _
from oslo_log import log, _options


cfg.CONF.register_opts([
    cfg.StrOpt('host', default=socket.gethostname(),
               help=_('Name of this node.  This can be an opaque identifier.  '
                    'It is not necessarily a hostname, FQDN, or IP address. '
                    'However, the node name must be valid within '
                    'an AMQP key, and if using ZeroMQ, a valid '
                    'hostname, FQDN, or IP address')),
])
log.register_options(cfg.CONF)


def prepare_service(argv=None):
    eventlet.monkey_patch()
    gettextutils.install('sfc.proxy')
    cfg.set_defaults(_options.log_opts,
                     default_log_levels=['amqplib=WARN',
                                         'qpid.messaging=INFO',
                                         'sqlalchemy=WARN',
                                         'stevedore=INFO',
                                         'eventlet.wsgi.server=WARN'
                                         ])
    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='sfc.proxy')
    log.setup(cfg.CONF, 'sfc.proxy')
