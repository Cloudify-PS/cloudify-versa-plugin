from cloudify import ctx
from cloudify import exceptions as cfy_exc
from cloudify.decorators import operation
import versa_plugin
from copy import deepcopy

from versa_plugin import with_versa
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


@operation
@with_versa
def create_resource_pool(versa, **kwargs):
    if is_use_existing():
        return
    instance = _get_node_configuration('instance', kwargs)
    versa_plugin.connectors.add_resource_pool(versa, instance)


@operation
@with_versa
def delete_resource_pool(versa, **kwargs):
    if is_use_existing():
        return
    instance = _get_node_configuration('instance', kwargs)
    name = get_mandatory(instance, 'name')
    versa_plugin.connectors.delete_resource_pool(versa, name)


@operation
@with_versa
def create_cms_local_organization(versa, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    versa_plugin.connectors.add_organization(versa, organization)


@operation
@with_versa
def delete_cms_local_organization(versa, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    name = get_mandatory(organization, 'name')
    versa_plugin.connectors.delete_organization(versa, name)


@operation
@with_versa
def create_organization(versa, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    versa_plugin.appliance.add_organization(versa, organization)


@operation
@with_versa
def delete_organization(versa, **kwargs):
    if is_use_existing():
        return
    organization = _get_node_configuration('organization', kwargs)
    name = get_mandatory(organization, 'name')
    versa_plugin.appliance.delete_organization(versa, name)


@operation
@with_versa
def create_appliance(versa, **kwargs):
    if is_use_existing():
        return
    device = _get_node_configuration('device', kwargs)
    management_ip = get_mandatory(device, 'mgmt-ip')
    versa_plugin.appliance.wait_for_device(versa, management_ip, ctx)
    task = versa_plugin.appliance.add_appliance(versa, device)
    versa_plugin.tasks.wait_for_task(versa, task, ctx)


@operation
@with_versa
def delete_appliance(versa, **kwargs):
    if is_use_existing():
        return
    device = _get_node_configuration('device', kwargs)
    name = get_mandatory(device, 'name')
    task = versa_plugin.appliance.delete_appliance(versa, name)
    versa_plugin.tasks.wait_for_task(versa, task, ctx)


@operation
@with_versa
def associate_organization(versa, **kwargs):
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
        versa_plugin.networking.create_interface(versa, appliance,
                                                 interface)
    task = versa_plugin.appliance.associate_organization(versa,
                                                         organization)
    versa_plugin.tasks.wait_for_task(versa, task, ctx)


@operation
@with_versa
def create_router(versa, **kwargs):
    if is_use_existing():
        return
    router = _get_node_configuration('router', kwargs)
    if versa_plugin.networking.is_router_exists(versa, router):
        raise cfy_exc.NonRecoverableError("Router exists")
    versa_plugin.networking.create_virtual_router(versa, router)


@operation
@with_versa
def delete_router(versa, **kwargs):
    if is_use_existing():
        return
    router = _get_node_configuration('router', kwargs)
    router_name = router['name']
    if versa_plugin.networking.is_router_exists(versa, router_name):
        versa_plugin.networking.delete_virtual_router(versa, router_name)


@operation
@with_versa
def insert_to_router(versa, **kwargs):
    if is_use_existing():
        return
    router = _get_node_configuration('router', kwargs)
    router_name = router['name']
    networks = router('networks', [])
    for net_name in networks:
        versa_plugin.networking.add_network_to_router(
            versa, router_name, net_name)


@operation
@with_versa
def delete_from_router(versa, **kwargs):
    if is_use_existing():
        return
    router = _get_node_configuration('router', kwargs)
    router_name = router['name']
    networks = router('networks', [])
    for net_name in networks:
        versa_plugin.networking.delete_network_from_router(
            versa, router_name, net_name)


@operation
@with_versa
def create_cgnat_pool(versa, **kwargs):
    if is_use_existing():
        return
    pool = _get_node_configuration('pool', kwargs)
    versa_plugin.cgnat.create_pool(versa, pool)


@operation
@with_versa
def delete_cgnat_pool(versa, **kwargs):
    if is_use_existing():
        return
    pool = _get_node_configuration('pool', kwargs)
    pool_name = pool['name']
    versa_plugin.cgnat.delete_pool(versa, pool_name)


@operation
@with_versa
def create_cgnat_rule(versa, **kwargs):
    if is_use_existing():
        return
    rule = _get_node_configuration('rule', kwargs)
    versa_plugin.cgnat.create_rule(versa, rule)


@operation
@with_versa
def delete_cgnat_rule(versa, **kwargs):
    if is_use_existing():
        return
    rule = _get_node_configuration('rule', kwargs)
    rule_name = rule['name']
    versa_plugin.cgnat.delete_rule(versa, rule_name)


@operation
@with_versa
def create_zone(versa, **kwargs):
    if is_use_existing():
        return
    zone = _get_node_configuration('zone', kwargs)
    zone_name = zone['name']
    zone_exsists = versa_plugin.networking.get_zone(versa, zone_name)
    if zone_exsists:
        raise cfy_exc.NonRecoverableError(
            "Zone '{}' exsists".format(zone_name))
    versa_plugin.networking.create_zone(versa, zone)


@operation
@with_versa
def delete_zone(versa, **kwargs):
    if is_use_existing():
        return
    zone = _get_node_configuration('zone', kwargs)
    zone_name = zone['name']
    versa_plugin.networking.delete_zone(versa, zone_name)


@operation
@with_versa
def insert_to_zone(versa, **kwargs):
    if is_use_existing():
        return
    zone = _get_node_configuration('zone', kwargs)
    zone_name = zone['name']
    zone_exsists = versa_plugin.networking.get_zone(versa,
                                                    zone_name)
    if zone_exsists:
        ctx.instance.runtime_properties[zone_name] = deepcopy(zone_exsists)
        new_zone = reqursive_update(zone_exsists, zone)
        versa_plugin.networking.update_zone(versa, new_zone)


@operation
@with_versa
def delete_from_zone(versa, **kwargs):
    if is_use_existing():
        return
    zone = _get_node_configuration('zone', kwargs)
    zone_name = zone['name']
    old_zone = ctx.instance.runtime_properties.get(zone_name, None)
    if old_zone:
        versa_plugin.networking.update_zone(versa, old_zone)


@operation
@with_versa
def create_firewall_policy(versa, **kwargs):
    if is_use_existing():
        return
    policy = _get_node_configuration('policy', kwargs)
    versa_plugin.firewall.add_policy(versa, policy)


@operation
@with_versa
def delete_firewall_policy(versa, **kwargs):
    if is_use_existing():
        return
    policy = _get_node_configuration('policy', kwargs)
    versa_plugin.firewall.delete_policy(versa, policy['name'])


@operation
@with_versa
def create_firewall_rules(versa, **kwargs):
    if is_use_existing():
        return
    policy_name = get_mandatory['policy_name']
    rules = _get_node_configuration('rules', kwargs)
    ctx.instance.runtime_properties['rules'] = {}
    ctx.instance.runtime_properties['appliance'] = versa.appliance
    ctx.instance.runtime_properties['org'] = versa.organization
    ctx.instance.runtime_properties['policy'] = policy_name
    for rule in rules:
        name = rule['name']
        ctx.instance.runtime_properties['rules'][name] = rule
        versa_plugin.firewall.add_rule(versa, policy_name, rule)


@operation
@with_versa
def delete_firewall_rules(versa, **kwargs):
    if is_use_existing():
        return
    policy_name = get_mandatory['policy_name']
    rules = _get_node_configuration('rules', kwargs)
    for rule in rules:
        versa_plugin.firewall.delete_rule(versa, policy_name, rule['name'])


@operation
@with_versa
def update_firewall_rule(versa, **kwargs):
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
    policy_name = ctx.instance.runtime_properties['policy']
    versa_plugin.firewall.update_rule(versa, policy_name, rule)


@operation
@with_versa
def get_firewall_rule(versa, **kwargs):
    name = kwargs.get('name')
    if not name:
        ctx.logger.info("Key 'name' is absent.")
        return
    policy_name = ctx.instance.runtime_properties['policy']
    rule = versa_plugin.firewall.get_rule(versa, policy_name, name)
    ctx.logger.info("Rule '{} is: {}".format(name, rule))


@operation
@with_versa
def create_url_filters(versa, **kwargs):
    filters = _get_node_configuration('filters', kwargs)
    for url_filter in filters:
        ctx.logger.info("Filter: {}".format(url_filter))
        versa_plugin.firewall.add_url_filter(versa, url_filter)


@operation
@with_versa
def delete_url_filters(versa, **kwargs):
    filters = _get_node_configuration('filters', kwargs)
    for url_filter in filters:
        ctx.logger.info("Filter: {}".format(url_filter))
        versa_plugin.firewall.delete_url_filter(versa, url_filter)


@operation
@with_versa
def create_dhcp_profile(versa, **kwargs):
    if is_use_existing():
        return
    profile = _get_node_configuration('profile', kwargs)
    profile_name = profile['name']
    if versa_plugin.limits.is_dhcp_profile_exists(versa,
                                                  profile_name):
        raise cfy_exc.NonRecoverableError("DHCP profile exists")
    versa_plugin.limits.create_dhcp_profile(versa, profile)


@operation
@with_versa
def delete_dhcp_profile(versa, **kwargs):
    if is_use_existing():
        return
    profile = _get_node_configuration('profile', kwargs)
    profile_name = profile['name']
    if versa_plugin.limits.is_dhcp_profile_exists(versa,
                                                  profile_name):
        versa_plugin.limits.delete_dhcp_profile(versa,
                                                profile_name)


@operation
@with_versa
def create_dhcp_options_profile(versa, **kwargs):
    if is_use_existing():
        return
    options_profile = _get_node_configuration('options_profile', kwargs)
    options_name = options_profile['name']
    if versa_plugin.dhcp.is_dhcp_profile_exists(versa, options_name):
        raise cfy_exc.NonRecoverableError("DHCP options profile exists")
    versa_plugin.dhcp.create_options_profile(versa, options_profile)


@operation
@with_versa
def delete_dhcp_options_profile(versa, **kwargs):
    if is_use_existing():
        return
    options_profile = _get_node_configuration('options_profile', kwargs)
    options_name = options_profile['name']
    if versa_plugin.dhcp.is_dhcp_profile_exists(versa, options_name):
        versa_plugin.dhcp.delete_options_profile(versa, options_name)


@operation
@with_versa
def create_dhcp_lease_profile(versa, **kwargs):
    if is_use_existing():
        return
    lease_profile = _get_node_configuration('lease_profile', kwargs)
    lease_name = lease_profile['lease_profile']
    if versa_plugin.dhcp.is_lease_profile_exsists(versa, lease_name):
        raise cfy_exc.NonRecoverableError("DHCP lease profile exists")
    versa_plugin.dhcp.create_lease_profile(versa, lease_profile)


@operation
@with_versa
def delete_dhcp_lease_profile(versa, **kwargs):
    if is_use_existing():
        return
    lease_profile = _get_node_configuration('lease_profile', kwargs)
    lease_name = lease_profile['lease_profile']
    if versa_plugin.dhcp.is_lease_profile_exsists(versa, lease_name):
        versa_plugin.dhcp.delete_lease_profile(versa, lease_name)


@operation
@with_versa
def create_dhcp_global_configuration(versa, **kwargs):
    if is_use_existing():
        return

    server_and_relay = _get_node_configuration('server_and_relay', kwargs)
    versa_plugin.dhcp.update_global_configuration(versa, server_and_relay)


@operation
@with_versa
def delete_dhcp_global_configuration(versa, **kwargs):
    if is_use_existing():
        return
    server_and_relay = []
    versa_plugin.dhcp.update_global_configuration(versa, server_and_relay)


@operation
@with_versa
def create_dhcp_pool(versa, **kwargs):
    if is_use_existing():
        return
    pool = _get_node_configuration('pool', kwargs)
    pool_name = pool['name']
    if versa_plugin.dhcp.is_pool_exists(versa, pool_name):
        raise cfy_exc.NonRecoverableError("DHCP pool exists")
    versa_plugin.dhcp.create_pool(versa, pool)


@operation
@with_versa
def delete_dhcp_pool(versa, **kwargs):
    if is_use_existing():
        return
    pool = _get_node_configuration('pool', kwargs)
    pool_name = pool['name']
    if versa_plugin.dhcp.is_pool_exists(versa, pool_name):
        versa_plugin.dhcp.delete_pool(versa, pool_name)


@operation
@with_versa
def create_dhcp_server(versa, **kwargs):
    if is_use_existing():
        return
    server = _get_node_configuration('server', kwargs)
    server_name = server['name']
    if versa_plugin.dhcp.is_server_exists(versa, server_name):
        raise cfy_exc.NonRecoverableError("DHCP server exists")
    versa_plugin.dhcp.create_server(versa, server)


@operation
@with_versa
def delete_dhcp_server(versa, **kwargs):
    if is_use_existing():
        return
    server = _get_node_configuration('server', kwargs)
    server_name = server['name']
    if versa_plugin.dhcp.is_server_exists(versa, server_name):
        versa_plugin.dhcp.delete_server(versa, server_name)


@operation
@with_versa
def create_interface(versa, **kwargs):
    if is_use_existing():
        return
    interface = _get_node_configuration('interface', kwargs)
    name = interface['name']
    if versa_plugin.networking.is_interface_exists(versa, name):
        raise cfy_exc.NonRecoverableError("Interface exists")
    versa_plugin.networking.create_interface(versa, interface)


@operation
@with_versa
def delete_interface(versa, **kwargs):
    if is_use_existing():
        return
    interface = _get_node_configuration('interface', kwargs)
    name = interface['name']
    if versa_plugin.networking.is_interface_exists(versa, name):
        versa_plugin.networking.delete_interface(versa, name)


@operation
@with_versa
def create_network(versa, **kwargs):
    if is_use_existing():
        return
    network = _get_node_configuration('network', kwargs)
    name = network['name']
    if versa_plugin.networking.is_network_exists(versa, name):
        raise cfy_exc.NonRecoverableError("Network exists")
    versa_plugin.networking.create_network(versa, network)


@operation
@with_versa
def delete_network(versa, **kwargs):
    if is_use_existing():
        return
    network = _get_node_configuration('network', kwargs)
    name = network['name']
    if versa_plugin.networking.is_network_exists(versa,
                                                 name):
        versa_plugin.networking.delete_network(versa, name)


@operation
@with_versa
def insert_to_limits(versa, **kwargs):
    if is_use_existing():
        return
    dhcp_profile = ctx.node.properties.get('dhcp_profile')
    routes = ctx.node.properties.get('routes', [])
    networks = ctx.node.properties.get('networks', [])
    interfaces = ctx.node.properties.get('interfaces', [])
    provider_orgs = ctx.node.properties.get('provider_orgs', [])
    for name in routes:
        versa_plugin.limits.add_routing_instance(versa, name)
    for name in networks:
        versa_plugin.limits.add_traffic_identification_networks(
            versa, name, 'using-networks')
    for name in interfaces:
        versa_plugin.limits.add_traffic_identification_networks(
            versa, name, 'using')
    for name in provider_orgs:
        versa_plugin.limits.add_provider_organization(versa, name)
    if dhcp_profile:
        versa_plugin.limits.insert_dhcp_profile_to_limits(versa,
                                                          dhcp_profile)


@operation
@with_versa
def delete_from_limits(versa, **kwargs):
    if is_use_existing():
        return
    dhcp_profile = ctx.node.properties.get('dhcp_profile')
    routes = ctx.node.properties.get('routes', [])
    networks = ctx.node.properties.get('networks', [])
    interfaces = ctx.node.properties.get('interfaces', [])
    provider_orgs = ctx.node.properties.get('provider_orgs', [])
    for name in routes:
        versa_plugin.limits.delete_routing_instance(versa, name)
    for name in networks:
        versa_plugin.limits.delete_traffic_identification_networks(
            versa, name, 'using-networks')
    for name in interfaces:
        versa_plugin.limits.delete_traffic_identification_networks(
            versa, name, 'using')
    for name in provider_orgs:
        versa_plugin.limits.delete_provider_organization(versa, name)
    if dhcp_profile:
        versa_plugin.limits.delete_dhcp_profile_from_limits(versa,
                                                            dhcp_profile)


@operation
@with_versa
def create_vpn_profile(versa, **kwargs):
    if is_use_existing():
        return
    profile = _get_node_configuration('profile', kwargs)
    name = profile['name']
    if versa_plugin.vpn.is_profile_exists(versa, name):
        raise cfy_exc.NonRecoverableError("VPN profile exists")
    versa_plugin.vpn.create_profile(versa, profile)


@operation
@with_versa
def delete_vpn_profile(versa, **kwargs):
    if is_use_existing():
        return
    profile = _get_node_configuration('profile', kwargs)
    name = profile['name']
    if versa_plugin.vpn.is_profile_exists(versa,
                                          name):
        versa_plugin.vpn.delete_profile(versa, name)
