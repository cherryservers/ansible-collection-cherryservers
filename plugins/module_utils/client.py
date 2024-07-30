import json
from typing import Tuple, Any

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


class ClientError(Exception):
    """A client related error."""


class CherryServersClient(object):
    _base_url = "https://api.cherryservers.com/v1/"

    def __init__(self, module: AnsibleModule):
        self._module = module
        self._base_url = self._module.params.get(
            "base_url", CherryServersClient._base_url
        )
        self._bearer_token = self._module.params.get("bearer_token", None)
        self._headers = {
            "Authorization": f"Bearer {self._bearer_token}",
            "Content-Type": "application/json",
        }

        self._validate_bearer_token()

    def _validate_bearer_token(self):
        try:
            self.send_request("GET", "user")
        except ClientError as err:
            self._module.fail_json(msg="Failed to validate bearer token.", error=err)

    def send_request(self, method: str, url: str, **kwargs) -> Any:
        url = self._base_url + url
        data = json.dumps(kwargs)

        resp, info = fetch_url(
            self._module, url, method=method, headers=self._headers, data=data
        )

        body = resp.read()
        if info["status"] >= 200:
            raise ClientError(info["body"])

        return json.loads(body)
