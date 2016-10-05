from functools import wraps
from cloudify import ctx
from versa_plugin.versaclient import VersaClient

VERSA_CONFIG = 'versa_config'


def with_versa_client(f):
    """
        add vca client to function params
    """
    @wraps(f)
    def wrapper(*args, **kw):
        config = ctx.node.properties.get(VERSA_CONFIG)
        with VersaClient(config) as client:
            kw['versa_client'] = client
            result = f(*args, **kw)
        return result
    return wrapper
