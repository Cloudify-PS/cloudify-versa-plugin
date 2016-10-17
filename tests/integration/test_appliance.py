# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import requests
from versa_plugin.versaclient import VersaClient
import versa_plugin.appliance
import versa_plugin.tasks
import configuration
from versa_plugin.connectors import Network
from versa_plugin.appliance import ApplianceInterface, NetworkInfo
requests.packages.urllib3.disable_warnings()


class ApplianceTestCase(unittest.TestCase):
    def setUp(self):
        self.config = configuration.data

    def notest_add_delete_organization(self):
        cms_org_name = "Test cms orgname"
        resource = "Test_resource"
        resource_address = "192.168.0.1"
        nms_org_name = "Testname"
        networks = [Network("versa2", "10.3.0.0", "255.255.255.0")]
        with VersaClient(self.config) as client:
            versa_plugin.connectors.add_resource_pool(client, resource,
                                                      resource_address)
            cms_org_uuid = versa_plugin.connectors.add_organization(client,
                                                                    cms_org_name,
                                                                    networks,
                                                                    resource)
            nms_org_uuid = versa_plugin.appliance.add_organization(client,
                                                                   nms_org_name,
                                                                   None,
                                                                   cms_org_uuid,
                                                                   cms_org_name)
            versa_plugin.appliance.delete_organization(client, nms_org_uuid)
            versa_plugin.connectors.delete_organization(client, cms_org_uuid)
            versa_plugin.connectors.delete_resource_pool(client, resource)


    def notest_add_organization(self):
        cms_org_name = "testcmsorg"
        nms_org_name = "Testname"
        with VersaClient(self.config) as client:
            versa_plugin.appliance.add_organization(client,
                                                    nms_org_name,
                                                    None,
                                                    cms_org_name)

    def notest_add_delete_appliance(self):
        cms_org_name = "cmsorgname"
        resource = "Test_resource"
        resource_address = "10.2.0.10"
        nms_org_name = "Testname"
        name = "app"
        networks = [Network("versa2", "10.3.0.0", "255.255.255.0"),
                    Network("versa3", "10.4.0.0", "255.255.255.0")]
        app_networks = [ApplianceInterface("versa2", "10.3.0.9", "vni-0/0"),
                        ApplianceInterface("versa3", "10.4.0.7", "vni-0/1")]
        with VersaClient(self.config) as client:
            versa_plugin.connectors.add_resource_pool(client, resource,
                                                      resource_address)
            cmsorg = versa_plugin.connectors.add_organization(client,
                                                              cms_org_name,
                                                              networks,
                                                              resource)
            org = versa_plugin.appliance.add_organization(client,
                                                          nms_org_name,
                                                          None,
                                                          cmsorg,
                                                          cms_org_name)
            print 'Wait for device'
            versa_plugin.appliance.wait_for_device(client, resource_address)
            task = versa_plugin.appliance.add_appliance(client,
                                                        resource_address, name,
                                                        org, cmsorg,
                                                        app_networks)
            print 'Wait for applaince creation'
            versa_plugin.tasks.wait_for_task(client, task)
            appl_uuid = versa_plugin.appliance.get_appliance_uuid(client, name)
            task_del = versa_plugin.appliance.delete_appliance(client, appl_uuid)
            print 'Wait for applaince deletion'
            versa_plugin.tasks.wait_for_task(client, task_del)
            versa_plugin.appliance.delete_organization(client, org)
            versa_plugin.connectors.delete_organization(client, cmsorg)
            versa_plugin.connectors.delete_resource_pool(client, resource)

    def notest_add_appliance(self):
        cms_org_name = "cmsorg"
        resource_address = "10.2.0.18"
        nms_org_name = "org"
        name = "testapp"
        app_networks = [ApplianceInterface("net1", "10.3.0.15", "vni-0/0")]
        with VersaClient(self.config) as client:
            task = versa_plugin.appliance.add_appliance(client,
                                                        resource_address, name,
                                                        nms_org_name,
                                                        cms_org_name,
                                                        app_networks)
            print 'Wait for applaince creation'
            versa_plugin.tasks.wait_for_task(client, task)

    def notest_delete_appliance(self):
        with VersaClient(self.config) as client:
            versa_plugin.appliance.delete_appliance(client, "")

    def test_get_organizations(self):
        with VersaClient(self.config) as client:
            name = 'org'
            orgs = versa_plugin.appliance.get_organization(client, name)
            print orgs
            # self.assertTrue(orgs)
            #

    def notest_add_appliance_organization(self):
        cms_org_name = "cmsorgname"
        nms_org_name = "TestnamePlug"
        with VersaClient(self.config) as client:
            cmsorg = versa_plugin.connectors.get_organization_uuid(client,
                                                                   cms_org_name)
            versa_plugin.appliance.add_organization(client,
                                                    nms_org_name,
                                                    None,
                                                    cmsorg,
                                                    cms_org_name)

    def notest_associate_organization(self):
        org = 'child2'
        appliance = 'testapp'
        net_info = NetworkInfo("testnet2", "vni-0/1", "10.22.0.100",
                               "255.255.255.0", "4")
        services = ['cgnat', 'nextgen-firewall']
        with VersaClient(self.config) as client:
            task = versa_plugin.appliance.associate_organization(client,
                                                                 appliance,
                                                                 org,
                                                                 net_info,
                                                                 services)
            versa_plugin.tasks.wait_for_task(client, task)

    def notest_disassociate_org(self):
        org = 'child'
        appliance = 'testapp'
        with VersaClient(self.config) as client:
            versa_plugin.appliance.disassociate_org(client, appliance, org)
