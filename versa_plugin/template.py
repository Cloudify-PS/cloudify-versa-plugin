import json
from requests import codes
from versa_plugin.versaclient import JSON


def update(client, config):
    template = config['template']
    org = config['organization']
    uri = config['uri']
    parameters = config['parameters']
    url = '/api/config/devices/template/{}/config/orgs/org-services/{}/class-of-service/interfaces/interface/%22{}%22'
    data = parameters
    client.post(url, json.dumps(data), JSON, codes.created)
