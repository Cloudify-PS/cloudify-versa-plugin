import json
from versa_plugin.versaclient import JSON
from versa_plugin import find_by_name
from requests import codes


def update_global_configuration(versa, lease_profile,
                                options_profile):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-server-and-relay'.format(versa.appliance,
                                              versa.organization)
    data = {
        "dhcp4-server-and-relay": {
            "default-lease-profile": lease_profile,
            "default-options-profile": options_profile,
            "log-unmatched-requests": False}}
    versa.client.put(url, json.dumps(data), JSON, codes.ok)


def create_options_profile(versa, name, domain, servers):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-options-profiles'.format(versa.appliance,
                                              versa.organization)
    data = {
        "dhcp4-options-profile": {
            "name": name,
            "domain-name": domain,
            "dns-server": servers,
            "custom-options": {"custom-dhcp-option": []}}}
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


def create_lease_profile(versa, name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-lease-profiles'.format(versa.appliance, versa.organization)
    data = {
        "dhcp4-lease-profile": {
            "name": name,
            "valid-lifetime": "3600",
            "renew-timer": "900",
            "rebind-timer": "2800",
            "log-utilization": False}}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_lease_profile(versa, name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-lease-profiles'\
        '/dhcp4-lease-profile/{}'.format(versa.appliance,
                                         versa.organization, name)
    versa.client.delete(url, codes.no_content)


def create_pool(versa, pool_name, mask,
                lease_profile, options_profile,
                range_name, begin_address, end_address):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/dhcp/dhcp4-dynamic-pools'.format(versa.appliance, versa.organization)
    data = {
        "dhcp4-dynamic-pool": {
            "name": pool_name,
            "subnet-mask": mask,
            "lease-profile": lease_profile,
            "options-profile": options_profile,
            "address-pools": {
                "dhcp4-address-pool-info": [{
                    "name": range_name,
                    "pool": {
                        "ipv4-range": {
                            "begin-address": begin_address,
                            "end-address": end_address}}}]},
            "exclude-addresses": {"dhcp4-address-pool-info": []}}}
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


def create_server(versa, server_name,
                  lease_profile, options_profile, networks, pool):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}/dhcp'\
        '/dhcp4-server-and-relay/service-profiles'.format(versa.appliance,
                                                          versa.organization)
    data = {
        "dhcp4-service-profile": {
            "name": server_name,
            "lease-profile": lease_profile,
            "options-profile": options_profile,
            "dhcp-request-match": {
                "networks": networks},
            "dhcp-service-type": {
                "service-type": {
                    "allocate-address": {
                        "dynamic": pool}}},
            "dhcp-log-settings": {
                "log-new-allocations": True,
                "log-renewals": False}}}
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
