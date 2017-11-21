
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
import versa_plugin.workflow
import versa_plugin.tasks
from time import sleep
requests.packages.urllib3.disable_warnings()


class WorkflowTestCase(base.BaseTest):

    def test_create_device(self):
        with VersaClient(self.config, '/tmp/versa.key') as client:
            config = {"name": "CPE2",
                      "location": {
                          "country": "nl",
                          "longitude": "0", "latitude": "0"},
                      "variables": {
                          "{$v_Lan_IPv4__staticaddress}": "192.168.1.1/32",
                          "{$v_mpls_IPv4__staticaddress}":  "192.168.2.2/32",
                          "{$v_mpls-Transport-VR_IPv4__vrHopAddress}": "192.168.3.3"}}
            task = versa_plugin.workflow.create_device(client, config)
            versa_plugin.tasks.wait_for_task(client, task, self.fake_ctx)
            sleep(2)
            task = versa_plugin.workflow.delete_device(client, config)
            versa_plugin.tasks.wait_for_task(client, task, self.fake_ctx)
