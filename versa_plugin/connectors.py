import json
from requests import codes
from versa_plugin.versaclient import JSON
import uuid


def add_resource_pool(client, instance):
    url = "/api/config/cms/local/instances"
    data = {"instance": instance}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_resource_pool(client, name):
    url = '/api/config/cms/local/instances/instance/{}'.format(name)
    client.delete(url, codes.no_content)


def add_organization(client, organization):
    url = "/api/config/cms/local/organizations"
    org_uuid = str(uuid.uuid4())
    for network in organization['org-networks']['org-network']:
        network['uuid'] = str(uuid.uuid4())
    organization['uuid'] = org_uuid
    data = {"organization": organization}
    client.post(url, json.dumps(data), JSON, codes.created)
    return org_uuid


def delete_organization(client, org_name):
    org_uuid = get_organization_uuid(client, org_name)
    url = "/api/config/cms/local/organizations/organization/" + org_uuid
    client.delete(url)


def get_organization_uuid(client, name):
    url = "/api/config/cms/local/organizations?deep"
    result = client.get(url, None, None)
    if not result:
        return None
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org['uuid']
    return None


def get_organization(client, name):
    url = "/api/config/cms/local/organizations?deep"
    result = client.get(url, None, None)
    if not result:
        return None
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org
    return None
