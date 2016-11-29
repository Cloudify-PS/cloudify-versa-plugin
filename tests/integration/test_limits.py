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
import versa_plugin.operations
import configuration
requests.packages.urllib3.disable_warnings()


dhcp_profile = """
{"name":"ffaadsf","description":"gff","dhcp-policy":{"requests-pps-rate":"56"},
"dhcp-options":{"max-servers":"22","max-clients":"11","max-relays":"33"}}}
"""

class ApplianceTestCase(base.BaseTest):
    def test_dhcp_profile(self):
        pass

    def test_limits(self):
        pass
