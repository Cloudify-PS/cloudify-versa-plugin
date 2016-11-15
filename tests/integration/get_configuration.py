from versa_plugin.versaclient import VersaClient
import configuration
from requests import codes
import mock
import yaml


def display(data):
    print yaml.safe_dump(data, default_flow_style=False)


def get_configuration(url):
    def info(x):
        print x

    fake_ctx = mock.MagicMock()
    fake_ctx.logger.info = info
    patcher_ctx1 = mock.patch('versa_plugin.versaclient.ctx', fake_ctx)
    patcher_ctx1.start()
    with VersaClient(configuration.versa_config, '/tmp/versakey') as client:
        result = client.get(url, None, None, codes.ok)
        patcher_ctx1.stop()
        return result


def select_by_name(url, root, name=""):
    output = get_configuration(url)
    result = output[root]
    if name:
        for item in result:
            if name == item['name']:
                result = item
                break
        else:
            result = []
    return result


def pool(name=""):
    url = "/api/config/cms/local/instances/instance"
    return select_by_name(url, 'instance', name)


def cms_organization(name=""):
    url = '/api/config/cms/local/organizations/organization?deep'
    return select_by_name(url, 'organization', name)


def nms_organization(name=""):
    url = '/api/config/nms/provider/organizations/organization?deep'
    return select_by_name(url, 'organization', name)


def appliance(name=""):
    url = '/api/config/nms/provider/appliances/appliance?deep'
    return select_by_name(url, 'appliance', name)

if __name__ == '__main__':
    # display(pool())
    # display(cms_organization('manualtesting'))
    # display(nms_organization())
    display(appliance('vcpe1'))
