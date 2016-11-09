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
import versa_plugin.firewall
import configuration
requests.packages.urllib3.disable_warnings()


class FirewallTestCase(unittest.TestCase):
    def setUp(self):
        self.config = configuration.data

    def test_add_url_filter(self):
        with VersaClient(self.config, '/tmp/versakey') as client:
            app = 'vcpe1tdcappliance'
            org = 'vcpe1_hq_org'
            name = 'youtube'
            patterns = ['youtube-pat']
            strings = ['youtube-str']
            action = 'block'
            print versa_plugin.firewall.add_url_filer(client, app, org,
                                                      name,
                                                      action, patterns, strings)
