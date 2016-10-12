import json
from versa_plugin.versaclient import JSON, XML
from requests import codes


def create_virtual_router(client, appliance, name, networks):
    url = '/api/config/devices/device/{}/config/routing-instances'.format(appliance)
    data = {
        "routing-instance":[{
            "name": name,
            "instance-type":"virtual-router",
            "networks":networks}]}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_virtual_router(client, appliance, name):
    url = '/api/config/devices/device/{}'\
          '/config/routing-instances/routing-instance/{}'.format(appliance,
                                                                 name)
    client.delete(url, codes.no_content)


def create_dhcp_profile(client, appliance, name):
    url = '/api/config/devices/device/{}/config/dhcp-profiles'.format(appliance)
    data = {"dhcp-profile": {"name": name}}
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


def update_dhcp_profile(client, appliance, org, profile):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    org_node = limits.lastChild
    profile_node = limits.createElement('dhcp-profile')
    profile_value = limits.createTextNode(profile)
    profile_node.appendChild(profile_value)
    org_node.appendChild(profile_node)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)


def update_available_routing_instances(client, appliance, org, instance):
    url = '/api/config/devices/device/{}/config/orgs/org/{}'.format(appliance,
                                                                    org)
    limits = get_organization_limits(client, appliance, org)
    org_node = limits.lastChild
    routing_node = limits.createElement("available-routing-instances")
    routing_value = limits.createTextNode(instance)
    routing_node.appendChild(routing_value)
    org_node.appendChild(routing_node)
    xmldata = limits.toxml()
    client.put(url, xmldata, XML, codes.no_content)
