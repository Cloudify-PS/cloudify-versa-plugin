import json
from requests import codes
from versa_plugin.versaclient import JSON


def create(client, config):
    pass


def delete(client, config):
    pass


def update(client, config):
    template = config['template']
    org = config['organization']
    interface = config['interface']
    parameters = config['parameters']
    base_url = '/api/config/devices/template/{}/config/orgs/org-services/{}'.format(template, org)
    url = base_url + '/class-of-service/interfaces/interface/%22{}%22'.format(interface)
    data = parameters
    client.put(url, json.dumps(data), JSON, codes.created)
