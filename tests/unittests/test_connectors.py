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

import mock
import unittest

import versa_plugin.connectors
from versa_plugin.connectors import Network


class ConnectorsMockTestCase(unittest.TestCase):

    def test_add_resource_pool(self):
        client = mock.MagicMock()
        client.post = mock.MagicMock()
        sample = '{"instance": {"name": "name", "ip-address": "address"}}'
        versa_plugin.connectors.add_resource_pool(client, "name", "address")
        self.assertEqual(client.post.call_args[0][1], sample)

    def test_delete_resource_pool(self):
        client = mock.MagicMock()
        versa_plugin.connectors.delete_resource_pool(client, "name")

    def test_add_organisation(self):
        fake_uuid = mock.MagicMock()
        fake_uuid.uuid4 = mock.MagicMock(return_value="1234")
        client = mock.MagicMock()
        client.post = mock.MagicMock()
        networks = [Network("name", "subnet", "mask")]
        resource = "Resource"
        with mock.patch('versa_plugin.connectors.uuid', fake_uuid):
            versa_plugin.connectors.add_organization(client, "org", networks,
                                                     resource)
        sample = """{"organization": {"resource-pool": {"instances":\
 "Resource"}, "description": "Created by cloudify", "uuid": "1234",\
 "org-networks": {"org-network": [{"ipaddress-allocation-mode": "manual",\
 "subnet": "subnet", "mask": "mask", "uuid": "1234", "name": "name"}]},\
 "name": "org"}}"""
        self.assertEqual(client.post.call_args[0][1], sample)
