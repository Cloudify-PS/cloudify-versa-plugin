import json
import time
import uuid
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
NetworkInfo = namedtuple("NetworkInfo", "name, parent, vlan, address, mask")


def _get_task_id(task_info):
    return task_info['output']['result']['task']['task-id']


def add_organization(client, org_name, parent, cms_org_uuid, cms_org_name):
    url = "/api/config/nms/provider/organizations"
    org_uuid = str(uuid.uuid4())
    parent = parent if parent else 'none'
    xmldata = """
    <organization>
        <uuid>{0}</uuid>
        <id>{1}</id>
        <name>{2}</name>
        <parent-org>{3}</parent-org>
        <subscription-plan>Default-All-Services-Plan</subscription-plan>
        <cms-orgs>
            <uuid>{4}</uuid>
            <name>{5}</name>
            <cms-connector>local</cms-connector>
        </cms-orgs>
     </organization>""".format(org_uuid, random.randint(1, 1000), org_name,
                               parent, cms_org_uuid, cms_org_name)
    client.post(url, xmldata, XML, codes.created)
    return org_uuid


def delete_organization(client, org_uuid):
    url = "/api/config/nms/actions/delete-organization"
    data = {"delete-organization": {"orguuid":  org_uuid}}
    return client.post(url, json.dumps(data), JSON, codes.ok)


def add_appliance(client, mgm_ip, name, org, cmsorg, net):
    url = "/api/config/nms/actions/add-devices"
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
                    <network-info>
                        <network-name>{4}</network-name>
                        <ip-address>{5}</ip-address>
                        <interface>{6}</interface>
                    </network-info>
                    <network-info>
                        <network-name>{7}</network-name>
                        <ip-address>{8}</ip-address>
                        <interface>{9}</interface>
                    </network-info>
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
    </add-devices> """.format(mgm_ip, name, org, cmsorg,
                              net[0].name, net[0].address, net[0].interface,
                              net[1].name, net[1].address, net[1].interface)
    result = client.post(url, xmldata, XML, codes.ok)
    return _get_task_id(result)


def associate_org_via_network(client, appliance, org, network_info):
    url = '/api/config/nms/actions/'\
        '/associate-organization-to-appliance'
    appliance_uuid = get_appliance_uuid(client, appliance)
    org_uuid = get_organization_uuid(client, org)
    data = {
        "associate-organization-to-appliance": {
            "orguuid": org_uuid,
            "networking-info": {
                "network-info": [{
                    "network-name": network_info.name,
                    "parent-interface": network_info.parent,
                    "vlan-id": network_info.vlan,
                    "ipaddress-allocation-mode": "MANUAL",
                    "slot": "0",
                    "ip-address": network_info.address,
                    "mask": network_info.mask}]},
            "applianceuuid": appliance_uuid,
            "subscription": {
                "solution-tier": "nextgen-firewall",
                "bandwidth": "100"}}}
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    result = client.post(url, json.dumps(data), JSON, codes.ok)
    return _get_task_id(result)


def associate_org_via_services(client, appliance, org, services):
    url = '/api/config/nms/actions'\
        '/associate-organization-to-appliance'
    appliance_uuid = get_appliance_uuid(client, appliance)
    org_uuid = get_organization_uuid(client, org)
    data = {
        "associate-organization-to-appliance": {
            "orguuid": org_uuid,
            "networking-info": {"network-info": []},
            "services": services,
            "applianceuuid": appliance_uuid,
            "subscription": {
                "solution-tier": "nextgen-firewall",
                "bandwidth": "100"}}}
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
    for app in result['appliance']:
        if app['name'] == name:
            return app['uuid']
    return None


def delete_appliance(client, uuid):
    url = "/api/config/nms/actions/delete-appliance"
    data = {
        "delete-appliance": {
            "applianceuuid": uuid,
            "dopostdelete": "true",
            "clean-config": "true"}}
    result = client.post(url, json.dumps(data), JSON, codes.ok)
    return _get_task_id(result)


def get_organization(client, name):
    url = "/api/config/nms/provider/organizations?deep"
    result = client.get(url, None, None)
    for org in result['organizations']['organization']:
        if name == org['name']:
            return org
    return None


def get_organization_uuid(client, name):
    url = "/api/config/nms/provider/organizations?deep"
    result = client.get(url, None, None)
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
