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
requests.packages.urllib3.disable_warnings()

zone = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    update: false
    zone:
        name: test_zone_name
        description: zone description
    """

zone_update = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    update: true
    zone:
        name: untrust
        routing-instance:
            - parent_router
    """

interface = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    name: vni-0/5
    """

interface_with_address = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    name: vni-0/5
    units:
      - name: 0
        address: 14.14.0.2
        mask: 255.255.255.0
    """

network = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    name: test_network
    interface: vni-0/5
    unit: 0
    """

router = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    update: false
    name: test_router
    """

limits = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    dhcp_profile:   tdc_dhcp_profile
    routes:
      - parent_router
      - hq_router
    provider_orgs:
      - vcpe1_parent_org
    """


class NetworkingTestCase(base.BaseTest):
    @unittest.skip("")
    def test_add_zone(self):
        self.update_node_properties(zone,
                                    "appliance_name org_name")
        versa_plugin.operations.create_zone()
        versa_plugin.operations.delete_zone()

    # @unittest.skip("")
    def test_update_zone(self):
        self.update_node_properties(zone_update,
                                    "appliance_name org_name")
        versa_plugin.operations.create_zone()
        versa_plugin.operations.delete_zone()

    @unittest.skip("")
    def test_create_interface_without_address(self):
        self.update_node_properties(interface,
                                    "appliance_name org_name")
        versa_plugin.operations.create_interface()
        versa_plugin.operations.delete_interface()

    @unittest.skip("")
    def test_create_interface_with_address(self):
        self.update_node_properties(interface_with_address,
                                    "appliance_name org_name")
        versa_plugin.operations.create_interface()
        versa_plugin.operations.delete_interface()

    @unittest.skip("")
    def test_create_network(self):
        self.update_node_properties(interface_with_address,
                                    "appliance_name org_name")
        versa_plugin.operations.create_interface()
        self.save_properties()
        self.update_node_properties(network,
                                    "appliance_name org_name")
        versa_plugin.operations.create_network()
        versa_plugin.operations.delete_network()
        self.restore_properties()
        versa_plugin.operations.delete_interface()

    @unittest.skip("")
    def test_create_router(self):
        self.update_node_properties(router,
                                    "appliance_name org_name")
        versa_plugin.operations.create_router()
        versa_plugin.operations.delete_router()

    @unittest.skip("")
    def test_limits(self):
        self.update_node_properties(limits,
                                    "appliance_name org_name")
        versa_plugin.operations.insert_to_limits()
