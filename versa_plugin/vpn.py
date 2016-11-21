import json
from versa_plugin.versaclient import JSON
from versa_plugin import find_by_name
from requests import codes


def create_profile(client, appliance, org, profile):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}/ipsec'.format(appliance, org)
    data = {"vpn-profile": profile}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_profile(client, appliance, org, name):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/ipsec/vpn-profile/{}'.format(appliance, org, name)
    client.delete(url)


def is_profile_exists(client, appliance, org, name):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/ipsec/vpn-profile?deep'.format(appliance, org)
    result = client.get(url, None, None, codes.ok)
    return find_by_name(result, "vpn-profile", name)
