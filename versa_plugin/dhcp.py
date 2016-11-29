import json
from versa_plugin.versaclient import JSON
from versa_plugin import find_by_name
from requests import codes


def update_global_configuration(versa, server_and_relay):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-server-and-relay'.format(versa.appliance,
                                              versa.organization)
    data = {"dhcp4-server-and-relay": server_and_relay}
    versa.client.put(url, json.dumps(data), JSON, codes.ok)


def create_options_profile(versa, options_profile):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-options-profiles'.format(versa.appliance,
                                              versa.organization)
    data = {"dhcp4-options-profile": options_profile}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_options_profile(versa, name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-options-profiles/'\
        'dhcp4-options-profile/{}'.format(versa.appliance, versa.organization,
                                          name)
    versa.client.delete(url, codes.no_content)


def is_dhcp_profile_exists(versa, name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-options-profiles/'\
        'dhcp4-options-profile?deep'.format(versa.appliance, versa.organization)
    result = versa.client.get(url, None, None, codes.ok)
    return find_by_name(result, "dhcp4-options-profile", name)


def is_lease_profile_exsists(versa, name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}/dhcp/'\
        'dhcp4-lease-profiles/'\
        'dhcp4-lease-profile?deep=true'.format(versa.appliance,
                                               versa.organization)
    result = versa.client.get(url, None, None, codes.ok)
    return find_by_name(result, "dhcp4-lease-profile", name)


def create_lease_profile(versa, lease_profile):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-lease-profiles'.format(versa.appliance, versa.organization)
    data = {"dhcp4-lease-profile": lease_profile}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_lease_profile(versa, name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-lease-profiles'\
        '/dhcp4-lease-profile/{}'.format(versa.appliance,
                                         versa.organization, name)
    versa.client.delete(url, codes.no_content)


def create_pool(versa, pool):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-dynamic-pools'.format(versa.appliance, versa.organization)
    data = {"dhcp4-dynamic-pool": pool}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_pool(versa, pool_name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-dynamic-pools'\
        '/dhcp4-dynamic-pool/{}'.format(versa.appliance, versa.organization,
                                        pool_name)
    versa.client.delete(url, codes.no_content)


def is_pool_exists(versa, pool_name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-dynamic-pools'\
        '/dhcp4-dynamic-pool?deep'.format(versa.appliance, versa.organization)
    result = versa.client.get(url, None, None, codes.ok)
    if not result:
        return
    for pool in result["dhcp4-dynamic-pool"]:
        if pool["name"] == pool_name:
            return True
    return False


def create_server(versa, server):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}/dhcp'\
        '/dhcp4-server-and-relay/service-profiles'.format(versa.appliance,
                                                          versa.organization)
    data = {"dhcp4-service-profile": server}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_server(versa, server_name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-server-and-relay'\
        '/service-profiles/dhcp4-service-profile/{}'.format(versa.appliance,
                                                            versa.organization,
                                                            server_name)
    versa.client.delete(url, codes.no_content)


def is_server_exists(versa, server_name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-server-and-relay'\
        '/service-profiles'\
        '/dhcp4-service-profile?deep'.format(versa.appliance,
                                             versa.organization)
    result = versa.client.get(url, None, None, codes.ok)
    return find_by_name(result, 'dhcp4-service-profile', server_name)
