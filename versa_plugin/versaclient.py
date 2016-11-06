import requests
import json
import os
from os import chmod
from xml.dom.minidom import parseString
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from cloudify import exceptions as cfy_exc
from cloudify import ctx
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
JSON = 'json'
XML = 'xml'


def _save_key_file(path, value):
    path = os.path.expanduser(path)
    with open(path, 'w') as content_file:
        chmod(path, 0600)
        content_file.write(value)


def _check_response(response, return_code, accept):
    if response.status_code == requests.codes.no_content:
        return None
    if response.status_code != return_code:
        raise cfy_exc.HttpException(response.url, response.status_code,
                                    response.content)
    if response.content:
        if accept == JSON:
            return json.loads(response.content)
        else:
            return parseString(response.content)
    else:
        return None


class VersaClient():
    def __init__(self, config, key_file):
        self.versa_url = config["versa_url"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.username = config["username"]
        self.password = config["password"]
        self.access_token = None
        self.verify = False
        self.key_file = key_file

    def __enter__(self):
        self.get_token()
        return self

    def __exit__(self, type, value, traceback):
        # self.revoke_token()
        pass

    def read_tokens_form_file(self):
        if os.path.isfile(self.key_file):
            with open(self.key_file) as file:
                self.access_token = file.readline().rstrip()
            return True
        return False

    def save_token_to_file(self):
        with open(self.key_file, "w") as file:
            file.write(self.access_token)

    def get_token(self):
        if self.read_tokens_form_file():
            return
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
            "grant_type": "password"}
        headers = self._get_headers(JSON, JSON)
        result = requests.post(self.versa_url + "/auth/token",
                               headers=headers, data=json.dumps(data),
                               verify=self.verify)
        try:
            result = json.loads(result.content)
            self.access_token = result['access_token']
            self.save_token_to_file()
        except (KeyError, TypeError, ValueError):
            raise cfy_exc.NonRecoverableError(
                "Incorrect reply: {}".format(result))

    def revoke_token(self):
        headers = {"Authorization": "Bearer {}".format(self.access_token)}
        requests.post(self.versa_url + "/auth/revoke",
                      headers=headers, verify=self.verify)
        if os.path.isfile(self.key_file):
            os.remove(self.key_file)
        self.access_token = None

    def get(self, path, data, content_type, return_code=200, accept=JSON):
        return self._request(requests.get, path, data,
                             content_type, return_code, accept)

    def post(self, path, data, content_type, return_code=201, accept=JSON):
        return self._request(requests.post, path, data,
                             content_type, return_code, accept)

    def put(self, path, data, content_type, return_code=204, accept=JSON):
        return self._request(requests.put, path, data,
                             content_type, return_code, accept)

    def delete(self, path, return_code=204, accept=JSON):
        return self._request(requests.delete, path, None,
                             None, return_code, accept)

    def _request(self, request_type, path, data, content_type, return_code,
                 accept):
        retry = 0
        ctx.logger.debug("Sending request to {0} with data {1}".format(
            self.versa_url + path, str(data))
        while True:
            headers = self._get_headers(content_type, accept)
            response = request_type(
                self.versa_url + path,
                headers=headers, data=data,
                verify=self.verify)
            if response.status_code == 401:
                if retry == 1:
                    break
                retry += 1
                self.revoke_token()
                self.get_token()
            else:
                return _check_response(response, return_code, accept)

    def _get_headers(self, content_type, accept):
        content_dict = {'json': 'application/json', 'xml': 'application/xml'}
        headers = {}
        if content_type:
            try:
                headers['Content-type'] = content_dict[content_type]
            except KeyError:
                raise cfy_exc.NonRecoverableError(
                    "Unknown content-type: {}".format(content_type))
        if self.access_token:
            headers["Authorization"] = "Bearer {}".format(self.access_token)
        headers['Accept'] = content_dict[accept]
        return headers
