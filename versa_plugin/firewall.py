import json
from requests import codes
from versa_plugin.versaclient import JSON
from collections import namedtuple

BlackList = namedtuple("BlackList", "name, actions, patterns, strings")
WhiteList = namedtuple("WhiteList", "name, patterns, strings")
CategoryAction = namedtuple("CategoryAction", "name, action, categories")
ReputationAction = namedtuple("ReputationAction", "name, action, reputations")


def add_policy(client, appliance, org, policy):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
        '/security/access-policies'.format(appliance, org)
    data = {"access-policy-group": policy}
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_policy(client, appliance, org, policy):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/access-policies/access-policy-group/{}'.format(appliance,
                                                                    org, policy)
    client.delete(url)


def add_rule(client, appliance, org, policy, rule):
    """
        :param  appliance (str)
        :param org (str)
        :param policy (str)
        :param rule (dict): firewall rule properties
    """
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules'.format(appliance, org, policy)
    data = {
        "access-policy": rule}
    client.post(url, json.dumps(data), JSON, codes.created)


def update_rule(client, appliance, org, policy, rule):
    """
        :param  appliance (str)
        :param org (str)
        :param policy (str)
        :param rule (dict): firewall rule properties
    """
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules/access-policy/{}'.format(appliance,
                                                               org, policy,
                                                               rule['name'])
    data = {
        "access-policy": rule}
    client.put(url, json.dumps(data), JSON, codes.no_content)


def delete_rule(client, appliance, org, policy, rule):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}/'\
        'security/access-policies'\
        '/access-policy-group/{}/rules/access-policy/{}'.format(appliance,
                                                                org, policy,
                                                                rule)
    client.delete(url)


def add_url_filter(client, appliance, org, url_filter):
    """
        :param appliance (str)
        :param org (str)
        :url_filter (dict)
    """
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/profiles/url-filtering'.format(appliance, org)
    data = {
        "url-filtering-profile": url_filter
    }
    client.post(url, json.dumps(data), JSON, codes.created)


def delete_url_filter(client, appliance, org, url_filter):
    """
        :param appliance (str)
        :param org (str)
        :url_filter (dict)
    """
    name = url_filter['name']
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/profiles/url-filtering/url-filtering-profile/{}'\
          .format(appliance, org, name)
    client.delete(url)


def _prepare_blacklist(lists):
    if lists:
        return {
            "action": {
                "predefined": lists.action},
            "patterns": lists.patterns,
            "strings": lists.strings}
    else:
        return {}


def _prepare_whitelist(lists):
    if lists:
        return {"patterns": lists.patterns,
                "strings": lists.strings}
    else:
        return {}


def _prepare_categories(actions):
    if actions:
        return [{"name": cat.name, "action": {
            "predefined": cat.action},
            "url-categories": {"predefined": cat.categories}}
                for cat in actions]
    else:
        return {}


def _prepare_reputations(actions):
    if actions:
        return [{"name": rep.name, "action": {
            "predefined": rep.action},
            "url-reputations": {"predefined": rep.reputations}}
            for rep in actions]
    else:
        return {}
