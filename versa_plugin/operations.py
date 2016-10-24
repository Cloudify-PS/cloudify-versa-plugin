from cloudify import ctx
from cloudify.decorators import operation
import versa_plugin

from versa_plugin.connectors import Network
from versa_plugin.appliance import ApplianceInterface, NetworkInfo
from versa_plugin import with_versa_client
import versa_plugin.tasks
import versa_plugin.networking
import versa_plugin.dhcp
import versa_plugin.firewall
import versa_plugin.cgnat
from versa_plugin.networking import Routing
from versa_plugin.cgnat import AddressRange


def is_use_existing():
    return ctx.node.properties.get('use_existing')


@operation
@with_versa_client
def create_resource_pool(versa_client, **kwargs):
    if is_use_existing():
        return
    resource = ctx.node.properties['name']
    resource_address = ctx.node.properties['ip_address']
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
    management_ip = ctx.node.properties['management_ip']
    config = ctx.node.properties['appliance_owner']
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
    net = org['networks'][0]
    net_info = NetworkInfo(net['name'], net['parent_interface'],
                           net['ip_address'], net['mask'],
                           net['unit'])
    parent = org['parent']
    versa_plugin.networking.create_interface(versa_client, appliance,
                                             net['parent_interface'])
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
def create_firewall(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    policy_name = ctx.node.properties['policy_name']
    rule_name = ctx.node.properties['rule_name']
    zones = ctx.node.properties.get('zones')
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
    versa_plugin.firewall.add_policy(versa_client, appliance_name,
                                     org_name, policy_name)
    versa_plugin.firewall.add_rule(versa_client, appliance_name,
                                   org_name, policy_name, rule_name)


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
def create_dhcp(versa_client, **kwargs):
    if is_use_existing():
        return
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    profile_name = ctx.node.properties['profile_name']
    options = ctx.node.properties['options_profile']
    options_name = options['name']
    domain = options['domain']
    servers = options['servers']
    lease_name = ctx.node.properties['lease_profile']
    pool = ctx.node.properties['pool']
    pool_name = pool['name']
    mask = pool['mask']
    range_name = pool['range_name']
    begin_address = pool['begin_address']
    end_address = pool['end_address']
    server = ctx.node.properties['server']
    server_name = server['name']
    networks = server['networks']
    versa_plugin.networking.update_dhcp_profile(versa_client, appliance_name,
                                                org_name, profile_name)
    versa_plugin.dhcp.create_options_profile(versa_client, appliance_name,
                                             org_name, options_name,
                                             domain, servers)
    versa_plugin.dhcp.create_lease_profile(versa_client, appliance_name,
                                           org_name, lease_name)
    versa_plugin.dhcp.create_pool(versa_client, appliance_name, org_name,
                                  pool_name, mask, lease_name, options_name,
                                  range_name, begin_address, end_address)
    versa_plugin.dhcp.update_global_configuration(versa_client, appliance_name,
                                                  org_name, lease_name,
                                                  options_name)
    versa_plugin.dhcp.create_server(versa_client, appliance_name, org_name,
                                    server_name, lease_name, options_name,
                                    networks, pool_name)
