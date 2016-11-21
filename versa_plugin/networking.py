import json
from versa_plugin.versaclient import JSON, XML
from versa_plugin import find_by_name
from requests import codes


def _netmask_to_cidr(netmask):
    return sum([bin(int(x)).count("1") for x in netmask.split(".")])


def _find_node_by_name(limits, name, value):
    node = None
    for item in limits.getElementsByTagName(name):
        if item.firstChild.data == value:
            node = item
            break
    return node


def _add_organization_child(xml, tagname, text):
    org_node = xml.lastChild
    node = xml.createElement(tagname)
    value = xml.createTextNode(text)
    node.appendChild(value)
    org_node.appendChild(node)


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


def create_virtual_router(client, appliance, router):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances'.format(appliance)
    data = {"routing-instance": [router]}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_virtual_router(client, appliance, name):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/routing-instance/{}'.format(appliance,
                                                                 name)
    client.delete(url, codes.no_content)


def is_router_exists(client, appliance, name):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/routing-instance?deep'.\
          format(appliance)
    result = client.get(url, None, None, codes.ok, JSON)
    return find_by_name(result, 'routing-instance', name)


def add_network_to_router(client, appliance, name, network):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/'\
          'routing-instance/{}'.format(appliance, name)
    result = client.get(url, None, None, codes.ok, JSON)
    result["routing-instance"]["networks"].append(network)
    client.put(url, json.dumps(result), JSON, codes.no_content)


def delete_network_from_router(client, appliance, name, network):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/'\
          'routing-instance/{}'.format(appliance, name)
    result = client.get(url, None, None, codes.ok, JSON)
    result["routing-instance"]["networks"].remove(network)
    client.put(url, json.dumps(result), JSON, codes.no_content)


def create_dhcp_profile(client, appliance, name):
    url = '/api/config/devices/device/{}/config/dhcp-profiles'.format(appliance)
    data = {
        "dhcp-profile": {
            "name": name,
            "dhcp-options": {
                "max-servers": "256",
                "max-clients": "256"}}}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_dhcp_profile(client, appliance, profile):
    url = '/api/config/devices/device/{}'\
          '/config/dhcp-profiles/dhcp-profile/{}'.format(appliance, profile)
    client.delete(url, codes.no_content)


def is_dhcp_profile_exists(client, appliance, profile):
    url = '/api/config/devices/device/{}'\
          '/config/dhcp-profiles/dhcp-profile?deep'.format(appliance)
    result = client.get(url, None, None, codes.ok, JSON)
    return find_by_name(result, 'dhcp-profile', profile)


def get_organization_limits(client, appliance, org):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    result = client.get(url, None, None, codes.ok, XML)
    org_node = result.lastChild
    operations_node = org_node.getElementsByTagName('y:operations')[0]
    org_node.removeChild(operations_node)
    return result


def insert_dhcp_profile_to_limits(client, appliance, org, profile):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    _add_organization_child(limits, 'dhcp-profile', profile)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def delete_dhcp_profile_from_limits(client, appliance, org, profile):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    node = _find_node_by_name(limits, "dhcp-profile", profile)
    if node:
        limits.firstChild.removeChild(node)
        xmldata = limits.toxml()
        client.put(url, xmldata, XML, codes.no_content)


def add_routing_instance(client, appliance, org, instance):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    _add_organization_child(limits, "available-routing-instances", instance)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def delete_routing_instance(client, appliance, org, instance):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    node = _find_node_by_name(limits, "available-routing-instances", instance)
    if node:
        limits.firstChild.removeChild(node)
        xmldata = limits.toxml()
        client.put(url, xmldata, XML, codes.no_content)


def add_provider_organization(client, appliance, org, provider):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    _add_organization_child(limits, "available-provider-orgs", provider)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def delete_provider_organization(client, appliance, org, provider):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    node = _find_node_by_name(limits, "available-provider-orgs", provider)
    if node:
        limits.firstChild.removeChild(node)
        xmldata = limits.toxml()
        client.put(url, xmldata, XML, codes.no_content)


def add_traffic_identification_networks(client, appliance, org, network):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    traffic_nodes = limits.getElementsByTagName('traffic-identification')
    if not traffic_nodes:
        tnode = limits.createElement('traffic-identification')
        limits.lastChild.appendChild(tnode)
        traffic_node = tnode
    else:
        traffic_node = traffic_nodes[0]
    node = limits.createElement("using-networks")
    value = limits.createTextNode(network)
    node.appendChild(value)
    traffic_node.appendChild(node)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def delete_traffic_identification_networks(client, appliance, org, network):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    traffic_node = limits.getElementsByTagName('traffic-identification')[0]
    node = None
    for net in limits.getElementsByTagName("using-networks"):
        if net.firstChild.data == network:
            node = net
            break
    if node:
        traffic_node.removeChild(node)
        xmldata = limits.toxml()
        client.put(url, xmldata, XML, codes.no_content)


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
