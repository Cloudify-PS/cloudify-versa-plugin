import json
from versa_plugin.versaclient import JSON
from requests import codes
from collections import namedtuple


AddressRange = namedtuple("AddressRange", "name, low, high")


def create_pool(client, appliance, org, pool_name, addresses,
                ranges, routing_instance, provider_org):
    """
        :param client - versa client "str"
        :param appliance - appliance name "str"
        :param org - organization name "str"
        :param pool_name - pool name "str"
        :param addresses - list of addrres in format ["addr, "addr"]
        :param ranges - list of type AddressRange [range1, range2]
        :param routing_instance - routing instance "str"
        :param provider_org - provider organizarion "str"
    """
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}/cgnat/pools'.format(appliance, org)
    range_list = [{'name': r.name,
                   'low': r.low,
                   'high': r.high} for r in ranges]
    data = {
        "pool": {
            "name": pool_name,
            "address": addresses,
            "icmp-mapping-timeout": "60",
            "udp-mapping-timeout": "300",
            "tcp-mapping-timeout": "7440",
            "address-allocation": "round-robin",
            "routing-instance": routing_instance,
            "provider-org": provider_org,
            "source-port": {
                "allocation-scheme": "automatic",
                "random-allocation": ""},
            "address-range": {
                'range': range_list}}}
    pools = client.post(url, json.dumps(data), JSON, codes.created)
    return pools


def delete_pool(client, appliance, org, name):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/cgnat/pools/pool/{}'.format(appliance, org, name)
    client.delete(url, codes.no_content)


def create_rule(client, appliance, org, rule_name,
                source_addresses, source_pool):
    """
        :param client - versa client "str"
        :param appliance - appliance name "str"
        :param org - organization name "str"
        :param rule_name - rule name "str"
        :param source_addresses - list in format ["10.0.0.0/8", ... ]
        :param source_pool - source pool
    """
    url = '/api/config/appliances/{}/orgs/org-services/{}/cgnat/rules'.format(
        appliance, org)
    data = {
        "rule": {
            "name": rule_name,
            "precedence": "1",
            "from": {
                "destination-address-range": {
                    "range": []},
                "source-address": source_addresses,
                "source-address-range": {
                    "range": []}},
            "then": {
                "translated": {
                    "translation-type": "napt-44",
                    "source-pool": source_pool,
                    "filtering-type": "none",
                    "mapping-type": "none"}}}}
    rules = client.post(url, json.dumps(data), JSON, codes.created)
    return rules


def delete_rule(client, appliance, org, name):
    url = '/api/config/devices/device/{}'\
          '/config/orgs/org-services/{}'\
          '/cgnat/rules/rule/{}'.format(appliance, org, name)
    client.delete(url, codes.no_content)


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
