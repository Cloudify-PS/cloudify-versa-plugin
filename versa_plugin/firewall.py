import json
from requests import codes
from versa_plugin.versaclient import JSON
from collections import namedtuple


Rule = namedtuple("Rule", "name")
BlackList = namedtuple("BlackList", "name, actions, patterns, strings")
WhiteList = namedtuple("WhiteList", "name, patterns, strings")
CategoryAction = namedtuple("CategoryAction", "name, action, categories")
ReputationAction = namedtuple("ReputationAction", "name, action, reputations")


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


def add_rule(client, appliance, org, policy, rules):
    """
        :param  appliance (str)
        :param org (str)
        :param policy (str)
        :param rules (Rule): firewall rules properties
    """
    url = '/api/config/devices/device/{}/config/orgs'\
        '/org-services/{}/security/access-policies/'\
        'access-policy-group/{}/rules'.format(appliance, org, policy)
    for rule in rules:
        data = {
            "access-policy": {
                "name": rule.name,
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


def add_url_filter(client, appliance, org, name, blacklist=None, whitelist=None,
                   categories=None, reputations=None):
    """
        :param appliance (str)
        :param org (str)
        :param policy (str)
        :param name (str)
        :param blacklist (BlackList):
        :param whitelist (WhiteList):
        :param categories (CategoryAction):
        :param reputations (ReputationAction):
    """
    url = '/api/config/devices/device/{}/config/orgs/org-services/{}'\
          '/security/profiles/url-filtering'.format(appliance, org)
    blacklist_params = _prepare_blacklist(blacklist)
    whitelist_params = _prepare_whitelist(whitelist)
    category_action = _prepare_categories(categories)
    reputatin_action = _prepare_reputations(reputations)
    data = {
        "url-filtering-profile": {
            "name": name,
            "cloud-lookup-mode": "never",
            "category-action-map": {
                "category-action": category_action},
            "reputation-action-map": {
                "reputation-action": reputatin_action},
            "blacklist": blacklist_params,
            "whitelist": whitelist_params}}
    client.post(url, json.dumps(data), JSON, codes.created)


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
