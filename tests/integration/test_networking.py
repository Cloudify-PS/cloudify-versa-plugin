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
import get_configuration as get_conf
requests.packages.urllib3.disable_warnings()

interface = """
    use_existing: false
    appliance_name: $appliance_name
    interface:
        name: $name
        enable: true
        promiscuous: false
    """

interface_with_address = """
    use_existing: false
    appliance_name: $appliance_name
    interface:
      name: $name
      enable: true
      promiscuous: false
      unit:
        - name: 0
          family:
              inet:
                address:
                  addr: 14.14.0.2/24
    """

tvi_interface_with_address = """
    use_existing: false
    appliance_name: $appliance_name
    interface:
      name: $name
      enable: true
      mode: ipsec
      mtu: 1400
      type: ipsec
      unit:
        - name: 0
          enable: true
          family:
              inet:
                address:
                  addr: 14.14.0.2/24
    """

network = """
    use_existing: false
    appliance_name: $appliance_name
    network:
      name: $name
      interfaces:
        - $interface
    """

router = """
    use_existing: false
    appliance_name: $appliance_name
    router:
        name: $name
        instance-type: virtual-router
        networks:
          - $network
        routing-options:
          static:
            route:
              rti-static-route-list:
                - ip-prefix: 1.2.3.0/24
                  next-hop: 5.6.7.8
                  preference: 1
                  tag: 0
                  interface: none
    """

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
    def add_interface(self, name):
        """ Add interface """
        self.assertFalse(get_conf.interface(self.appliance, name))
        versa_plugin.operations.create_interface()
        self.assertTrue(get_conf.interface(self.appliance, name))

    def delete_interface(self, name):
        """ Delete interface """
        self.assertTrue(get_conf.interface(self.appliance, name))
        versa_plugin.operations.delete_interface()
        self.assertFalse(get_conf.interface(self.appliance, name))

    def add_network(self, name, **kwargs):
        """ Add network """
        self.assertFalse(get_conf.network(self.appliance, name))
        versa_plugin.operations.create_network()
        self.assertTrue(get_conf.network(self.appliance, name))

    def delete_network(self, name, **kwargs):
        """ Delete network """
        self.assertTrue(get_conf.network(self.appliance, name))
        versa_plugin.operations.delete_network()
        self.assertFalse(get_conf.network(self.appliance, name))

    def add_router(self, name, **kwargs):
        """ Add router """
        self.assertFalse(get_conf.router(self.appliance, name))
        versa_plugin.operations.create_router()
        self.assertTrue(get_conf.router(self.appliance, name))

    def delete_router(self, name, **kwargs):
        """ Delete router """
        self.assertTrue(get_conf.router(self.appliance, name))
        versa_plugin.operations.delete_router()
        self.assertFalse(get_conf.router(self.appliance, name))

    @unittest.skip("")
    def test_interface_without_address(self):
        name = 'vni-0/1'
        self.add_to_sequence(self.add_interface,
                             self.delete_interface,
                             interface,
                             name=name)
        self.run_sequence()

    @unittest.skip("")
    def test_interface_with_address(self):
        name = 'vni-0/9'
        self.add_to_sequence(self.add_interface,
                             self.delete_interface,
                             interface_with_address,
                             name=name)
        self.run_sequence()

    @unittest.skip("")
    def test_tvi_interface_with_address(self):
        name = 'tvi-0/9'
        self.add_to_sequence(self.add_interface,
                             self.delete_interface,
                             tvi_interface_with_address,
                             name=name)
        self.run_sequence()

    @unittest.skip("")
    def test_network(self):
        interface = 'vni-0/9'
        unit = '.0'
        name = self.gen_name('network')
        self.add_to_sequence(self.add_interface,
                             self.delete_interface,
                             interface_with_address,
                             name=interface)
        self.add_to_sequence(self.add_network,
                             self.delete_network,
                             network,
                             name=name,
                             interface=interface+unit)
        self.run_sequence()

    # @unittest.skip("")
    def test_router(self):
        interface = 'vni-0/9'
        unit = '.0'
        network_name = self.gen_name('network')
        name = self.gen_name('router')
        self.add_to_sequence(self.add_interface,
                             self.delete_interface,
                             interface_with_address,
                             name=interface)
        self.add_to_sequence(self.add_network,
                             self.delete_network,
                             network,
                             name=network_name,
                             interface=interface+unit)
        self.add_to_sequence(self.add_router,
                             self.delete_router,
                             router,
                             name=name,
                             network=network_name)
        self.run_sequence()

    @unittest.skip("")
    def test_zone(self):
        self.update_node_properties(zone,
                                    "appliance_name org_name")
        versa_plugin.operations.create_zone()
        versa_plugin.operations.delete_zone()

    @unittest.skip("")
    def test_update_zone(self):
        self.update_node_properties(zone_update,
                                    "appliance_name org_name")
        versa_plugin.operations.create_zone()
        versa_plugin.operations.delete_zone()

    @unittest.skip("")
    def test_limits(self):
        self.update_node_properties(limits,
                                    "appliance_name org_name")
        versa_plugin.operations.insert_to_limits()
