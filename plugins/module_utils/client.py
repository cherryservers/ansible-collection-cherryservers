# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Cherry Servers public API client.

This utility module is used by ansible modules to access Cherry Servers public API.
It uses the ansible provided standard utilities for working with HTTP(S).

Classes:

    CherryServersClient

Exceptions:

    ClientError

"""

import json
from typing import Any

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


class ClientError(Exception):
    """A client related error."""


class CherryServersClient:  # pylint: disable=too-few-public-methods
    """Cherry Server public API client.

    Upon instantiation this class will attempt to validate
    the provided Cherry Servers authentication token,
    and will fail the ansible module if unable to do so.

    Methods:

        send_request(method: str, url: str, **kwargs) -> Any

    """

    _base_url = "https://api.cherryservers.com/v1/"

    def __init__(self, module: AnsibleModule):
        self._module = module
        self._base_url = self._module.params.get(
            "base_url", CherryServersClient._base_url
        )
        self._auth_token = self._module.params.get("auth_token", None)
        if self._auth_token is None:
            self._module.fail_json(msg="auth_token is required.")

        self._headers = {
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json",
        }

        self._validate_auth_token()

    def _validate_auth_token(self):
        try:
            self.send_request("GET", "user")
        except ClientError:
            self._module.fail_json(msg="Failed to validate auth token.")

    def send_request(self, method: str, url: str, **kwargs) -> Any:
        """Send request to Cherry Servers API.

        This sends a request to Cherry Servers API and returns the response payload upon success.
        If an API error occurs, a ClientError exception is raised with the error payload.

        Args:

            method (str): The HTTP method to use.
            url (str): The URL to send the request to. Will be appended to the base URL.
            kwargs (dict): The keyword arguments to pass to the requests.

        Returns:

            Any: The response payload. A Python object created by json.loads().

        Raises:

            ClientError: The API server responded with an error.
        """
        url = self._base_url + url
        data = json.dumps(kwargs)

        resp, info = fetch_url(
            self._module, url, method=method, headers=self._headers, data=data
        )

        body = resp.read()
        if info["status"] >= 400:
            raise ClientError(json.loads(info["body"]))

        return json.loads(body)
