import json
from versa_plugin.versaclient import JSON
from requests import codes
from collections import namedtuple


AddressRange = namedtuple("AddressRange", "name, low, high")


def create_pool(versa, pool):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}/cgnat/pools'.format(versa.appliance,
                                                            versa.organization)
    data = {"pool": pool}
    pools = versa.client.post(url, json.dumps(data), JSON, codes.created)
    return pools


def delete_pool(versa, name):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/cgnat/pools/pool/{}'.format(versa.appliance, versa.organization,
                                        name)
    versa.client.delete(url, codes.no_content)


def create_rule(versa, rule):
    url = '/api/config/appliances/{}/orgs/org-services/{}/cgnat/rules'.format(
        versa.appliance, versa.organization)
    data = {"rule": rule}
    rules = versa.client.post(url, json.dumps(data), JSON, codes.created)
    return rules


def delete_rule(versa, name):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/cgnat/rules/rule/{}'.format(versa.appliance, versa.organization,
                                        name)
    versa.client.delete(url, codes.no_content)


def get_list_nat_pools(versa, appliance, org):
    url = '/api/config/appliances/{}/orgs/org-services/{}/cgnat/pools/pool'.\
        format(appliance, org)
    pools = versa.client.get(url, None, None, codes.ok)
    return pools


def get_list_nat_rules(versa, appliance, org):
    url = '/api/config/appliances/{}/orgs/org-services/{}/cgnat/rules/rule'.\
        format(appliance, org)
    pools = versa.client.get(url, None, None, codes.ok)
    return pools
