import json
from versa_plugin.versaclient import JSON
from versa_plugin import find_by_name
from requests import codes


def create_interface(versa, interface):
    url = '/api/config/devices/device'\
          '/{}/config/interfaces'.format(versa.appliance)
    itype = interface['name'].split('-')[0]
    data = {itype: interface}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_interface(versa, name):
    itype = name.split('-')[0]
    url = '/api/config/devices/device/{}'\
          '/config/interfaces/{}/%22{}%22'.format(versa.appliance, itype, name)
    versa.client.delete(url, codes.no_content)


def is_interface_exists(versa, name):
    url = '/api/config/devices/device/{}/config/interfaces?deep'.\
          format(versa.appliance)
    result = versa.client.get(url, None, None, codes.ok, JSON)
    return find_by_name(result.get('interfaces'), 'itype', name)


def create_network(versa, network):
    url = '/api/config/devices/device/{}'\
          '/config/networks'.format(versa.appliance)
    data = {"network": network}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_network(versa, name):
    url = '/api/config/devices/device/{}'\
          '/config/networks/network/{}'.format(name)
    versa.client.delete(url, codes.no_content)


def is_network_exists(versa, name):
    url = '/api/config/devices/device/{}/config/networks/network?deep'.\
          format(versa.appliance)
    result = versa.client.get(url, None, None, codes.ok, JSON)
    return find_by_name(result, 'network', name)


def create_virtual_router(versa, router):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances'.format(versa.appliance)
    data = {"routing-instance": [router]}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_virtual_router(versa, name):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances'\
          '/routing-instance/{}'.format(versa.appliance, name)
    versa.client.delete(url, codes.no_content)


def is_router_exists(versa, name):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/routing-instance?deep'.\
          format(versa.appliance)
    result = versa.client.get(url, None, None, codes.ok, JSON)
    return find_by_name(result, 'routing-instance', name)


def add_network_to_router(versa, name, network):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/'\
          'routing-instance/{}'.format(versa.appliance, name)
    result = versa.client.get(url, None, None, codes.ok, JSON)
    result["routing-instance"]["networks"].append(network)
    versa.client.put(url, json.dumps(result), JSON, codes.no_content)


def delete_network_from_router(versa, name, network):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/'\
          'routing-instance/{}'.format(versa.appliance, name)
    result = versa.client.get(url, None, None, codes.ok, JSON)
    result["routing-instance"]["networks"].remove(network)
    versa.client.put(url, json.dumps(result), JSON, codes.no_content)


def update_zone(versa, zone):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/objects/zones/zone/{}'.format(versa.appliance, versa.organization,
                                          zone['name'])
    data = {
        "zone": zone}
    versa.client.put(url, json.dumps(data), JSON, codes.ok)


def get_zone(versa, zone_name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/objects/zones/zone'.format(versa.appliance, versa.organization)
    result = versa.client.get(url, None, None, codes.ok, JSON)
    for zone in result['zone']:
        if zone['name'] == zone_name:
            return zone
    return None


def create_zone(versa, zone):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}/objects/zones'.format(versa.appliance,
                                                            versa.organization)
    data = {"zone": zone}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_zone(versa, zone_name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/objects/zones/zone/{}'.format(versa.appliance, versa.organization,
                                        zone_name)
    versa.client.delete(url)
