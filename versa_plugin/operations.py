from cloudify import ctx
from cloudify.decorators import operation
import versa_plugin

from versa_plugin.connectors import Network
from versa_plugin.appliance import ApplianceInterface
from versa_plugin import with_versa_client


@operation
@with_versa_client
def create(versa_client, cms_config, nms_config, **kwargs):
    cms_org_name = cms_config['org_name']
    resource = cms_config['resource_name']
    resource_address = cms_config['resource_address']
    nms_org_name = nms_config['org_name']
    name = nms_config['appliance_name']
    left_net = cms_config['left_network']
    right_net = cms_config['right_network']
    networks = [Network(left_net['name'], left_net['address'],
                        left_net['mask']),
                Network(right_net['name'], right_net['address'],
                        right_net['mask'])]
    left_iface = nms_config['left_interface']
    right_iface = nms_config['right_interface']
    app_networks = [ApplianceInterface(left_iface['name'],
                                       left_iface['address'],
                                       left_iface['interface']),
                    ApplianceInterface(right_iface['name'],
                                       right_iface['address'],
                                       right_iface['interface'])]
    versa_plugin.connectors.add_resource_pool(versa_client, resource,
                                              resource_address)
    cmsorg = versa_plugin.connectors.add_organization(versa_client,
                                                      cms_org_name,
                                                      networks,
                                                      resource)
    org = versa_plugin.appliance.add_organization(versa_client,
                                                  nms_org_name,
                                                  cmsorg,
                                                  cms_org_name)
    versa_plugin.appliance.wait_for_device(versa_client, resource_address)
    task = versa_plugin.appliance.add_appliance(versa_client,
                                                resource_address, name,
                                                org, cmsorg,
                                                app_networks)
    versa_plugin.tasks.wait_for_task(versa_client, task)
    appl_uuid = versa_plugin.appliance.get_appliance_uuid(versa_client, name)
    ctx.instance.runtime_properties['appliance'] = {}
    appliance_info = ctx.instance.runtime_properties['appliance']
    appliance_info['appliance_uuid'] = appl_uuid
    appliance_info['organization_uuid'] = org
    appliance_info['connector_uuid'] = cmsorg
    appliance_info['resource_name'] = resource


@operation
@with_versa_client
def configure(versa_client, **kwargs):
    pass


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
