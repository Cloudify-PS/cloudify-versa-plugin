from cloudify import ctx
from cloudify.decorators import operation
import versa_plugin

from versa_plugin.connectors import Network
from versa_plugin.appliance import ApplianceInterface, NetworkInfo
from versa_plugin import with_versa_client
import versa_plugin.tasks
import versa_plugin.networking
from versa_plugin.cgnat import AddressRange


@operation
@with_versa_client
def create_resource_pool(versa_client, **kwargs):
    resource = ctx.node.properties['name']
    resource_address = ctx.node.properties['ip_address']
    versa_plugin.connectors.add_resource_pool(versa_client, resource,
                                              resource_address)


@operation
@with_versa_client
def delete_resource_pool(versa_client, **kwargs):
    resource = ctx.node.properties['name']
    versa_plugin.connectors.delete_resource_pool(versa_client, resource)


@operation
@with_versa_client
def create_cms_local_organization(versa_client, **kwargs):
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
    cms_org_name = ctx.node.properties['name']
    versa_plugin.connectors.delete_organization(versa_client,
                                                cms_org_name)


@operation
@with_versa_client
def create_organization(versa_client, **kwargs):
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
    nms_org_name = ctx.node.properties['name']
    versa_plugin.appliance.delete_organization(versa_client,
                                               nms_org_name)


@operation
@with_versa_client
def create_appliance(versa_client, **kwargs):
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
    name = ctx.node.properties['appliance_name']
    task = versa_plugin.appliance.delete_appliance(versa_client, name)
    versa_plugin.tasks.wait_for_task(versa_client, task)


@operation
@with_versa_client
def associate_organization(versa_client, **kwargs):
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
    appliance_name = ctx.node.properties['appliance_name']
    router_name = ctx.node.properties['name']
    organization_name = ctx.node.properties['organization']
    networks = ctx.node.properties['networks']
    versa_plugin.networking.create_virtual_router(versa_client, appliance_name,
                                                  router_name, networks)
    versa_plugin.networking.update_routing_instance(versa_client,
                                                    appliance_name,
                                                    organization_name,
                                                    router_name)


@operation
@with_versa_client
def create_cgnat(versa_client, **kwargs):
    appliance_name = ctx.node.properties['appliance_name']
    org_name = ctx.node.properties['org_name']
    pool = ctx.node.properties['pool']
    pool_name = pool['name']
    addresses = pool['addresses']
    ranges = [AddressRange(r['name'], r['low'], r['hight'])
              for r in pool['ranges']]
    routing_instance = pool['routing_instance']
    provider_org = pool['provider_org']
    versa_plugin.cgnat.create_pool(versa_client, appliance_name,
                                   org_name, pool_name,
                                   addresses, ranges, routing_instance,
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
    pass
