import json
from requests import codes
from versa_plugin.versaclient import JSON
from collections import namedtuple

BlackList = namedtuple("BlackList", "name, actions, patterns, strings")
WhiteList = namedtuple("WhiteList", "name, patterns, strings")
CategoryAction = namedtuple("CategoryAction", "name, action, categories")
ReputationAction = namedtuple("ReputationAction", "name, action, reputations")


def add_policy(versa, policy):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
        '/security/access-policies'.format(versa.appliance, versa.organization)
    data = {"access-policy-group": policy}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_policy(versa, policy):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/access-policies'\
          '/access-policy-group/{}'.format(versa.appliance, versa.organization,
                                           policy)
    versa.client.delete(url)


def add_rule(versa, policy, rule):
    """
        :param  appliance (str)
        :param org (str)
        :param policy (str)
        :param rule (dict): firewall rule properties
    """
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules'.format(versa.appliance,
                                              versa.organization, policy)
    data = {"access-policy": rule}
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def update_rule(versa, policy, rule):
    """
        :param policy (str)
        :param rule (dict): firewall rule properties
    """
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group'\
        '/{}/rules/access-policy/{}'.format(versa.appliance,
                                            versa.organization, policy,
                                            rule['name'])
    data = {"access-policy": rule}
    versa.client.put(url, json.dumps(data), JSON, codes.no_content)


def reorder_rules(versa, policy, rules):
    """
        :param  appliance (str)
        :param org (str)
        :param policy (str)
        :param rules (list): firewall rules with new order
    """
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules'.format(versa.appliance, versa.org, policy)
    data = {"rules": {"access-policy": rules}}
    versa.client.put(url, json.dumps(data), JSON, codes.no_content)


def get_rule(versa, policy, name):
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules?deep'.format(versa.appliance,
                                                   versa.organization, policy)
    result = versa.client.get(url, None, None, codes.ok, JSON)
    if not result:
        return None
    for rule in result['rules']['access-policy']:
        if name == rule['name']:
            return rule
    return None


def get_all_rules(versa, policy):
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules?deep'.format(versa.appliance,
                                                   versa.org, policy)
    result = versa.client.get(url, None, None, codes.ok, JSON)
    if not result:
        return None
    return result['rules']['access-policy']

def delete_rule(versa, policy, rule):
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}/'\
        'security/access-policies'\
        '/access-policy-group'\
        '/{}/rules/access-policy/{}'.format(versa.appliance,
                                            versa.organization, policy, rule)
    versa.client.delete(url)


def add_url_filter(versa, url_filter):
    """
        :url_filter (dict)
    """
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/profiles/url-filtering'.format(versa.appliance,
                                                    versa.organization)
    data = {
        "url-filtering-profile": url_filter
    }
    versa.client.post(url, json.dumps(data), JSON, codes.created)


def delete_url_filter(versa, url_filter):
    """
        :param appliance (str)
        :param org (str)
        :url_filter (dict)
    """
    name = url_filter['name']
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/profiles/url-filtering/url-filtering-profile/{}'\
          .format(versa.appliance, versa.organization, name)
    versa.client.delete(url)


def update_captive_portal(versa, portal):
    url = '/api/config/devices/device/{}/config/orgs'\
          '/org-services/{}/security/captive-portal'.format(versa.appliance, versa.org)
    data = {"captive-portal": portal}
    versa.client.put(url, json.dumps(data), JSON, codes.no_content)


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
