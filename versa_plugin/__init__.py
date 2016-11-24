import os
from functools import wraps
from cloudify import ctx
from cloudify import exceptions as cfy_exc
from versa_plugin.versaclient import VersaClient

VERSA_CONFIG = 'versa_config'


def _create_path():
    if ctx._local:
        key_dir = ctx._context['storage']._storage_dir
    else:
        key_dir = os.path.dirname(os.environ.get('VIRTUALENV', '/tmp'))
    return '{}/versa.key'.format(key_dir)


class Versa:
    def __init__(self):
        path = _create_path()
        config = ctx.node.properties.get(VERSA_CONFIG)
        self.client = VersaClient(config, path)
        self.appliance = ctx.node.properties.get('appliance')
        self.organization = ctx.node.properties.get('organization')

    def __enter__(self):
        self.client.get_token()
        return self

    def __exit__(self, type, value, traceback):
        pass


def with_versa(f):
    """
        add vca client to function params
    """
    @wraps(f)
    def wrapper(*args, **kw):
        with Versa() as versa:
            kw['versa'] = versa
            result = f(*args, **kw)
        return result
    return wrapper


def get_mandatory(obj, parameter):
    """
        return value for field or raise exception if field does not exist
    """
    value = obj.get(parameter)
    if value:
        return value
    else:
        raise cfy_exc.NonRecoverableError(
            "Mandatory parameter {0} is absent".format(parameter))


def find_by_name(result, key, name):
    if not result:
        return None
    for item in result[key]:
        if item["name"] == name:
            return item
    return None
