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
import requests
from cloudify import exceptions as cfy_exc
import xml

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


class VersaClientMockTestCase(unittest.TestCase):

    # def setUp(self):
        # self.client = VersaClient(configuration, '/tmp/testkey')

    def test_check_response(self):
        response = mock.MagicMock()
        codes = requests.codes
        accept_json = 'json'

        response.status_code = codes.not_found
        with self.assertRaises(cfy_exc.HttpException):
            _check_response(response, codes.no_content, accept_json)

        response.status_code = codes.no_content
        result = _check_response(response, codes.no_content, accept_json)
        self.assertIsNone(result)

        response.status_code = codes.ok
        response.content = '{}'

        result = _check_response(response, codes.ok, accept_json)
        self.assertIsInstance(result, dict)

        response.content = '<xml/>'
        result = _check_response(response, codes.ok, 'xml')
        self.assertIsInstance(result, xml.dom.minidom.Document)

        response.content = None
        result = _check_response(response, codes.ok, accept_json)
        self.assertIsNone(result)

        response.status_code = codes.ok
        response.content = '{}'
        with self.assertRaises(cfy_exc.NonRecoverableError):
            _check_response(response, codes.ok, 'fail')

    @unittest.skip("")
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

    @unittest.skip("")
    def test_get(self):
        with mock.patch('versa_plugin.versaclient.requests', mock.MagicMock(
                return_value={})),\
             mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
                self.client.get('/path', 'data', 'json')

    @unittest.skip("")
    def test_post(self):
        with mock.patch('versa_plugin.versaclient.requests', mock.MagicMock(
                return_value={})),\
             mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
            self.client.post('/path', 'data', 'json')

    @unittest.skip("")
    def test_delete(self):
        with mock.patch('versa_plugin.versaclient.requests', mock.MagicMock(
                return_value={})),\
             mock.patch('versa_plugin.versaclient._check_response',
                        mock.MagicMock()):
            self.client.delete('/path')

    @unittest.skip("")
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

    @unittest.skip("")
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
