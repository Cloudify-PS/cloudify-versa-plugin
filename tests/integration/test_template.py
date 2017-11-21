
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

import requests
import base
from versa_plugin.versaclient import VersaClient
import versa_plugin.template
requests.packages.urllib3.disable_warnings()


class TemplateTestCase(base.BaseTest):

    def test_create_device(self):
        with VersaClient(self.config, '/tmp/versa.key') as client:
            config = {'template': 'branch',
                      'organization': 'Provider',
                      'interface': 'vni-0/0',
                      'parameters': {
                          "interface": {"name": "vni-0/0",
                                        "shaping-rate":
                                        {"burst-size": "40000",
                                         "rate": "1000"}}}}
            versa_plugin.template.update(client, config)
