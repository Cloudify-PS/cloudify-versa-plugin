import json
import time
import uuid
import versa_plugin
from versa_plugin.versaclient import JSON
from requests import codes
from cloudify import exceptions as cfy_exc
import random
from versa_plugin import get_mandatory

SUCCESS = 'SUCCESS'
MAX_RETRY = 30
SLEEP_TIME = 3


def _get_task_id(task_info):
    return task_info['output']['result']['task']['task-id']


def add_organization(client, organization):
    url = "/api/config/nms/provider/organizations"
    org_uuid = str(uuid.uuid4())
    cms_org_name = get_mandatory(get_mandatory(organization, 'cms-orgs'),
                                 'name')
    cms_org_uuid = versa_plugin.connectors.get_organization_uuid(client,
                                                                 cms_org_name)
    while True:
        org_id = random.randint(1, 1000)
        if not is_organization_id_exists(client, org_id):
            break
    organization['uuid'] = org_uuid
    organization['id'] = org_id
    organization['cms-orgs']['uuid'] = cms_org_uuid
    data = {'organization': organization}
    client.post(url, json.dumps(data), JSON, codes.created)
    return org_uuid


def delete_organization(client, org_name):
    org_uuid = get_organization_uuid(client, org_name)
    if not org_uuid:
        return None
    url = "/api/config/nms/actions/delete-organization"
    data = {"delete-organization": {"orguuid":  org_uuid}}
    return client.post(url, json.dumps(data), JSON, codes.ok)


def add_appliance(client, device):
    url = "/api/config/nms/actions/add-devices"
    device['org'] = get_organization_uuid(client, device['org'])
    device['cmsorg'] = versa_plugin.connectors.get_organization_uuid(
        client, device['cmsorg'])
    if not device['org']:
        raise cfy_exc.NonRecoverableError("NMS organization uuid not found")
    elif not device['cmsorg']:
        raise cfy_exc.NonRecoverableError("CMS organization uuid not found")
    data = {'add-devices': {'devices': {'device': device}}}
    result = client.post(url, json.dumps(data), JSON, codes.ok)
    return _get_task_id(result)


def associate_organization(client, organization):
    url = '/api/config/nms/actions/'\
        '/associate-organization-to-appliance'
    appliance_uuid = get_appliance_uuid(client,
                                        get_mandatory(organization,
                                                      'appliance'))
    org_uuid = get_organization_uuid(client,
                                     get_mandatory(organization,
                                                   'org'))
    organization["orguuid"] = org_uuid
    organization["applianceuuid"] = appliance_uuid
    del organization['org']
    del organization['appliance']
    data = {"associate-organization-to-appliance": organization}
    result = client.post(url, json.dumps(data), JSON, codes.ok)
    return _get_task_id(result)


def disassociate_org(client, appliance, org):
    url = '/api/config/nms/actions'\
          '/dissociate-organization-from-appliances'
    appliance_uuid = get_appliance_uuid(client, appliance)
    org_uuid = get_organization_uuid(client, org)
    data = {
        "dissociate-organization-from-appliances": {
            "orguuid": org_uuid,
            "appliances": [appliance_uuid]}}
    client.post(url, json.dumps(data), JSON, codes.ok)


def get_appliance_uuid(client, name):
    url = '/api/config/nms/provider/appliances/appliance/'
    result = client.get(url, None, None, codes.ok)
    if not result:
        return None
    for app in result['appliance']:
        if app['name'] == name:
            return app['uuid']
    return None


def delete_appliance(client, name):
    url = "/api/config/nms/actions/delete-appliance"
    uuid = get_appliance_uuid(client, name)
    if not uuid:
        return None
    data = {
        "delete-appliance": {
            "applianceuuid": uuid,
            "dopostdelete": "true",
            "clean-config": "true"}}
    result = client.post(url, json.dumps(data), JSON, codes.ok)
    return _get_task_id(result)


def is_organization_id_exists(client, test_id):
    url = "/api/config/nms/provider/organizations?deep"
    result = client.get(url, None, None)
    if not result:
        return False
    for org in result['organizations']['organization']:
        if test_id == org['id']:
            return True
    return False


def get_organization(client, name):
    url = "/api/config/nms/provider/organizations?deep"
    result = client.get(url, None, None)
    if not result:
        return None
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org
    return None


def get_organization_uuid(client, name):
    url = "/api/config/nms/provider/organizations?deep"
    result = client.get(url, None, None)
    if not result:
        return None
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org['uuid']
    return None


def get_device_information(client, address):
    url = '/api/config/nms/actions/get-device-information'
    data = {
     "get-device-information": {
          "ip-address": address,
          "clean-config": "false"}}
    result = client.post(url, json.dumps(data), JSON, codes.ok)
    if not result:
        return None
    if result['output']['status'] == SUCCESS:
        return result['output']['device-details']['interfaces']
    else:
        return None


def wait_for_device(client, address, ctx):
    for retry in range(MAX_RETRY):
        ctx.logger.info("Waiting for device. Try {}/{}".format(retry + 1,
                                                               MAX_RETRY))
        device_info = get_device_information(client, address)
        if device_info:
            return
        time.sleep(SLEEP_TIME)
    raise cfy_exc.NonRecoverableError("Can't get device information")
