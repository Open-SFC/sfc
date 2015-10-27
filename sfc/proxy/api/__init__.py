from oslo.config import cfg

# Register options for the service
API_SERVICE_OPTS = [
    cfg.IntOpt('port',
               default=20203,
               help='The port for the SFC Proxy server',),
    cfg.StrOpt('host',
               default='0.0.0.0',
               help='The listen IP for the SFC Proxy server',),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='api',
                         title='Options for the SFC Proxy service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)
