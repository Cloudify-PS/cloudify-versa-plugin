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

import mock
import unittest

from versa_plugin.versaclient import VersaClient, _check_response
from cloudify import exceptions as cfy_exc

configuration = {
        "versa_url": "https://185.98.150.104:9183",
        "organization": "org",
        "cms_organization": "cms_org",
        "client_id": "voae_rest",
        "client_secret": "c4a6428db293850f9cd176812cf4dfad",
        "username": "Administrator",
        "password": "versa123",
        "grant_type": "password"
}


class VersaPluginMockTestCase(unittest.TestCase):

    def setUp(self):
        self.client = VersaClient(configuration)

    def test__check_response(self):
        response = mock.MagicMock()

        response.status_code = 404
        with self.assertRaises(cfy_exc.HttpException):
            _check_response(response, 200)

        response.status_code = 200
        response.content = '{}'

        result = _check_response(response, 200)
        self.assertIsInstance(result, dict)

        response.content = None
        result = _check_response(response, 200)
        self.assertIsNone(result)

    def test_get_token(self):
        good_result = {"access_token": 'token', 'refresh_token': 'token'}
        with mock.patch('versa_plugin.VersaClient.post', mock.MagicMock(
                return_value=good_result)):
            self.client.get_token()
            self.assertTrue(self.client.access_token)
            self.assertTrue(self.client.refresh_token)

        with mock.patch('versa_plugin.VersaClient.post', mock.MagicMock(
                return_value={})):
            with self.assertRaises(cfy_exc.NonRecoverableError):
                 self.client.get_token()

        with mock.patch('versa_plugin.VersaClient.post', mock.MagicMock(
                return_value=None)):
            with self.assertRaises(cfy_exc.NonRecoverableError):
                 self.client.get_token()

    def test_get(self):
        with mock.patch('versa_plugin.versaclient.requests', mock.MagicMock(
                return_value={})),\
             mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
                self.client.get('/path', 'data', 'json')

    def test_post(self):
        with mock.patch('versa_plugin.versaclient.requests', mock.MagicMock(
                return_value={})),\
             mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
            self.client.post('/path', 'data', 'json')

    def test_delete(self):
        with mock.patch('versa_plugin.versaclient.requests', mock.MagicMock(
                return_value={})),\
             mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
            self.client.delete('/path')

    def test_request(self):
        request_type = mock.MagicMock()
        with mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
            self.client._request(request_type, '/path', 'data', 'json', 200)

        request_type = mock.MagicMock(
            side_effect = cfy_exc.HttpException('url','404','Error'))
        with mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
            with self.assertRaises(cfy_exc.HttpException):
                self.client._request(request_type, '/path', 'data', 'json', 200)

    def test_get_headers(self):
        headers = self.client._get_headers('json')
        self.assertEqual('application/json', headers['Content-type'])

        headers = self.client._get_headers('xml')
        self.assertEqual('application/xml', headers['Content-type'])

        headers = self.client._get_headers(None)
        self.assertNotIn('Content-type', headers)

        with self.assertRaises(cfy_exc.NonRecoverableError):
            self.client._get_headers('bad')

        headers = self.client._get_headers('json')
        self.assertNotIn("Authorization", headers)

        self.client.access_token = "Token"
        headers = self.client._get_headers('json')
        self.assertIn("Authorization", headers)

