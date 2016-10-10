import json
from versa_plugin.versaclient import JSON
from requests import codes
from collections import namedtuple


AddressRange = namedtuple("AddressRange", "name, low, high")


def create_pool(client, appliance, org, pool_name, addresses,
                ranges):
    """
        :param client - versa client "str"
        :param appliance - appliance name "str"
        :param org - organization name "str"
        :param pool_name - pool name "str"
        :param addresses - list of addrres in format ["addr, "addr"]
        :param ranges - list of type AddressRange [range1, range2]
    """
    url = '/api/config/appliances/{}/orgs/org-services/{}/cgnat'.format(
        appliance, org)
    range_list = [{'name': r.name,
                   'low': r.low,
                   'hight': r.hight} for r in ranges]
    data = {
        "pool": {
            "name": pool_name,
            "address": addresses,
            "icmp-mapping-timeout": "60",
            "udp-mapping-timeout": "300",
            "tcp-mapping-timeout": "7440",
            "address-allocation": "round-robin",
            "address-range": {
                'range': range_list}}}
    pools = client.post(url, json.dumps(data), JSON, codes.created)
    return pools


def create_rule(client, appliance, org, rule_name, source_zone,
                source_addresses,
                source_ranges, dest_zone, dest_addresses, dest_ranges,
                translation_type):
    """
        :param client - versa client "str"
        :param appliance - appliance name "str"
        :param org - organization name "str"
        :param rule_name - rule name "str"
        :param source_zone - source_zone "str"
        :param source_addresses - list in format ["10.0.0.0/8", ... ]
        :param source_ranges - list of type AddressRange [range1, range2]
        :param dest_zone - dest_zone "str"
        :param dest_addresses - list in format ["10.0.0.0/8", ... ]
        :param dest_ranges - list of type AddressRange [range1, range2]
        :param translation_type - type of translation "str"
    """
    url = '/api/config/appliances/{}/orgs/org-services/{}/cgnat'.format(
        appliance, org)
    source_range_list = [{'name': r.name,
                          'low': r.low,
                          'hight': r.hight} for r in source_ranges]
    dest_range_list = [{'name': r.name,
                        'low': r.low,
                        'hight': r.hight} for r in dest_ranges]
    data = {
        "rule": {
            "name": rule_name,
            "precedence": "1",
            "from": {
                "source-zone": [source_zone],
                "source-address": source_addresses,
                "source-address-range": {
                    "range": source_range_list}},
            "destination-zone": [dest_zone],
            "destination-address": dest_addresses,
            "destination-address-range": {
                    "range": dest_range_list}},
            "then": {
                "translated": {
                    "translation-type": translation_type,
                    "source-pool": "pool1"}}}
    rules = client.post(url, json.dumps(data), JSON, codes.created)
    return rules


def get_list_nat_pools(client, appliance, org):
    url = '/api/config/appliances/{}/orgs/org-services/{}/cgnat/pools/pool'.\
        format(appliance, org)
    pools = client.get(url, None, None, codes.ok)
    return pools


def get_list_nat_rules(client, appliance, org):
    url = '/api/config/appliances/{}/orgs/org-services/{}/cgnat/rules/rule'.\
        format(appliance, org)
    pools = client.get(url, None, None, codes.ok)
    return pools
