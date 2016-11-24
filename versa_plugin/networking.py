import json
from versa_plugin.versaclient import JSON
from versa_plugin import find_by_name
from requests import codes


def create_interface(client, appliance, interface):
    url = '/api/config/devices/device/{}/config/interfaces'.format(appliance)
    itype = interface['name'].split('-')[0]
    data = {itype: interface}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_interface(client, appliance, name):
    itype = name.split('-')[0]
    url = '/api/config/devices/device/{}'\
          '/config/interfaces/{}/%22{}%22'.format(appliance, itype, name)
    client.delete(url, codes.no_content)


def create_network(client, appliance, network):
    url = '/api/config/devices/device/{}/config/networks'.format(appliance)
    data = {"network": network}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_network(client, appliance, name):
    url = '/api/config/devices/device/{}'\
          '/config/networks/network/{}'.format(appliance, name)
    client.delete(url, codes.no_content)


def is_network_exists(client, appliance, name):
    url = '/api/config/devices/device/{}/config/networks/network?deep'.\
          format(appliance)
    result = client.get(url, None, None, codes.ok, JSON)
    return find_by_name(result, 'network', name)


def create_virtual_router(context, router):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances'.format(context.appliance)
    data = {"routing-instance": [router]}
    context.client.post(url, json.dumps(data), JSON, codes.created)


def delete_virtual_router(context, name):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances'\
          '/routing-instance/{}'.format(context.appliance, name)
    context.client.delete(url, codes.no_content)


def is_router_exists(context, name):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/routing-instance?deep'.\
          format(context.appliance)
    result = context.client.get(url, None, None, codes.ok, JSON)
    return find_by_name(result, 'routing-instance', name)


def add_network_to_router(context, name, network):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/'\
          'routing-instance/{}'.format(context.appliance, name)
    result = context.client.get(url, None, None, codes.ok, JSON)
    result["routing-instance"]["networks"].append(network)
    context.client.put(url, json.dumps(result), JSON, codes.no_content)


def delete_network_from_router(context, name, network):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/'\
          'routing-instance/{}'.format(context.appliance, name)
    result = context.client.get(url, None, None, codes.ok, JSON)
    result["routing-instance"]["networks"].remove(network)
    context.client.put(url, json.dumps(result), JSON, codes.no_content)


def update_zone(client, appliance, org, zone):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/objects/zones/zone/{}'.format(appliance, org, zone['name'])
    data = {
        "zone": zone}
    client.put(url, json.dumps(data), JSON, codes.ok)


def get_zone(client, appliance, org, zone_name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/objects/zones/zone'.format(appliance, org)
    result = client.get(url, None, None, codes.ok, JSON)
    for zone in result['zone']:
        if zone['name'] == zone_name:
            return zone
    return None


def create_zone(client, appliance, org, zone):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}/objects/zones'.format(appliance, org)
    data = {"zone": zone}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_zone(client, appliance, org, zone_name):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/objects/zones/zone/{}'.format(appliance, org, zone_name)
    client.delete(url)
