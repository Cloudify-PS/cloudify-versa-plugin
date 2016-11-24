import json
from versa_plugin.versaclient import JSON
from versa_plugin import find_by_name
from requests import codes


def create_profile(versa, profile):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}/ipsec'.format(versa.appliance,
                                                      versa.organization)
    data = {"vpn-profile": profile}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_profile(versa, name):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/ipsec/vpn-profile/{}'.format(versa.appliance, versa.organization,
                                         name)
    versa.client.delete(url)


def is_profile_exists(versa, name):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/ipsec/vpn-profile?deep'.format(versa.appliance, versa.organization)
    result = versa.client.get(url, None, None, codes.ok)
    return find_by_name(result, "vpn-profile", name)
