import json
from requests import codes
from versa_plugin.versaclient import JSON


def add_policy(client, appliance, org, policy):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
        '/security/access-policies'.format(appliance, org)
    data = {"access-policy-group": {"name": policy}}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_policy(client, appliance, org, policy):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/access-policies/access-policy-group/{}'.format(appliance,
                                                                    org, policy)
    client.delete(url, None, None, codes.no_content)


def add_rule(client, appliance, org, policy, rule):
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules'.format(appliance, org, policy, rule)
    data = {}
    client.post(url, json.dumps(data), JSON, codes.created)
"""
    {"access-policy":{"name":"newrule","match":{"source":{"zone":{"zone-list":["trust"]},"address":{}},"destination":{"zone":{"zone-list":["untrust"]},"address":{}},"application":{},"ttl":{}},"set":{"lef":{"event":"end","options":{"send-pcap-data":{"enable":false}}},"action":"allow"}}}"
"""


def delete_rule(client, appliance, org, policy, rule):
    url = 'api/config/devices/device/{}/config/orgs/org-services/{}/'\
        'security/access-policies'\
        '/access-policy-group/{}/rules/access-policy/{}'.format(appliance,
                                                                org, policy,
                                                                rule)
    client.delete(url, None, None, codes.no_content)
