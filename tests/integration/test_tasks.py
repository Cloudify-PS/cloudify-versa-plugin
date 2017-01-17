#! Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
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
import versa_plugin.tasks
import configuration
requests.packages.urllib3.disable_warnings()


class TasksTestCase(unittest.TestCase):
    def setUp(self):
        self.config = configuration.data

    def test_get_task_info(self):
        with VersaClient(self.config) as client:
            task = '25'
            print versa_plugin.tasks.get_task_info(client, task)

    def notest_get_all_tasks(self):
        with VersaClient(self.config) as client:
            print versa_plugin.tasks.get_all_tasks(client)
