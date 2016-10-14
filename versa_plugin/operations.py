from cloudify import ctx
from cloudify.decorators import operation
import versa_plugin

from versa_plugin.connectors import Network
from versa_plugin.appliance import ApplianceInterface, NetworkInfo
from versa_plugin import with_versa_client


@operation
@with_versa_client
def create_resource_pool(versa_client, **kwargs):
    resource = ctx.node.properties['name']
    resource_address = ctx.node.properties['ip_address']
    versa_plugin.connectors.add_resource_pool(versa_client, resource,
                                              resource_address)


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
def create_appliance(versa_client, **kwargs):
    name = ctx.node.properties['appliance_name']
    management_ip = ctx.node.properties['management_ip']
    config = ctx.node.properties['appliance_owner']
    nms_org_name = config['nms_org_name']
    cms_org_name = config['cms_org_name']
    networks = config['networks']
    app_networks = [ApplianceInterface(net['name'],
                                       net['address'],
                                       net['interface']) for net in networks]
    versa_plugin.appliance.wait_for_device(versa_client, management_ip)
    task = versa_plugin.appliance.add_appliance(versa_client,
                                                management_ip, name,
                                                nms_org_name, cms_org_name,
                                                app_networks)
    versa_plugin.tasks.wait_for_task(versa_client, task)

    associate_organizations(versa_client, ctx.node.properties['organizations'])


def associate_organizations(versa_client, appliance, organizations):
    for org in organizations:
        nms_org_name = org['nms_org_name']
        net = org['networks'][0]
        net_info = NetworkInfo(net['name'], net['parent_interface'],
                               net['ip_address'], net['mask'],
                               net['unit'])
        task = versa_plugin.appliance.associate_organization(versa_client,
                                                             appliance,
                                                             nms_org_name,
                                                             net_info)
        versa_plugin.tasks.wait_for_task(versa_client, task)


@operation
@with_versa_client
def delete(versa_client, **kwargs):
    appliance_info = ctx.instance.runtime_properties['appliance']
    appl_uuid = appliance_info['appliance_uuid']
    org = appliance_info['organization_uuid']
    cmsorg = appliance_info['connector_uuid']
    resource = appliance_info['resource_name']

    task_del = versa_plugin.appliance.delete_appliance(versa_client, appl_uuid)
    versa_plugin.tasks.wait_for_task(versa_client, task_del)
    versa_plugin.appliance.delete_organization(versa_client, org)
    versa_plugin.connectors.delete_organization(versa_client, cmsorg)
    versa_plugin.connectors.delete_resource_pool(versa_client, resource)
