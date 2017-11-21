from cloudify import ctx
from cloudify import exceptions as cfy_exc
from cloudify.decorators import operation
import versa_plugin
from copy import deepcopy

from versa_plugin import with_versa_client
from versa_plugin import get_mandatory
import versa_plugin.appliance
import versa_plugin.cgnat
import versa_plugin.connectors
import versa_plugin.dhcp
import versa_plugin.firewall
import versa_plugin.networking
import versa_plugin.tasks
import versa_plugin.vpn
import versa_plugin.limits
from versa_plugin.cgnat import AddressRange
from collections import namedtuple

ApplianceContext = namedtuple("ApplianceContext",
                              "client, appliance, organization")


def is_use_existing():
    return ctx.node.properties.get('use_existing')


def reqursive_update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, dict):
            r = reqursive_update(d.get(k, {}), v)
            d[k] = r
        elif isinstance(v, list):
            if isinstance(u[k], list):
                d[k] = d.setdefault(k, []) + u[k]
            else:
                d[k] = d.setdefault(k, []) + [u[k]]
        else:
            d[k] = u[k]
    return d


def _get_node_configuration(key, kwargs):
    value = ctx.node.properties.get(key, {})
    value.update(kwargs.get(key, {}))
    if value:
        return value
    else:
        raise cfy_exc.NonRecoverableError(
            "Configuration parameter {0} is absent".format(key))


def _get_context(client):
    appliance = get_mandatory(ctx.node.properties, 'appliance_name')
    org = ctx.node.properties.get('org_name', None)
    return ApplianceContext(client, appliance, org)


@operation
@with_versa_client
def create_resource_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    instance = _get_node_configuration('instance', kwargs)
    versa_plugin.connectors.add_resource_pool(versa_client, instance)


@operation
@with_versa_client
def delete_resource_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    instance = _get_node_configuration('instance', kwargs)
    name = get_mandatory(instance, 'name')
    versa_plugin.connectors.delete_resource_pool(versa_client, name)


@operation
@with_versa_client
def create_cms_local_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    versa_plugin.connectors.add_organization(versa_client, organization)


@operation
@with_versa_client
def delete_cms_local_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    name = get_mandatory(organization, 'name')
    versa_plugin.connectors.delete_organization(versa_client, name)


@operation
@with_versa_client
def create_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    versa_plugin.appliance.add_organization(versa_client, organization)


@operation
@with_versa_client
def delete_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    name = get_mandatory(organization, 'name')
    versa_plugin.appliance.delete_organization(versa_client, name)


@operation
@with_versa_client
def create_appliance(versa_client, **kwargs):
    if is_use_existing():
        return
    device = _get_node_configuration('device', kwargs)
    management_ip = get_mandatory(device, 'mgmt-ip')
    versa_plugin.appliance.wait_for_device(versa_client, management_ip, ctx)
    task = versa_plugin.appliance.add_appliance(versa_client, device)
    versa_plugin.tasks.wait_for_task(versa_client, task, ctx)


@operation
@with_versa_client
def delete_appliance(versa_client, **kwargs):
    if is_use_existing():
        return
    device = _get_node_configuration('device', kwargs)
    name = get_mandatory(device, 'name')
    task = versa_plugin.appliance.delete_appliance(versa_client, name)
    versa_plugin.tasks.wait_for_task(versa_client, task, ctx)


@operation
@with_versa_client
def associate_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    appliance = get_mandatory(organization, 'appliance')
    net_info = get_mandatory(organization, 'networking-info')
    for net in net_info:
        interface_name = get_mandatory(get_mandatory(net, 'network-info'),
                                       'parent-interface')
        interface = {"name": interface_name, "enable": True,
                     "promiscuous": False}
        versa_plugin.networking.create_interface(versa_client, appliance,
                                                 interface)
    task = versa_plugin.appliance.associate_organization(versa_client,
                                                         organization)
    versa_plugin.tasks.wait_for_task(versa_client, task, ctx)


@operation
@with_versa_client
def create_router(versa_client, **kwargs):
    if is_use_existing():
        return
    context = _get_context(versa_client)
    router = _get_node_configuration('router', kwargs)
    if versa_plugin.networking.is_router_exists(context, router):
        raise cfy_exc.NonRecoverableError("Router exists")
    versa_plugin.networking.create_virtual_router(context, router)


@operation
@with_versa_client
def delete_router(versa_client, **kwargs):
    if is_use_existing():
        return
    context = _get_context(versa_client)
    router = _get_node_configuration('router', kwargs)
    router_name = router['name']
    if versa_plugin.networking.is_router_exists(context, router_name):
        versa_plugin.networking.delete_virtual_router(context, router_name)


@operation
@with_versa_client
def insert_to_router(versa_client, **kwargs):
    if is_use_existing():
        return
    context = _get_context(versa_client)
    router = _get_node_configuration('router', kwargs)
    router_name = router['name']
    networks = ctx.node.properties.get('networks', [])
    for name in networks:
        versa_plugin.networking.add_network_to_router(
            context, router_name, name)


@operation
@with_versa_client
def delete_from_router(versa_client, **kwargs):
    if is_use_existing():
        return
    context = _get_context(versa_client)
    networks = ctx.node.properties.get('networks', [])
    router_name = ctx.node.properties['name']
    for name in networks:
        versa_plugin.networking.delete_network_from_router(
            context, router_name, name)


@operation
@with_versa_client
def create_cgnat(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    pool = ctx.node.properties['pool']
    pool_name = pool['name']
    ranges = [AddressRange(r['name'], r['low'], r['hight'])
              for r in pool['ranges']]
    routing_instance = pool['routing_instance']
    provider_org = pool['provider_org']
    versa_plugin.cgnat.create_pool(versa_client, appliance_name,
                                   org_name, pool_name,
                                   ranges, routing_instance,
                                   provider_org)
    rule = ctx.node.properties['rule']
    rule_name = rule['name']
    source_addresses = rule['addresses']
    versa_plugin.cgnat.create_rule(versa_client, appliance_name,
                                   org_name, rule_name,
                                   source_addresses, pool_name)


@operation
@with_versa_client
def delete_cgnat(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    pool = ctx.node.properties['pool']
    pool_name = pool['name']
    rule = ctx.node.properties['rule']
    rule_name = rule['name']
    versa_plugin.cgnat.delete_rule(versa_client, appliance_name,
                                   org_name, rule_name)
    versa_plugin.cgnat.delete_pool(versa_client, appliance_name,
                                   org_name, pool_name)


@operation
@with_versa_client
def create_zone(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    zone = ctx.node.properties['zone']
    zone_name = zone['name']
    zone_exsists = versa_plugin.networking.get_zone(versa_client,
                                                    appliance_name,
                                                    org_name,
                                                    zone_name)
    if zone_exsists:
        raise cfy_exc.NonRecoverableError(
            "Zone '{}' exsists".format(zone_name))
    versa_plugin.networking.create_zone(versa_client,
                                        appliance_name,
                                        org_name, zone)


@operation
@with_versa_client
def insert_to_zone(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    zone = ctx.node.properties['zone']
    zone_name = zone['name']
    zone_exsists = versa_plugin.networking.get_zone(versa_client,
                                                    appliance_name,
                                                    org_name,
                                                    zone_name)
    if zone_exsists:
        ctx.instance.runtime_properties[zone_name] = deepcopy(zone_exsists)
        new_zone = reqursive_update(zone_exsists, zone)
        versa_plugin.networking.update_zone(versa_client,
                                            appliance_name,
                                            org_name, new_zone)


@operation
@with_versa_client
def delete_zone(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    zone = ctx.node.properties['zone']
    zone_name = zone['name']
    versa_plugin.networking.delete_zone(versa_client,
                                        appliance_name,
                                        org_name, zone_name)


@operation
@with_versa_client
def delete_from_zone(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    zone = ctx.node.properties['zone']
    zone_name = zone['name']
    old_zone = ctx.instance.runtime_properties.get(zone_name, None)
    if old_zone:
        versa_plugin.networking.update_zone(versa_client,
                                            appliance_name,
                                            org_name, old_zone)


@operation
@with_versa_client
def create_firewall_policy(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    policy = ctx.node.properties['policy']
    versa_plugin.firewall.add_policy(versa_client, appliance_name,
                                     org_name, policy)


@operation
@with_versa_client
def delete_firewall_policy(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    policy = ctx.node.properties['policy']
    versa_plugin.firewall.delete_policy(versa_client, appliance_name,
                                        org_name, policy['name'])


@operation
@with_versa_client
def create_firewall_rule(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    policy_name = ctx.node.properties['policy_name']
    rule = ctx.node.properties['rule']
    ctx.instance.runtime_properties['rules'] = {}
    ctx.instance.runtime_properties['appliance'] = appliance_name
    ctx.instance.runtime_properties['org'] = org_name
    ctx.instance.runtime_properties['policy'] = policy_name
    name = rule['name']
    ctx.instance.runtime_properties['rules'][name] = rule
    versa_plugin.firewall.add_rule(versa_client, appliance_name,
                                   org_name, policy_name, rule)
    if ctx.node.properties['on_top']:
        all_rules = versa_plugin.firewall.get_all_rules(versa_client,
                                                        appliance_name,
                                                        org_name, policy_name)
        sorted_list = []
        for rule in all_rules:
            if rule['name'] == name:
                sorted_list.insert(0, rule)
            else:
                sorted_list.append(rule)
        versa_plugin.firewall.reorder_rules(versa_client, appliance_name,
                                            org_name, policy_name, sorted_list)


@operation
@with_versa_client
def update_firewall_rule(versa_client, **kwargs):
    rule = kwargs.get('rule')
    if not rule:
        return
    name = rule.get('name')
    if not name:
        ctx.logger.info("Key 'name' in rule is absent.")
        return
    old_rule = ctx.instance.runtime_properties['rules'].get(name)
    if not old_rule:
        ctx.logger.info("Rule: '{}' not found.".format(name))
        return
    reqursive_update(rule, old_rule)
    appliance_name = ctx.instance.runtime_properties['appliance']
    org_name = ctx.instance.runtime_properties['org']
    policy_name = ctx.instance.runtime_properties['policy']
    versa_plugin.firewall.update_rule(versa_client, appliance_name,
                                      org_name, policy_name, rule)


@operation
@with_versa_client
def get_firewall_rule(versa_client, **kwargs):
    name = kwargs.get('name')
    if not name:
        ctx.logger.info("Key 'name' is absent.")
        return
    appliance_name = ctx.instance.runtime_properties['appliance']
    org_name = ctx.instance.runtime_properties['org']
    policy_name = ctx.instance.runtime_properties['policy']
    rule = versa_plugin.firewall.get_rule(versa_client, appliance_name,
                                          org_name, policy_name, name)
    ctx.logger.info("Rule '{} is: {}".format(name, rule))


@operation
@with_versa_client
def delete_firewall_rule(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    policy_name = ctx.node.properties['policy_name']
    rule = ctx.node.properties['rule']
    versa_plugin.firewall.delete_rule(versa_client, appliance_name,
                                      org_name, policy_name, rule['name'])


@operation
@with_versa_client
def create_url_filters(versa_client, **kwargs):
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    url_filters = ctx.node.properties['filters']
    for url_filter in url_filters:
        ctx.logger.info("Filter: {}".format(url_filter))
        versa_plugin.firewall.add_url_filter(versa_client, appliance_name,
                                             org_name, url_filter)


@operation
@with_versa_client
def delete_url_filters(versa_client, **kwargs):
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    url_filters = ctx.node.properties['filters']
    for url_filter in url_filters:
        ctx.logger.info("Filter: {}".format(url_filter))
        versa_plugin.firewall.delete_url_filter(versa_client, appliance_name,
                                                org_name, url_filter)


@operation
@with_versa_client
def create_dhcp_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    profile_name = ctx.node.properties['profile_name']
    if versa_plugin.limits.is_dhcp_profile_exists(versa_client,
                                                  appliance_name,
                                                  profile_name):
        raise cfy_exc.NonRecoverableError("Dhcp profile exists")
    versa_plugin.limits.create_dhcp_profile(versa_client, appliance_name,
                                            profile_name)


@operation
@with_versa_client
def delete_dhcp_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    profile_name = ctx.node.properties['profile_name']
    if versa_plugin.limits.is_dhcp_profile_exists(versa_client,
                                                  appliance_name,
                                                  profile_name):
        versa_plugin.limits.delete_dhcp_profile(versa_client,
                                                appliance_name,
                                                profile_name)


@operation
@with_versa_client
def create_dhcp_lease_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    lease_name = ctx.node.properties['lease_profile']
    versa_plugin.dhcp.create_lease_profile(versa_client, appliance_name,
                                           org_name, lease_name)


@operation
@with_versa_client
def delete_dhcp_lease_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    lease_name = ctx.node.properties['lease_profile']
    if versa_plugin.dhcp.is_lease_profile_exsists(versa_client, appliance_name,
                                                  org_name, lease_name):
        versa_plugin.dhcp.delete_lease_profile(versa_client, appliance_name,
                                               org_name, lease_name)


@operation
@with_versa_client
def create_dhcp_options_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    options_name = ctx.node.properties['name']
    domain = ctx.node.properties['domain']
    servers = ctx.node.properties['servers']
    versa_plugin.dhcp.create_options_profile(versa_client, appliance_name,
                                             org_name, options_name,
                                             domain, servers)


@operation
@with_versa_client
def delete_dhcp_options_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    options_name = ctx.node.properties['name']
    if versa_plugin.dhcp.is_dhcp_profile_exists(versa_client, appliance_name,
                                                org_name, options_name):
        versa_plugin.dhcp.delete_options_profile(versa_client, appliance_name,
                                                 org_name, options_name)


@operation
@with_versa_client
def create_dhcp_global_configuration(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    lease_profile = ctx.node.properties['lease_profile']
    options_profile = ctx.node.properties['options_profile']
    versa_plugin.dhcp.update_global_configuration(versa_client, appliance_name,
                                                  org_name, lease_profile,
                                                  options_profile)


@operation
@with_versa_client
def delete_dhcp_global_configuration(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    lease_profile = []
    options_profile = []
    versa_plugin.dhcp.update_global_configuration(versa_client, appliance_name,
                                                  org_name, lease_profile,
                                                  options_profile)


@operation
@with_versa_client
def create_dhcp_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    lease_profile = ctx.node.properties['lease_profile']
    options_profile = ctx.node.properties['options_profile']
    pool_name = ctx.node.properties['name']
    mask = ctx.node.properties['mask']
    range_name = ctx.node.properties['range_name']
    begin_address = ctx.node.properties['begin_address']
    end_address = ctx.node.properties['end_address']
    versa_plugin.dhcp.create_pool(versa_client, appliance_name, org_name,
                                  pool_name, mask, lease_profile,
                                  options_profile,
                                  range_name, begin_address, end_address)


@operation
@with_versa_client
def delete_dhcp_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    pool_name = ctx.node.properties['name']
    if versa_plugin.dhcp.is_pool_exists(versa_client, appliance_name,
                                        org_name, pool_name):
        versa_plugin.dhcp.delete_pool(versa_client, appliance_name, org_name,
                                      pool_name)


@operation
@with_versa_client
def create_dhcp_server(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    lease_profile = ctx.node.properties['lease_profile']
    options_profile = ctx.node.properties['options_profile']
    pool_name = ctx.node.properties['pool_name']
    server_name = ctx.node.properties['name']
    networks = ctx.node.properties['networks']
    versa_plugin.dhcp.create_server(versa_client, appliance_name, org_name,
                                    server_name, lease_profile, options_profile,
                                    networks, pool_name)


@operation
@with_versa_client
def delete_dhcp_server(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    server_name = ctx.node.properties['name']
    if versa_plugin.dhcp.is_server_exists(versa_client, appliance_name,
                                          org_name, server_name):
        versa_plugin.dhcp.delete_server(versa_client, appliance_name, org_name,
                                        server_name)


@operation
@with_versa_client
def create_interface(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    interface = _get_node_configuration('interface', kwargs)
    versa_plugin.networking.create_interface(versa_client, appliance_name,
                                             interface)


@operation
@with_versa_client
def delete_interface(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    interface = _get_node_configuration('interface', kwargs)
    name = interface['name']
    versa_plugin.networking.delete_interface(versa_client, appliance_name,
                                             name)


@operation
@with_versa_client
def create_network(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    network = _get_node_configuration('network', kwargs)
    if versa_plugin.networking.is_network_exists(versa_client,
                                                 appliance_name,
                                                 network):
        raise cfy_exc.NonRecoverableError("Network exists")
    versa_plugin.networking.create_network(versa_client, appliance_name,
                                           network)


@operation
@with_versa_client
def delete_network(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    network = _get_node_configuration('network', kwargs)
    name = network['name']
    if versa_plugin.networking.is_network_exists(versa_client,
                                                 appliance_name,
                                                 name):
        versa_plugin.networking.delete_network(versa_client, appliance_name,
                                               name)


@operation
@with_versa_client
def insert_to_limits(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    dhcp_profile = ctx.node.properties.get('dhcp_profile')
    routes = ctx.node.properties.get('routes', [])
    networks = ctx.node.properties.get('networks', [])
    interfaces = ctx.node.properties.get('interfaces', [])
    provider_orgs = ctx.node.properties.get('provider_orgs', [])
    if dhcp_profile:
        versa_plugin.limits.insert_dhcp_profile_to_limits(versa_client,
                                                          appliance_name,
                                                          org_name,
                                                          dhcp_profile)
    for name in routes:
        versa_plugin.limits.add_routing_instance(versa_client,
                                                 appliance_name,
                                                 org_name, name)
    for name in networks:
        versa_plugin.limits.add_traffic_identification_networks(
            versa_client, appliance_name, org_name, name, 'using-networks')
    for name in interfaces:
        versa_plugin.limits.add_traffic_identification_networks(
            versa_client, appliance_name, org_name, name, 'using')
    for name in provider_orgs:
        versa_plugin.limits.add_provider_organization(versa_client,
                                                      appliance_name,
                                                      org_name,
                                                      name)


@operation
@with_versa_client
def delete_from_limits(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    dhcp_profile = ctx.node.properties.get('dhcp_profile')
    routes = ctx.node.properties.get('routes', [])
    networks = ctx.node.properties.get('networks', [])
    interfaces = ctx.node.properties.get('interfaces', [])
    provider_orgs = ctx.node.properties.get('provider_orgs', [])
    for name in routes:
        versa_plugin.limits.delete_routing_instance(versa_client,
                                                    appliance_name,
                                                    org_name, name)
    for name in networks:
        versa_plugin.limits.delete_traffic_identification_networks(
            versa_client, appliance_name, org_name, name, 'using-networks')
    for name in interfaces:
        versa_plugin.limits.delete_traffic_identification_networks(
            versa_client, appliance_name, org_name, name, 'using')
    for name in provider_orgs:
        versa_plugin.limits.delete_provider_organization(versa_client,
                                                         appliance_name,
                                                         org_name,
                                                         name)
    if dhcp_profile:
        versa_plugin.limits.delete_dhcp_profile_from_limits(versa_client,
                                                            appliance_name,
                                                            org_name,
                                                            dhcp_profile)


@operation
@with_versa_client
def create_vpn_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    profile = _get_node_configuration('profile', kwargs)
    name = profile['name']
    if versa_plugin.vpn.is_profile_exists(versa_client,
                                          appliance_name, org_name,
                                          name):
        raise cfy_exc.NonRecoverableError("VPN profile exists")
    versa_plugin.vpn.create_profile(versa_client, appliance_name, org_name,
                                    profile)


@operation
@with_versa_client
def delete_vpn_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    profile = _get_node_configuration('profile', kwargs)
    name = profile['name']
    if versa_plugin.vpn.is_profile_exists(versa_client,
                                          appliance_name, org_name,
                                          name):
        versa_plugin.vpn.delete_profile(versa_client, appliance_name, org_name,
                                        name)


@operation
@with_versa_client
def insert_captive_portal(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    portal = _get_node_configuration('captive_portal', kwargs)
    versa_plugin.firewall.update_captive_portal(versa_client, appliance_name,
                                                org_name, portal)


@operation
@with_versa_client
def clean_captive_portal(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    portal = {"port": "0", "track-by-host": False, "expiration-time": "30",
              "custom-pages": {}}
    versa_plugin.firewall.update_captive_portal(versa_client, appliance_name,
                                                org_name, portal)


@operation
@with_versa_client
def update_template(versa_client, **kwargs):
    config = _get_node_configuration('config', kwargs)
    if not config:
        ctx.logger.info("Key 'parameters' is absent.")
        return
    versa_plugin.template.update(versa_client, config)


@operation
@with_versa_client
def create_device(versa_client, **kwargs):
    parameters = kwargs.get('parameters')
    if not parameters:
        ctx.logger.info("Key 'parameters' is absent.")
        return
    versa_plugin.template.update(versa_client, parameters)
