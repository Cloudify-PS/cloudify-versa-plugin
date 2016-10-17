import requests
import json
from xml.dom.minidom import parseString

from cloudify import exceptions as cfy_exc
from requests.exceptions import RequestException

JSON = 'json'
XML = 'xml'


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
    def __init__(self, config):
        self.versa_url = config["versa_url"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.username = config["username"]
        self.password = config["password"]
        self.access_token = None
        self.refresh_token = None
        self.verify = False

    def __enter__(self):
        self.get_token()
        return self

    def __exit__(self, type, value, traceback):
        self.revoke_token()

    def get_token(self):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
            "grant_type": "password"}
        result = self.post("/auth/token", json.dumps(data), JSON,
                           return_code=200)
        try:
            self.access_token = result['access_token']
            self.refresh_token = result['refresh_token']
        except (KeyError, TypeError):
            raise cfy_exc.NonRecoverableError(
                "Incorrect reply: {}".format(result))

    def revoke_token(self):
        self.post("/auth/revoke", None, None, return_code=200, accept=JSON)

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
        headers = self._get_headers(content_type, accept)
        try:
            response = request_type(
                self.versa_url + path,
                headers=headers, data=data,
                verify=self.verify)
            return _check_response(response, return_code, accept)
        except RequestException:
            raise cfy_exc.HttpException(path, 404, "")

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

    def _refresh_token(self):
        pass
