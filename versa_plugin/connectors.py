import json
from requests import codes
from versa_plugin.versaclient import JSON
import uuid
from versa_plugin import get_mandatory


def add_resource_pool(versa, instance):
    url = "/api/config/cms/local/instances"
    data = {"instance": instance}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_resource_pool(versa, name):
    url = '/api/config/cms/local/instances/instance/{}'.format(name)
    versa.client.delete(url, codes.no_content)


def add_organization(versa, organization):
    url = "/api/config/cms/local/organizations"
    org_uuid = str(uuid.uuid4())
    networks = get_mandatory(get_mandatory(organization, 'org-networks'),
                             'org-network')
    for network in networks:
        network['uuid'] = str(uuid.uuid4())
    organization['uuid'] = org_uuid
    data = {"organization": organization}
    versa.client.post(url, json.dumps(data), JSON, codes.created)
    return org_uuid


def delete_organization(versa, org_name):
    org_uuid = get_organization_uuid(versa, org_name)
    url = "/api/config/cms/local/organizations/organization/" + org_uuid
    versa.client.delete(url)


def get_organization_uuid(versa, name):
    url = "/api/config/cms/local/organizations?deep"
    result = versa.client.get(url, None, None)
    if not result:
        return None
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org['uuid']
    return None


def get_organization(versa, name):
    url = "/api/config/cms/local/organizations?deep"
    result = versa.client.get(url, None, None)
    if not result:
        return None
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org
    return None
