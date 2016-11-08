import json
from versa_plugin.versaclient import JSON, XML
from requests import codes
from collections import namedtuple

Routing = namedtuple("Routing",
                     "ip_prefix, next_hop, interface, preference, tag")
Unit = namedtuple("Unit", "name, address, mask")


def _netmask_to_cidr(netmask):
    return sum([bin(int(x)).count("1") for x in netmask.split(".")])


def create_interface(client, appliance, name, units=None):
    url = '/api/config/devices/device/{}/config/interfaces'.format(appliance)
    data = {"vni": {"name": name, "enable": True, "promiscuous": False}}
    if units:
        units_list = [{"name": u.name,
                       "family": {
                           "inet": {
                               "address": [{
                                   "addr": "{}/{}".format(u.address,
                                                          _netmask_to_cidr(
                                                              u.mask))}]}},
                       "enable": True}
                      for u in units]
        data['vni'].update({"unit": units_list})
    client.post(url, json.dumps(data), JSON, codes.created)


def create_network(client, appliance, name, interface):
    url = '/api/config/devices/device/{}/config/networks'.format(appliance)
    data = {"network": {
        "name": name,
        "interfaces": [interface]}}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_interface(client, appliance, name):
    url = '/api/config/devices/device/{}'\
          '/config/interfaces/vni/%22{}%22'.format(appliance, name)
    client.delete(url, codes.no_content)


def create_virtual_router(client, appliance, name, networks, routings=None):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances'.format(appliance)
    route_list = []
    if routings:
        for route in routings:
            route_list.append({
                            "ip-prefix": route.ip_prefix,
                            "next-hop": route.next_hop,
                            "preference": route.preference,
                            "tag": route.tag,
                            "interface": route.interface})
    data = {
        "routing-instance": [{
            "name": name,
            "instance-type": "virtual-router",
            "networks": networks,
            "routing-options": {
                "static": {
                    "route": {
                        "rti-static-route-list": route_list}}}}]}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_virtual_router(client, appliance, name):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/routing-instance/{}'.format(appliance,
                                                                 name)
    client.delete(url, codes.no_content)


def add_network_to_router(client, appliance, name, network):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/'\
          'routing-instance/{}'.format(appliance, name)
    result = client.get(url, None, None, codes.ok, JSON)
    result["routing-instance"]["networks"].append(network)
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


def get_organization_limits(client, appliance, org):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    result = client.get(url, None, None, codes.ok, XML)
    org_node = result.lastChild
    operations_node = org_node.getElementsByTagName('y:operations')[0]
    org_node.removeChild(operations_node)
    return result


def add_organization_child(xml, tagname, text):
    org_node = xml.lastChild
    node = xml.createElement(tagname)
    value = xml.createTextNode(text)
    node.appendChild(value)
    org_node.appendChild(node)


def update_dhcp_profile(client, appliance, org, profile):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    add_organization_child(limits, 'dhcp-profile', profile)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def update_routing_instance(client, appliance, org, instance):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    add_organization_child(limits, "available-routing-instances", instance)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def update_provider_organization(client, appliance, org, provider):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    add_organization_child(limits, "available-provider-orgs", provider)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def update_traffic_identification_networks(client, appliance, org, network):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    traffic_node = limits.getElementsByTagName('traffic-identification')[0]
    node = limits.createElement("using-networks")
    value = limits.createTextNode(network)
    node.appendChild(value)
    traffic_node.appendChild(node)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def update_zones(client, appliance, org, zone, networks, routing_instances):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}/objects/zones/zone/{}'.format(appliance,
                                                                      org, zone)
    data = {
        "zone": {"name": zone,
                 "networks": networks,
                 "routing-instance": routing_instances}}
    client.put(url, json.dumps(data), JSON, codes.ok)


def get_zone(client, appliance, org, zone):
    url = '/api/config/devices/device/{}'\
        '/config/orgs/org-services/{}'\
        '/objects/zones/zone'.format(appliance, org)
    result = client.get(url, None, None, codes.ok, JSON)
    for zone in result['zones']:
        if zone['name'] == zone:
            return zone
    return None


def add_network_to_zone(client, appliance, org, zone, network):
    zone = get_zone(client, appliance, org, zone)
    new_networks = zone['networks'] + [network]
    update_zones(client, appliance, org, zone, new_networks)
