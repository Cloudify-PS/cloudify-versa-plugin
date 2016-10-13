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
import versa_plugin.networking
import configuration
requests.packages.urllib3.disable_warnings()


class NetworkingTestCase(unittest.TestCase):
    def setUp(self):
        self.config = configuration.data

    def notest_create_dhcp_profile(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            name = 'testdhcpprofile'
            versa_plugin.networking.create_dhcp_profile(client,
                                                        appliance,
                                                        name)

    def notest_delete_dhcp_profile(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            name = 'testdhcpprofile'
            versa_plugin.networking.delete_dhcp_profile(client,
                                                        appliance,
                                                        name)

    def notest_get_organization_limits(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            org = 'mytestorg'
            print versa_plugin.networking.get_organization_limits(client,
                                                                  appliance,
                                                                  org).toxml()

    def notest_update_dhcp_profile(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            org = 'mytestorg'
            profile = 'testdhcpprofile'
            versa_plugin.networking.update_dhcp_profile(client,
                                                        appliance,
                                                        org,
                                                        profile)

    def notest_update_routing_instances(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            org = 'mytestorg'
            instance = 'testrouter'
            versa_plugin.networking.update_routing_instance(client,
                                                            appliance,
                                                            org,
                                                            instance)

    def notest_update_provider_organization(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            org = 'child3'
            provider = 'mytestorg'
            versa_plugin.networking.update_provider_orranization(client,
                                                                 appliance,
                                                                 org,
                                                                 provider)

    def notest_create_virtual_router(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            name = 'testrouter'
            networks = ['versa2']
            routing = [versa_plugin.networking.Routing("1.2.3.0/24",
                                                       "5.6.7.8", "vni-0/0.0",
                                                       None, 1)]
            versa_plugin.networking.create_virtual_router(client,
                                                          appliance,
                                                          name,
                                                          networks,
                                                          routing)

    def notest_delete_virtual_router(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            name = 'testrouter'
            versa_plugin.networking.delete_virtual_router(client,
                                                          appliance,
                                                          name)

    def notest_create_interface(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            name = 'vni-0/3'
            versa_plugin.networking.create_interface(client,
                                                     appliance,
                                                     name)

    def notest_delete_interface(self):
        with VersaClient(self.config) as client:
            appliance = 'testapp'
            name = 'vni-0/3'
            versa_plugin.networking.delete_interface(client,
                                                     appliance,
                                                     name)
