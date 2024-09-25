# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Cherry Servers public API client.

This utility module is used by ansible modules to access Cherry Servers public API.
It uses the ansible provided standard utilities for working with HTTP(S).

Classes:

    CherryServersClient

"""

import json
from typing import Any, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ._version import _VERSION


class CherryServersClient:  # pylint: disable=too-few-public-methods
    """Cherry Server public API client.

    Upon instantiation this class will attempt to validate
    the provided Cherry Servers authentication token,
    and will fail the ansible module if unable to do so.
    This token can be set via the CHERRY_AUTH_TOKEN and
    CHERRY_AUTH_KEY environment variables or passed as
    an ansible module parameter.

    Methods:

        send_request(method: str, url: str, timeout: int, **kwargs) -> Tuple[int, Any]

    """

    _base_url = "https://api.cherryservers.com/v1/"

    def __init__(self, module: AnsibleModule):
        self._module = module
        self._base_url = self._module.params.get(
            "base_url", CherryServersClient._base_url
        )
        self._auth_token = self._module.params.get("auth_token", None)
        if self._auth_token is None:
            self._module.fail_json(msg="auth_token not provided.")

        self._headers = {
            "Authorization": f"Bearer {self._auth_token}",
            "Content-Type": "application/json",
            "User-Agent": f"cherryservers-ansible/{_VERSION}",
        }

        self._validate_auth_token()

    def _validate_auth_token(self):
        status, _2 = self.send_request("GET", "user", 10)
        if status != 200:
            self._module.fail_json(msg="Failed to validate auth token.")

    def send_request(
        self, method: str, url: str, timeout: int, **kwargs
    ) -> Tuple[int, Any]:
        """Send request to Cherry Servers API.

        This sends a request to Cherry Servers API.
        On success, returns the status code of the response along with response object.
        On failure, returns the status code of the response along with the error message.

        Args:

            method (str): The HTTP method to use.
            url (str): The URL to send the request to. Will be appended to the base URL.
            timeout (int): The timeout in seconds.
            kwargs (Any): The keyword arguments to pass to the requests.

        Returns:

            Tuple[int, Any]: The status code of the response along with response object (or
            error message on failure).

        """
        url = self._base_url + url
        data = json.dumps(kwargs)

        resp, info = fetch_url(
            self._module,
            url,
            method=method,
            headers=self._headers,
            data=data,
            timeout=timeout,
        )

        body = None
        if info["status"] >= 400:
            body = json.loads(info["body"])["message"]
        elif not 200 <= info["status"] < 300:
            self._module.fail_json(msg=info["msg"])
        elif method != "DELETE":
            body = json.loads(resp.read())

        return info["status"], body
