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
import versa_plugin.vpn
import test_networking
import get_configuration as get_conf
requests.packages.urllib3.disable_warnings()


router = """
    use_existing: false
    appliance_name: $appliance_name
    router:
        name: $name
        instance-type: virtual-router
        interfaces:
          - $interface
    """

limits = """
    appliance_name: $appliance_name
    org_name: $org_name
    routes:
        - $router
    interfaces:
        - $interface
"""

vpn_profile = """
    appliance_name: $appliance_name
    org_name: $org_name
    profile:
        name: $name
        vpn-type: site-to-site
        tunnel-initiate: automatic
        hardware-accelerator: any
        tunnel-routing-instance: $router
        tunnel-interface: $interface
        local-auth-info:
            auth-type: psk
            id-string: 1.2.3.4
            id-type: ip
            key: 1
        peer-auth-info:
            auth-type: psk
            id-type: ip
            key: 1
            id-string: 1.2.3.5
        ipsec:
            fragmentation: pre-fragmentation
            force-nat-t: disable
            mode: tunnel
            pfs-group: mod-none
            anti-replay: disable
            transform: esp-aes128-sha1
            keepalive-timeout: 10
        ike:
            version: v2
            group: mod2
            transform: aes128-sha1
            lifetime: 28800
            dpd-timeout: 30
        local:
            inet: 1.2.3.6
        peer:
            inet: 1.2.3.4
        """


class ApplianceTestCase(base.BaseTest):
    def add_vpn_profile(self, name, **kwargs):
        """ Add VPN profile """
        self.assertFalse(get_conf.vpn_profile(self.appliance, self.org, name))
        versa_plugin.operations.create_vpn_profile()
        self.assertTrue(get_conf.vpn_profile(self.appliance, self.org, name))

    def delete_vpn_profile(self, name, **kwargs):
        """ Delete VPN profile """
        self.assertTrue(get_conf.vpn_profile(self.appliance, self.org, name))
        versa_plugin.operations.delete_vpn_profile()
        self.assertFalse(get_conf.vpn_profile(self.appliance, self.org, name))

    def test_vpn_profile(self):
        interface = 'tvi-0/9'
        unit = '.0'
        router_name = self.gen_name('router')
        name = self.gen_name('vpn-profile')
        networking = test_networking.Operations(self.appliance)
        self.add_to_sequence(networking.add_interface,
                             networking.delete_interface,
                             test_networking.tvi_interface_with_address,
                             name=interface)
        self.add_to_sequence(networking.add_router,
                             networking.delete_router,
                             router,
                             name=router_name,
                             interface=interface+unit)
        self.add_to_sequence(networking.add_limits,
                             networking.delete_limits,
                             limits,
                             router=router_name,
                             interface=interface+unit)
        self.add_to_sequence(self.add_vpn_profile,
                             self.delete_vpn_profile,
                             vpn_profile,
                             name=name,
                             router=router_name,
                             interface=interface+unit)
        self.run_sequence()
