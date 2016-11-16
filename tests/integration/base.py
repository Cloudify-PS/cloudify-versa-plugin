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
import mock
import configuration
import yaml
from string import Template
from copy import deepcopy
from random import choice
from string import ascii_uppercase
from collections import namedtuple


Operation = namedtuple("Operation", "add, delete, template, arguments")


class BaseTest(unittest.TestCase):
    def setUp(self):
        def info(x):
            print x
        self.config = configuration.versa_config
        self.fake_ctx = mock.MagicMock()
        self.fake_ctx._context['storage']._storage_dir = '/tmp'
        self.fake_ctx.logger.info = info
        patcher_ctx1 = mock.patch('versa_plugin.ctx', self.fake_ctx)
        patcher_ctx2 = mock.patch('versa_plugin.operations.ctx', self.fake_ctx)
        patcher_ctx3 = mock.patch('versa_plugin.versaclient.ctx', self.fake_ctx)
        patcher_ctx1.start()
        patcher_ctx2.start()
        patcher_ctx3.start()
        self.prop = []
        self.sequence = []

    def tearDown(self):
        mock.patch.stopall()

    def gen_name(self, prefix):
        suffix = ''.join(choice(ascii_uppercase) for i in range(5))
        return "{}-{}".format(prefix, suffix)

    def yaml_to_dict(self, template, **kwargs):
        return yaml.load(Template(template).substitute(kwargs))

    def set_node_properties(self, template="{}",  **kwargs):
        kwargs.update(configuration.appliance)
        node_config = Template(template).substitute(kwargs)
        self.fake_ctx.node.properties = {'versa_config': self.config}
        self.fake_ctx.node.properties.update(yaml.load(node_config))
        self.fake_ctx.instance.runtime_properties = {}

    def save_properties(self):
        self.prop.append(deepcopy(self.fake_ctx.node.properties))

    def restore_properties(self):
        self.fake_ctx.node.properties.clear()
        self.fake_ctx.node.properties.update(self.prop.pop())

    def set_runtime_properties(self, **kwargs):
        kwargs.update(configuration.appliance)
        self.fake_ctx.instance.runtime_properties.update(kwargs)

    def add_to_sequence(self, add, delete, template, **kwargs):
            self.save_properties()
            template = template if template else '{}'
            self.sequence.append(Operation(add, delete, template, kwargs))

    def run_sequence(self):
        completed = []
        try:
            for item in self.sequence:
                print item.add.__doc__
                self.set_node_properties(item.template, **item.arguments)
                item.add(**item.arguments)
                completed.append(item)
        finally:
            for item in reversed(completed):
                print item.delete.__doc__
                self.set_node_properties(item.template, **item.arguments)
                item.delete(**item.arguments)
