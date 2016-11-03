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


def add_rule(client, appliance, org, policy, rule_name):
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules'.format(appliance, org, policy)
    data = {
        "access-policy": {
            "name": rule_name,
            "match": {
                "source": {
                    "zone": {
                        "zone-list": ["trust"]}},
                "destination": {
                    "zone": {
                        "zone-list": ["untrust"]}}},
            "set": {
                "lef": {
                    "event": "end",
                    "options": {
                        "send-pcap-data": {
                            "enable": False}}},
                "action": "allow"}}}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_rule(client, appliance, org, policy, rule):
    url = 'api/config/devices/device/{}/config/orgs/org-services/{}/'\
        'security/access-policies'\
        '/access-policy-group/{}/rules/access-policy/{}'.format(appliance,
                                                                org, policy,
                                                                rule)
    client.delete(url, None, None, codes.no_content)


def add_url_filer(client, appliance, org, name, action, patterns, strings):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/profiles/url-filtering'.format(appliance, org)
    data = {
        "url-filtering-profile": {
            "name": name,
            "cloud-lookup-mode": "never",
            "category-action-map": {
                "category-action": []},
            "reputation-action-map": {
                "reputation-action": []},
            "blacklist": {
                "action": {
                    "predefined": action},
                "patterns": patterns,
                "strings": strings},
            "whitelist": {}}}
    client.post(url, json.dumps(data), JSON, codes.created)
