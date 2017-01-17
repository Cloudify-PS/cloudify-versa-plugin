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


options_profile = """
            "name": name,
            "domain-name": domain,
            "dns-server": servers,
            "custom-options": {"custom-dhcp-option": []}}}

"""

lease_profile = """

            "name": name,
            "valid-lifetime": "3600",
            "renew-timer": "900",
            "rebind-timer": "2800",
            "log-utilization": False}}
"""


global_configuration = """

            "default-lease-profile": lease_profile,
            "default-options-profile": options_profile,
            "log-unmatched-requests": False}}
"""

pool = """
            "name": pool_name,
            "subnet-mask": mask,
            "lease-profile": lease_profile,
            "options-profile": options_profile,
            "address-pools": {
                "dhcp4-address-pool-info": [{
                    "name": range_name,
                    "pool": {
                        "ipv4-range": {
                            "begin-address": begin_address,
                            "end-address": end_address}}}]},
            "exclude-addresses": {"dhcp4-address-pool-info": []}}}
"""

server = """
            "name": server_name,
            "lease-profile": lease_profile,
            "options-profile": options_profile,
            "dhcp-request-match": {
                "networks": networks},
            "dhcp-service-type": {
                "service-type": {
                    "allocate-address": {
                        "dynamic": pool}}},
            "dhcp-log-settings": {
                "log-new-allocations": True,
                "log-renewals": False}}}
"""

class DHCPTestCase(base.BaseTest):
    def test_create_pool(self):
        nc = configuration.Node
        node_config = """
        use_existing: false
        appliance_name: {}
        org_name: {}
        lease_profile: {}
        options_profile: {}
        name: test_pool_name
        mask: 255.255.255.0
        range_name: test_range_name
        begin_address: 10.100.0.10
        end_address: 10.100.0.29
        """.format(nc.appliance_name,
                   nc.org_name,
                   nc.lease_profile,
                   nc.options_profile)
        self.update_node_properties(node_config)
        versa_plugin.operations.create_dhcp_pool()
        versa_plugin.operations.delete_dhcp_pool()
