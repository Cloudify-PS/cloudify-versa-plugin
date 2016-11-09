from cloudify import ctx
from cloudify.decorators import operation
import versa_plugin

from versa_plugin import with_versa_client
import versa_plugin.tasks
import versa_plugin.networking
import versa_plugin.dhcp
import versa_plugin.firewall
import versa_plugin.cgnat
from versa_plugin.networking import Routing
from versa_plugin.networking import Unit
from versa_plugin.cgnat import AddressRange
from versa_plugin.firewall import Rule
from versa_plugin.connectors import Network
from versa_plugin.appliance import ApplianceInterface, NetworkInfo


def is_use_existing():
    return ctx.node.properties.get('use_existing')


@operation
@with_versa_client
def create_resource_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    if kwargs.get('ip_address'):
        resource_address = kwargs['ip_address']
    else:
        resource_address = ctx.node.properties['ip_address']
    resource = ctx.node.properties['name']
    versa_plugin.connectors.add_resource_pool(versa_client, resource,
                                              resource_address)


@operation
@with_versa_client
def delete_resource_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    resource = ctx.node.properties['name']
    versa_plugin.connectors.delete_resource_pool(versa_client, resource)


@operation
@with_versa_client
def create_cms_local_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    cms_org_name = ctx.node.properties['name']
    resource = ctx.node.properties['resources'][0]
    networks = ctx.node.properties['networks']
    net_list = [Network(net['name'], net['subnet'],
                        net['mask']) for net in networks]
    versa_plugin.connectors.add_organization(versa_client,
                                             cms_org_name,
                                             net_list,
                                             resource)


@operation
@with_versa_client
def delete_cms_local_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    cms_org_name = ctx.node.properties['name']
    versa_plugin.connectors.delete_organization(versa_client,
                                                cms_org_name)


@operation
@with_versa_client
def create_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    nms_org_name = ctx.node.properties['name']
    cms_org_name = ctx.node.properties['cms_org_name']
    parent = ctx.node.properties['parent']
    versa_plugin.appliance.add_organization(versa_client,
                                            nms_org_name,
                                            parent,
                                            cms_org_name)


@operation
@with_versa_client
def delete_organization(versa_client, **kwargs):
    if is_use_existing():
        return
    nms_org_name = ctx.node.properties['name']
    versa_plugin.appliance.delete_organization(versa_client,
                                               nms_org_name)


@operation
@with_versa_client
def create_appliance(versa_client, **kwargs):
    if is_use_existing():
        return
    name = ctx.node.properties['appliance_name']
    if kwargs.get('management_ip'):
        management_ip = kwargs['management_ip']
    else:
        management_ip = ctx.node.properties['management_ip']
    config = ctx.node.properties['appliance_owner']
    nms_org_name = config['nms_org_name']
    cms_org_name = config['cms_org_name']
    networks_inputs = kwargs.get('appliance_owner', {}).get('networks')
    networks = networks_inputs if networks_inputs else config['networks']
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
    name = ctx.node.properties['appliance_name']
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
    parent = org['parent']
    for net in net_info:
        versa_plugin.networking.create_interface(versa_client, appliance,
                                                 net.parent)
    task = versa_plugin.appliance.associate_organization(versa_client,
                                                         appliance,
                                                         nms_org_name,
                                                         net_info)
    versa_plugin.tasks.wait_for_task(versa_client, task)
    versa_plugin.networking.update_provider_organization(versa_client,
                                                         appliance,
                                                         nms_org_name,
                                                         parent)


@operation
@with_versa_client
def create_router(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    router_name = ctx.node.properties['name']
    organization_name = ctx.node.properties['org_name']
    networks = ctx.node.properties['networks']
    routings = []
    if ctx.node.properties.get('routings'):
        routings = [Routing(r['ip_prefix'], r['next_hop'],
                            r['interface'], r['preference'],
                            r['tag']) for r in ctx.node.properties['routings']]
    versa_plugin.networking.create_virtual_router(versa_client, appliance_name,
                                                  router_name, networks,
                                                  routings)
    versa_plugin.networking.update_routing_instance(versa_client,
                                                    appliance_name,
                                                    organization_name,
                                                    router_name)
    parent_router = ctx.node.properties.get('parent_router_name')
    if parent_router:
        versa_plugin.networking.update_routing_instance(versa_client,
                                                        appliance_name,
                                                        organization_name,
                                                        parent_router)


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
def create_firewall(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    policy_name = ctx.node.properties['policy_name']
    rules = [Rule(r['name']) for r in ctx.node.properties['rules']]
    zones = ctx.node.properties.get('zones')
    url_filters = ctx.node.properties.get('url_filtering')
    if zones:
        for zone in zones:
            for zone_name in zone:
                networks = zone[zone_name].get('networks', [])
                routing_instances = zone[zone_name].get('routing_instances', [])
                versa_plugin.networking.update_zones(versa_client,
                                                     appliance_name,
                                                     org_name, zone_name,
                                                     networks,
                                                     routing_instances)
    if policy_name:
        versa_plugin.firewall.add_policy(versa_client, appliance_name,
                                         org_name, policy_name)
        versa_plugin.firewall.add_rule(versa_client, appliance_name,
                                       org_name, policy_name, rules)
    if url_filters:
        for url_filter in url_filters:
            versa_plugin.firewall.add_url_filter(versa_client, appliance_name,
                                                 org_name, url_filter)


@operation
@with_versa_client
def add_url_filters(versa_client, **kwargs):
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    additional_url_filters = kwargs.get('url_filters', {})
    if additional_url_filters:
        for url_filter in additional_url_filters:
            versa_plugin.firewall.add_url_filter(versa_client, appliance_name,
                                                 org_name, url_filter)
        ctx.instance.runtime_properties[additional_url_filters] =\
            additional_url_filters


@operation
@with_versa_client
def create_dhcp_profile(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    profile_name = ctx.node.properties['profile_name']
    versa_plugin.networking.create_dhcp_profile(versa_client, appliance_name,
                                                profile_name)
    orgs = ctx.node.properties['organizations']
    for org_name in orgs:
        versa_plugin.networking.update_dhcp_profile(versa_client,
                                                    appliance_name,
                                                    org_name, profile_name)


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
def create_interface(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    name = ctx.node.properties['name']
    units = ctx.node.properties['units']
    if units:
        unitlist = [Unit(unit['name'], unit['address'], unit['mask'])
                    for unit in units]
    else:
        unitlist = []
    versa_plugin.networking.create_interface(versa_client, appliance_name,
                                             name, unitlist)


@operation
@with_versa_client
def create_network(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    name = ctx.node.properties['name']
    interface = ctx.node.properties['interface']
    unit = ctx.node.properties['unit']
    full_interface = "{}.{}".format(interface, unit)
    versa_plugin.networking.create_network(versa_client, appliance_name,
                                           name, full_interface)
    versa_plugin.networking.update_traffic_identification_networks(
        versa_client, appliance_name, org_name, name)
    zone = ctx.node.properties['zone']
    if zone:
        versa_plugin.networking.add_network_to_zone(
            versa_client, appliance_name, org_name, zone, name)
    router = ctx.node.properties['router']
    if router:
        versa_plugin.networking.add_network_to_router(
            versa_client, appliance_name, router, name)
