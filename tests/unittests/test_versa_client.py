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
        self.client = VersaClient(configuration, '/tmp/testkey')

    def test_check_response(self):
        response = mock.MagicMock()

        response.status_code = 404
        accept = 'json'
        with self.assertRaises(cfy_exc.HttpException):
            _check_response(response, 200, accept)

        response.status_code = 200
        response.content = '{}'

        result = _check_response(response, 200, accept)
        self.assertIsInstance(result, dict)

        response.content = None
        result = _check_response(response, 200, accept)
        self.assertIsNone(result)

    def test_get_token(self):
        good_result = mock.MagicMock()
        good_result.content = '{"access_token": "token"}'
        with mock.patch('versa_plugin.versaclient.requests.post',
                        mock.MagicMock(return_value=good_result)),\
            mock.patch('versa_plugin.versaclient.VersaClient.'
                       'read_tokens_form_file',
                       mock.MagicMock(return_value=False)),\
            mock.patch('versa_plugin.versaclient.VersaClient.'
                       'save_token_to_file',
                       mock.MagicMock(return_value=None)):
            self.client.get_token()
            self.assertTrue(self.client.access_token)

        bad_result = mock.MagicMock()
        bad_result.content = ''
        with mock.patch('versa_plugin.versaclient.requests.post',
                        mock.MagicMock(return_value=bad_result)),\
            mock.patch('versa_plugin.versaclient.VersaClient.'
                       'read_tokens_form_file',
                       mock.MagicMock(return_value=False)),\
            mock.patch('versa_plugin.versaclient.VersaClient.'
                       'save_token_to_file',
                       mock.MagicMock(return_value=None)):
            with self.assertRaises(cfy_exc.NonRecoverableError):
                self.client.get_token()

        bad_result.content = None
        with mock.patch('versa_plugin.versaclient.requests.post',
                        mock.MagicMock(return_value=bad_result)),\
            mock.patch('versa_plugin.versaclient.VersaClient.'
                       'read_tokens_form_file',
                       mock.MagicMock(return_value=False)),\
            mock.patch('versa_plugin.versaclient.VersaClient.'
                       'save_token_to_file',
                       mock.MagicMock(return_value=None)):
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
        with mock.patch('versa_plugin.versaclient.requests', mock.MagicMock()) as req,\
             mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()),\
             mock.patch('versa_plugin.versaclient.ctx',  mock.MagicMock()):
            req.delete.__name__ = 'delete'
            self.client.delete('/path')

    def test_request(self):
        request_type = mock.MagicMock()
        with mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
            self.client._request(request_type, '/path', 'data', 'json', 200,
                                 'json')

        request_type = mock.MagicMock(
            side_effect=cfy_exc.HttpException('url', '404', 'Error'))
        with mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
            with self.assertRaises(cfy_exc.HttpException):
                self.client._request(request_type, '/path', 'data', 'json',
                                     200, 'json')

    def test_get_headers(self):
        accept = 'json'
        headers = self.client._get_headers('json', accept)
        self.assertEqual('application/json', headers['Content-type'])

        headers = self.client._get_headers('xml', accept)
        self.assertEqual('application/xml', headers['Content-type'])
        self.assertEqual('application/json', headers['Accept'])

        headers = self.client._get_headers(None, accept)
        self.assertNotIn('Content-type', headers)

        with self.assertRaises(cfy_exc.NonRecoverableError):
            self.client._get_headers('bad', accept)

        headers = self.client._get_headers('json', accept)
        self.assertNotIn("Authorization", headers)

        self.client.access_token = "Token"
        headers = self.client._get_headers('json', accept)
        self.assertIn("Authorization", headers)
