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
import base
import requests
import unittest
import versa_plugin.operations
import get_configuration as get_conf
requests.packages.urllib3.disable_warnings()

organization = """
      organization:
        name: $name
        parent-org: none
        subscription-plan: Default-All-Services-Plan
        cms-orgs:
            name: $cms_name
            cms-connector: local
"""

child_organization = """
      organization:
        name: $name
        parent-org: $parent_name
        subscription-plan: Default-All-Services-Plan
        cms-orgs:
            name: $cms_name
            cms-connector: local
"""

appliance = """
      appliance:
        appliance_name: $app_name
        """

associate = """
      appliance_name: $app_name
      organization:
        nms_org_name: $nms_name
        parent: $parent_name
"""


class ApplianceTestCase(base.BaseTest):
    @unittest.skip("")
    def test_organization(self):
        nms_org_name = self.gen_name("org")
        cms_org_name = "manualtesting"
        self.update_node_properties(organization, "", name=nms_org_name,
                                    cms_name=cms_org_name)
        self.assertFalse(get_conf.nms_organization(nms_org_name))
        versa_plugin.operations.create_organization()
        self.assertTrue(get_conf.nms_organization(nms_org_name))
        versa_plugin.operations.delete_organization()
        self.assertFalse(get_conf.nms_organization(nms_org_name))

    @unittest.skip("")
    def test_appliance(self):
        nms_org_name = self.gen_name("org")
        cms_org_name = 'manualtesting'
        resource_address = "192.168.200.203"
        name = self.gen_name("appliance")
        self.update_node_properties(organization, "", name=nms_org_name,
                                    cms_name=cms_org_name)
        self.assertFalse(get_conf.nms_organization(nms_org_name))
        versa_plugin.operations.create_organization()
        self.assertTrue(get_conf.nms_organization(nms_org_name))
        self.save_properties()
        kwargs = {
                'appliance': {
                    'management_ip': resource_address,
                    'appliance_owner': {
                        'nms_org_name': nms_org_name,
                        'cms_org_name': cms_org_name,
                        'networks': [{
                            'name': 'hq',
                            'ip_address': '10.1.0.11',
                            'interface': 'vni-0/0'}]}}}
        self.update_node_properties(appliance, "", app_name=name)
        self.assertFalse(get_conf.appliance(name))
        versa_plugin.operations.create_appliance(**kwargs)
        self.assertTrue(get_conf.appliance(name))
        versa_plugin.operations.delete_appliance(**kwargs)
        self.assertFalse(get_conf.appliance(name))
        self.restore_properties()
        versa_plugin.operations.delete_organization()
        self.assertFalse(get_conf.nms_organization(nms_org_name))

    # @unittest.skip("")
    def test_associate_organization(self):
        nms_org_name = self.gen_name("org")
        nms_org_name_child = self.gen_name("childorg")
        name = self.gen_name("appliance")
        cms_org_name = 'manualtesting'
        resource_address = "192.168.200.203"
        self.update_node_properties(organization, "", name=nms_org_name,
                                    cms_name=cms_org_name)
        self.assertFalse(get_conf.nms_organization(nms_org_name))
        versa_plugin.operations.create_organization()
        self.assertTrue(get_conf.nms_organization(nms_org_name))
        self.save_properties()
        self.update_node_properties(child_organization, "",
                                    name=nms_org_name_child,
                                    parent_name=nms_org_name,
                                    cms_name=cms_org_name)
        self.assertFalse(get_conf.nms_organization(nms_org_name_child))
        versa_plugin.operations.create_organization()
        self.assertTrue(get_conf.nms_organization(nms_org_name_child))
        self.save_properties()
        kwargs = {
                'appliance': {
                    'management_ip': resource_address,
                    'appliance_owner': {
                        'nms_org_name': nms_org_name,
                        'cms_org_name': cms_org_name,
                        'networks': [{
                            'name': 'hq',
                            'ip_address': '10.1.0.11',
                            'interface': 'vni-0/0'}]}}}
        self.update_node_properties(appliance, "", app_name=name)
        self.assertFalse(get_conf.appliance(name))
        versa_plugin.operations.create_appliance(**kwargs)
        self.assertTrue(get_conf.appliance(name))
        self.save_properties()
        self.update_node_properties(associate, "",
                                    app_name=name,
                                    nms_name=nms_org_name_child,
                                    parent_name=nms_org_name)
        kwargs_associated = {
                'organization': {
                    'networks': [{
                        'name': 'branch',
                        'ip_address': '10.2.0.11',
                        'mask': '255.255.255.0',
                        'parent_interface': 'vni-0/1',
                        'unit': '0'}]}}
        versa_plugin.operations.associate_organization(**kwargs_associated)
        self.restore_properties()
        versa_plugin.operations.delete_appliance(**kwargs)
        self.assertFalse(get_conf.appliance(name))
        self.restore_properties()
        versa_plugin.operations.delete_organization()
        self.assertFalse(get_conf.nms_organization(nms_org_name_child))
        self.restore_properties()
        versa_plugin.operations.delete_organization()
        self.assertFalse(get_conf.nms_organization(nms_org_name))
