import os
from functools import wraps
from cloudify import ctx
from versa_plugin.versaclient import VersaClient

VERSA_CONFIG = 'versa_config'


def _create_path():
    if ctx._local:
        key_dir = ctx._context['storage']._storage_dir
    else:
        key_dir = os.path.dirname(os.environ['VIRTUALENV'])
    return '{}/versa.key'.format(key_dir)


def with_versa_client(f):
    """
        add vca client to function params
    """
    @wraps(f)
    def wrapper(*args, **kw):
        config = ctx.node.properties.get(VERSA_CONFIG)
        path = _create_path()
        with VersaClient(config, path) as client:
            kw['versa_client'] = client
            result = f(*args, **kw)
        return result
    return wrapper
