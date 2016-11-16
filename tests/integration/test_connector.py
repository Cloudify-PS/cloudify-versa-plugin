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

pool = """
    instance:
        name: $pool_name
        ip-address: 1.2.3.4
      """

organization = """
      organization:
        name: $cms_name
        resource-pool:
          instances:
            - $pool_name
        org-networks:
          org-network:
            - name: test_net1
              subnet: 10.1.0.0
              mask: 255.255.255.0
              ipaddress-allocation-mode: manual
            - name: test_net2
              subnet: 10.2.0.0
              mask: 255.255.255.0
              ipaddress-allocation-mode: manual
"""


class ConnectorTestCase(base.BaseTest):
    def add_pool(self, pool_name, **kwargs):
        """ Add pool """
        self.assertFalse(get_conf.pool(pool_name))
        versa_plugin.operations.create_resource_pool()
        self.assertTrue(get_conf.pool(pool_name))

    def delete_pool(self, pool_name, **kwargs):
        """ Delete pool """
        self.assertTrue(get_conf.pool(pool_name))
        versa_plugin.operations.delete_resource_pool()
        self.assertFalse(get_conf.pool(pool_name))

    def add_organization(self, cms_name, **kwargs):
        """ Add organization """
        self.assertFalse(get_conf.cms_organization(cms_name))
        versa_plugin.operations.create_cms_local_organization()
        self.assertTrue(get_conf.cms_organization(cms_name))

    def delete_organization(self, cms_name, **kwargs):
        """ Delete organization """
        self.assertTrue(get_conf.cms_organization(cms_name))
        versa_plugin.operations.delete_cms_local_organization()
        self.assertFalse(get_conf.cms_organization(cms_name))

    # @unittest.skip("")
    def test_resource_pool(self):
        pool_name = self.gen_name('pool')
        self.add_to_sequence(self.add_pool,
                             self.delete_pool,
                             pool,
                             pool_name=pool_name)
        self.run_sequence()

    # @unittest.skip("")
    def test_organization(self):
        pool_name = self.gen_name('pool')
        cms_name = self.gen_name('cms')
        self.add_to_sequence(self.add_pool,
                             self.delete_pool,
                             pool,
                             pool_name=pool_name)
        self.add_to_sequence(self.add_organization,
                             self.delete_organization,
                             organization,
                             cms_name=cms_name,
                             pool_name=pool_name)
        self.run_sequence()
