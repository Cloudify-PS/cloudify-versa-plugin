
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

import versa_plugin.appliance


class ApplianceMockTestCase(unittest.TestCase):

    def test_add_organisation(self):
        fake_uuid = mock.MagicMock()
        fake_uuid.uuid4 = mock.MagicMock(return_value="1234")
        client = mock.MagicMock()
        client.post = mock.MagicMock()
        with mock.patch('versa_plugin.appliance.uuid', fake_uuid):
            uuid = versa_plugin.appliance.add_organization(client, "org",
                                                            "uuid",
                                                            "org")
            self.assertEqual(uuid, "org:vcpe:1234")

    def test_delete_organisation(self):
        client = mock.MagicMock()
        versa_plugin.appliance.delete_organization(client, "uuid")
