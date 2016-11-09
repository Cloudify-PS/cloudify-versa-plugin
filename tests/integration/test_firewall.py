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
requests.packages.urllib3.disable_warnings()


filter = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    filters:
          - name: test_filter
            description: test
            default-action:
                predefined: allow
            cloud-lookup-mode: never
            category-action-map:
                category-action: []
            reputation-action-map:
                reputation-action: []
            blacklist:
                action:
                    predefined: alert
                patterns:
                    - "https://www.youtube.com/*"
            whitelist: {}
            """

policy = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    policy:
        name: test_policy_name
        description: descr
    """

rules = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    policy_name: $firewall_policy
    rules:
        - name: test_rule_name
          match:
            source:
                zone:
                    zone-list:
                        - trust
            destination:
                zone:
                    zone-list:
                        - untrust
          set:
              lef:
                  event: end
                  options:
                      send-pcap-data:
                          enable: False
              action: allow
    """

rules_with_filter = """
    use_existing: false
    appliance_name: $appliance_name
    org_name: $org_name
    policy_name: $firewall_policy
    rules:
        - name: test_rule_name
          match:
            source:
                zone:
                    zone-list:
                        - trust
            destination:
                zone:
                    zone-list:
                        - untrust
          set:
              lef:
                  event: end
                  options:
                      send-pcap-data:
                          enable: False
              action: allow
              security-profile:
                  urlf: test
    """


class FirewallTestCase(base.BaseTest):
    def notest_add_url_filter(self):
        self.update_node_properties(filter,
                                    "appliance_name org_name")
        versa_plugin.operations.create_url_filters()
        versa_plugin.operations.delete_url_filters()

    def notest_add_policy(self):
        self.update_node_properties(policy,
                                    "appliance_name org_name")
        versa_plugin.operations.create_firewall_policy()
        versa_plugin.operations.delete_firewall_policy()

    def notest_add_rule(self):
        self.update_node_properties(rules,
                                    "appliance_name org_name firewall_policy")
        versa_plugin.operations.create_firewall_rules()
        versa_plugin.operations.delete_firewall_rules()

    def notest_add_rule_with_filter(self):
        self.update_node_properties(rules_with_filter,
                                    "appliance_name org_name firewall_policy")
        versa_plugin.operations.create_firewall_rules()
        versa_plugin.operations.delete_firewall_rules()
