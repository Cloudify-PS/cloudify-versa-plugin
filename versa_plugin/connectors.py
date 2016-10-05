import json
from requests import codes
from versa_plugin.versaclient import JSON
import uuid


class Network:
    def __init__(self, name, subnet, mask):
        self.name = name
        self.subnet = subnet
        self.mask = mask


def add_resource_pool(client, name, ip_address):
    url = "/api/config/cms/local/instances"
    data = {
        "instance": {
            "name": name,
            "ip-address": ip_address}}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_resource_pool(client, name):
    url = '/api/config/cms/local/instances/instance/{}'.format(name)
    client.delete(url, codes.no_content)


def add_organization(client, org_name, networks, resource):
    url = "/api/config/cms/local/organizations"
    org_uuid = 'cms:org:' + str(uuid.uuid4())
    network_list = []
    for network in networks:
        net = {
            "uuid": str(uuid.uuid4()),
            "name": network.name,
            "subnet": network.subnet,
            "mask": network.mask,
            "ipaddress-allocation-mode": "manual"}
        network_list.append(net)

    data = {
        "organization": {
            "uuid": org_uuid,
            "name": org_name,
            "description": 'Created by cloudify',
            "org-networks": {
                "org-network": network_list},
            "resource-pool": {"instances": resource}}}
    client.post(url, json.dumps(data), JSON, codes.created)
    return org_uuid


def delete_organization(client, org_uuid):
    url = "/api/config/cms/local/organizations/organization/" + org_uuid
    client.delete(url)


def get_organization_uuid(client, name):
    url = "/api/config/cms/local/organizations?deep"
    result = client.get(url, None, None)
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org['uuid']
    return None


def get_organization(client, name):
    url = "/api/config/cms/local/organizations?deep"
    result = client.get(url, None, None)
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org
    return None


def get_network_information(client, org_uuid):
    url = '/api/config/cms/local/organizations/organization/{0}/org-networks/org-network?select=uuid;ipaddress-allocation-mode;name;subnet;mask;vxlan'.format(org_uuid)
    result = client.get(url, None, None, codes.ok)
    return result
