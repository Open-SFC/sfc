# Server Specific Configurations
server = {
    'port': '20203',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'sfc.proxy.api.resources.root.RootController',
    'modules': ['sfc.proxy.api'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/sfc/proxy/api/templates',
    'debug': True,
}
