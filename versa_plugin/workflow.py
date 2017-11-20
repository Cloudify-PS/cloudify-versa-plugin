import json
from requests import codes
from versa_plugin.versaclient import JSON


def _get_task_id(task_info):
    return task_info['TaskResponse']['task-id']


def _get_new_id(client):
    url = '/vnms/sdwan/global/Branch/availableId/withSerialNumber'
    result = client.get(url, None, None, codes.ok)
    return result['AvailableIDResponseModel']['branchId']


def _substitute_vars(body, vars):
    keys = vars.keys()
    for i in body['versanms.sdwan-device-workflow']["postStagingTemplateInfo"]["templateData"]["device-template-variable"]["variable-binding"]["attrs"]:
        if i['name'] in keys:
            i['value'] = vars[i['name']]


def create_device(client, config):
    new_id = _get_new_id(client)
    name = "CPE2"
    data = {"versanms.sdwan-device-workflow":
            {"deviceName": name, "siteId": new_id,
             "orgName": "Provider", "deviceGroup": "CPE1",
             "locationInfo": {"country": "nl",
                              "longitude": "0", "latitude": "0"}}}
    template_vars = {"{$v_Lan_IPv4__staticaddress}": "192.168.1.1/32",
                     "{$v_mpls_IPv4__staticaddress}":  "192.168.2.2/32",
                     "{$v_mpls-Transport-VR_IPv4__vrHopAddress}": "192.168.3.3"}
    url = "/vnms/sdwan/workflow/devices/device/template/data/{}".format(name)
    reply = client.post(url, json.dumps(data), JSON, codes.ok)
    _substitute_vars(reply, template_vars)
    url = "/vnms/sdwan/workflow/devices/device"
    client.post(url, json.dumps(reply), JSON, codes.ok)
    url = "/vnms/sdwan/workflow/devices/device/deploy/{}".format(name)
    result = client.post(url, None, JSON, codes.accepted)
    return _get_task_id(result)
