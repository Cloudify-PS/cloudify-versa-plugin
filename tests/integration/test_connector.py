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
import versa_plugin.connectors
import configuration
from versa_plugin.connectors import Network
requests.packages.urllib3.disable_warnings()


class ConnectorTestCase(unittest.TestCase):
    def setUp(self):
        self.config = configuration.data

    def test_add_delete_resource_pool(self):
        name = "Test_resource"
        address = "192.168.0.1"
        with VersaClient(self.config, '/tmp/versa.key') as client:
            versa_plugin.connectors.add_resource_pool(client, name, address)
            versa_plugin.connectors.delete_resource_pool(client, name)

    def notest_add_delete_organization(self):
        org_name = "Test orgname"
        resource = "Test_resource"
        address = "192.168.0.1"
        networks = [Network("versa2", "10.3.0.0", "255.255.255.0")]
        with VersaClient(self.config) as client:
            versa_plugin.connectors.add_resource_pool(client, resource, address)
            versa_plugin.connectors.add_organization(client,
                                                     org_name,
                                                     networks,
                                                     resource)
            versa_plugin.connectors.delete_organization(client, org_name)
            versa_plugin.connectors.delete_resource_pool(client, resource)

    def notest_get_organization(self):
        with VersaClient(self.config) as client:
            orgs = versa_plugin.connectors.get_organization(client)
            print orgs
            self.assertTrue(orgs)
