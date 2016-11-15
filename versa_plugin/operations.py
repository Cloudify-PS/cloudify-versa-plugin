from cloudify import ctx
from cloudify import exceptions as cfy_exc
from cloudify.decorators import operation
import versa_plugin
from copy import deepcopy

from versa_plugin import with_versa_client
import versa_plugin.tasks
import versa_plugin.networking
import versa_plugin.dhcp
import versa_plugin.firewall
import versa_plugin.cgnat
import versa_plugin.connectors
from versa_plugin.networking import Routing
from versa_plugin.networking import Unit
from versa_plugin.cgnat import AddressRange
from versa_plugin.appliance import ApplianceInterface, NetworkInfo


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


def _get_configuration(key, kwargs):
    value = ctx.node.properties.get(key, {})
    value.update(kwargs.get(key, {}))
    return value

@operation
@with_versa_client
def create_resource_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    instance = _get_configuration('instance', kwargs)
    versa_plugin.connectors.add_resource_pool(versa_client, instance)


@operation
@with_versa_client
def delete_resource_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    instance = _get_configuration('instance', kwargs)
    name = instance['name']
    versa_plugin.connectors.delete_resource_pool(versa_client, name)


@operation
@with_versa_client
def create_cms_local_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_configuration('organization', kwargs)
    versa_plugin.connectors.add_organization(versa_client,
                                             organization)


@operation
@with_versa_client
def delete_cms_local_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_configuration('organization', kwargs)
    cms_org_name = organization['name']
    versa_plugin.connectors.delete_organization(versa_client,
                                                cms_org_name)


@operation
@with_versa_client
def create_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_configuration('organization', kwargs)
    versa_plugin.appliance.add_organization(versa_client,
                                            organization)


@operation
@with_versa_client
def delete_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    organization = _get_configuration('organization', kwargs)
    nms_org_name = organization['name']
    versa_plugin.appliance.delete_organization(versa_client,
                                               nms_org_name)


@operation
@with_versa_client
def create_appliance(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance = _get_configuration('appliance', kwargs)
    name = appliance['appliance_name']
    management_ip = appliance['management_ip']
    config = appliance['appliance_owner']
    nms_org_name = config['nms_org_name']
    cms_org_name = config['cms_org_name']
    networks = config['networks']
    app_networks = [ApplianceInterface(net['name'],
                                       net['ip_address'],
                                       net['interface']) for net in networks]
    versa_plugin.appliance.wait_for_device(versa_client, management_ip)
    task = versa_plugin.appliance.add_appliance(versa_client,
                                                management_ip, name,
                                                nms_org_name, cms_org_name,
                                                app_networks)
    versa_plugin.tasks.wait_for_task(versa_client, task)


@operation
@with_versa_client
def delete_appliance(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance = _get_configuration('appliance', kwargs)
    name = appliance['appliance_name']
    task = versa_plugin.appliance.delete_appliance(versa_client, name)
    versa_plugin.tasks.wait_for_task(versa_client, task)


@operation
@with_versa_client
def associate_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance = ctx.node.properties['appliance_name']
    org = ctx.node.properties['organization']
    nms_org_name = org['nms_org_name']
    networks_inputs = kwargs.get('organization', {}).get('networks')
    nets = networks_inputs if networks_inputs else org['networks']
    net_info = [NetworkInfo(net['name'], net['parent_interface'],
                            net['ip_address'], net['mask'],
                            net['unit']) for net in nets]
    for net in net_info:
        versa_plugin.networking.create_interface(versa_client, appliance,
                                                 net.parent)
    task = versa_plugin.appliance.associate_organization(versa_client,
                                                         appliance,
                                                         nms_org_name,
                                                         net_info)
    versa_plugin.tasks.wait_for_task(versa_client, task)


@operation
@with_versa_client
def create_router(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    router_name = ctx.node.properties['name']
    networks = ctx.node.properties.get('networks', [])
    routings = ctx.node.properties.get('routings', [])
    update = ctx.node.properties['update']
    if update:
        for name in networks:
            versa_plugin.networking.add_network_to_router(
                versa_client, appliance_name, router_name, name)
    else:
        if routings:
            routings = [Routing(r['ip_prefix'], r['next_hop'],
                                r['interface'], r['preference'],
                                r['tag']) for r in routings]
        versa_plugin.networking.create_virtual_router(versa_client,
                                                      appliance_name,
                                                      router_name, networks,
                                                      routings)


@operation
@with_versa_client
def delete_router(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    networks = ctx.node.properties.get('networks', [])
    router_name = ctx.node.properties['name']
    update = ctx.node.properties['update']
    if update:
        for name in networks:
            versa_plugin.networking.delete_network_to_router(
                versa_client, appliance_name, router_name, name)


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
    update = ctx.node.properties['update']
    zone_name = zone['name']
    zone_exsists = versa_plugin.networking.get_zone(versa_client,
                                                    appliance_name,
                                                    org_name,
                                                    zone_name)
    if update:
        if zone_exsists:
            ctx.instance.runtime_properties[zone_name] = deepcopy(zone_exsists)
            new_zone = reqursive_update(zone_exsists, zone)
            versa_plugin.networking.update_zone(versa_client,
                                                appliance_name,
                                                org_name, new_zone)
    else:
        if zone_exsists:
            raise cfy_exc.NonRecoverableError(
                "Zone '{}' exsists".format(zone_name))
        versa_plugin.networking.create_zone(versa_client,
                                            appliance_name,
                                            org_name, zone)


@operation
@with_versa_client
def delete_zone(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    zone = ctx.node.properties['zone']
    update = ctx.node.properties['update']
    zone_name = zone['name']
    if update:
        old_zone = ctx.instance.runtime_properties.get(zone_name, None)
        if old_zone:
            versa_plugin.networking.update_zone(versa_client,
                                                appliance_name,
                                                org_name, old_zone)
    else:
        versa_plugin.networking.delete_zone(versa_client,
                                            appliance_name,
                                            org_name, zone_name)


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
def create_firewall_rules(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    policy_name = ctx.node.properties['policy_name']
    rules = ctx.node.properties['rules']
    ctx.instance.runtime_properties['rules'] = {}
    ctx.instance.runtime_properties['appliance'] = appliance_name
    ctx.instance.runtime_properties['org'] = org_name
    ctx.instance.runtime_properties['policy'] = policy_name
    for rule in rules:
        name = rule['name']
        ctx.instance.runtime_properties['rules'][name] = rule
        versa_plugin.firewall.add_rule(versa_client, appliance_name,
                                       org_name, policy_name, rule)


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
def delete_firewall_rules(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    policy_name = ctx.node.properties['policy_name']
    rules = ctx.node.properties['rules']
    for rule in rules:
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
    versa_plugin.networking.create_dhcp_profile(versa_client, appliance_name,
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
    versa_plugin.dhcp.delete_server(versa_client, appliance_name, org_name,
                                    server_name)


@operation
@with_versa_client
def create_interface(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    name = ctx.node.properties['name']
    units = ctx.node.properties.get('units')
    if units:
        unitlist = [Unit(unit['name'], unit['address'], unit['mask'])
                    for unit in units]
    else:
        unitlist = []
    versa_plugin.networking.create_interface(versa_client, appliance_name,
                                             name, unitlist)


@operation
@with_versa_client
def delete_interface(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    name = ctx.node.properties['name']
    versa_plugin.networking.delete_interface(versa_client, appliance_name,
                                             name)


@operation
@with_versa_client
def create_network(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    name = ctx.node.properties['name']
    interface = ctx.node.properties['interface']
    unit = ctx.node.properties['unit']
    full_interface = "{}.{}".format(interface, unit)
    versa_plugin.networking.create_network(versa_client, appliance_name,
                                           name, full_interface)


@operation
@with_versa_client
def delete_network(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    name = ctx.node.properties['name']
    versa_plugin.networking.delete_network(versa_client, appliance_name, name)


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
    provider_orgs = ctx.node.properties.get('provider_orgs', [])
    if dhcp_profile:
        versa_plugin.networking.update_dhcp_profile(versa_client,
                                                    appliance_name,
                                                    org_name, dhcp_profile)
    for name in routes:
        versa_plugin.networking.add_routing_instance(versa_client,
                                                     appliance_name,
                                                     org_name, name)
    for name in networks:
        versa_plugin.networking.add_traffic_identification_networks(
            versa_client, appliance_name, org_name, name)
    for name in provider_orgs:
        versa_plugin.networking.add_provider_organization(versa_client,
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
    provider_orgs = ctx.node.properties.get('provider_orgs', [])
    if dhcp_profile:
        versa_plugin.networking.update_dhcp_profile(versa_client,
                                                    appliance_name,
                                                    org_name, dhcp_profile)
    for name in routes:
        versa_plugin.networking.delete_routing_instance(versa_client,
                                                        appliance_name,
                                                        org_name, name)
    for name in networks:
        versa_plugin.networking.delete_traffic_identification_networks(
            versa_client, appliance_name, org_name, name)
    for name in provider_orgs:
        versa_plugin.networking.delete_provider_organization(versa_client,
                                                             appliance_name,
                                                             org_name,
                                                             name)
