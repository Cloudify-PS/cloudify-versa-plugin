import json
import time
import uuid
import versa_plugin
from versa_plugin.versaclient import JSON, XML
from requests import codes
from cloudify import exceptions as cfy_exc
from collections import namedtuple
import random

SUCCESS = 'SUCCESS'
MAX_RETRY = 30
SLEEP_TIME = 3

ApplianceInterface = namedtuple("ApplianceInterface",
                                "name, address, interface")
NetworkInfo = namedtuple("NetworkInfo", "name, parent, address, mask, unit")


def _get_task_id(task_info):
    return task_info['output']['result']['task']['task-id']


def add_organization(client, org_name, parent, cms_org_name):
    url = "/api/config/nms/provider/organizations"
    org_uuid = str(uuid.uuid4())
    cms_org_uuid = versa_plugin.connectors.get_organization_uuid(client,
                                                                 cms_org_name)
    if not parent:
        parent = 'none'
    while True:
        org_id = random.randint(1, 1000)
        if not is_organization_id_exists(client, org_id):
            break
    xmldata = """
    <organization>
        <uuid>{0}</uuid>
        <id>{1}</id>
        <name>{2}</name>
        <right>2</right>
        <parent-org>{3}</parent-org>
        <subscription-plan>Default-All-Services-Plan</subscription-plan>
        <cms-orgs>
            <uuid>{4}</uuid>
            <name>{5}</name>
            <cms-connector>local</cms-connector>
        </cms-orgs>
     </organization>""".format(org_uuid, org_id, org_name,
                               parent, cms_org_uuid, cms_org_name)
    client.post(url, xmldata, XML, codes.created)
    return org_uuid


def delete_organization(client, org_name):
    org_uuid = get_organization_uuid(client, org_name)
    if not org_uuid:
        return None
    url = "/api/config/nms/actions/delete-organization"
    data = {"delete-organization": {"orguuid":  org_uuid}}
    return client.post(url, json.dumps(data), JSON, codes.ok)


def add_appliance(client, mgm_ip, name, nms_org_name, cms_org_name, networks):
    url = "/api/config/nms/actions/add-devices"
    nms_org_uuid = get_organization_uuid(client, nms_org_name)
    cms_org_uuid = versa_plugin.connectors.get_organization_uuid(client,
                                                                 cms_org_name)
    if not nms_org_uuid:
        raise cfy_exc.NonRecoverableError("NMS organization uuid not found")
    elif not cms_org_uuid:
        raise cfy_exc.NonRecoverableError("CMS organization uuid not found")
    net_info = ""
    for net in networks:
        info = """
                    <network-info>
                        <network-name>{0}</network-name>
                        <ip-address>{1}</ip-address>
                        <interface>{2}</interface>
                    </network-info>
               """.format(net.name, net.address, net.interface)
        net_info += info
    xmldata = """
    <add-devices>
        <devices>
            <device>
                <mgmt-ip>{0}</mgmt-ip>
                <name>{1}</name>
                <org>{2}</org>
                <cmsorg>{3}</cmsorg>
                <type>service-vnf</type>
                <networking-info>
                {4}
                </networking-info>
                <snglist>
                    <sng>
                        <name>Default_All_Services</name>
                        <isPartOfVCSN>true</isPartOfVCSN>
                    </sng>
                </snglist>
                <subscription>
                    <solution-tier>nextgen-firewall</solution-tier>
                    <bandwidth>100</bandwidth>
                </subscription>
            </device>
        </devices>
    </add-devices> """.format(mgm_ip, name, nms_org_uuid, cms_org_uuid,
                              net_info)
    result = client.post(url, xmldata, XML, codes.ok)
    return _get_task_id(result)


def associate_organization(client, appliance, org, net_info,
                           services=None):
    url = '/api/config/nms/actions/'\
        '/associate-organization-to-appliance'
    appliance_uuid = get_appliance_uuid(client, appliance)
    org_uuid = get_organization_uuid(client, org)
    network_info = [{
                    "network-name": n_info.name,
                    "parent-interface": n_info.parent,
                    "subinterface-unit-number": n_info.unit,
                    "vlan-id": n_info.unit,
                    "ipaddress-allocation-mode": "MANUAL",
                    "slot": "0",
                    "ip-address": n_info.address,
                    "mask": n_info.mask} for n_info in net_info]
    data = {
        "associate-organization-to-appliance": {
            "orguuid": org_uuid,
            "networking-info": {
                "network-info": network_info},
            "applianceuuid": appliance_uuid,
            "subscription": {
                "solution-tier": "nextgen-firewall",
                "bandwidth": "100"}}}
    if services:
        data["associate-organization-to-appliance"]["services"] = services
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


def wait_for_device(client, address):
    for retry in range(MAX_RETRY):
        print "Waiting for device. Try {}/{}".format(retry + 1, MAX_RETRY)
        device_info = get_device_information(client, address)
        if device_info:
            return
        time.sleep(SLEEP_TIME)
    raise cfy_exc.NonRecoverableError("Can't get device information")


def wait_for_parent(client, parent):
    for retry in range(MAX_RETRY):
        print "Waiting for parent org. Try {}/{}".format(retry + 1, MAX_RETRY)
        uuid = get_organization_uuid(client, parent)
        if uuid:
            return
        time.sleep(SLEEP_TIME)
    raise cfy_exc.NonRecoverableError("Can't get parent organization")
