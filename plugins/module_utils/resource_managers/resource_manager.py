# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Manage Cherry Servers resources through the public API"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Sequence, List, Optional, Union

from ansible.module_utils import basic as utils
from .. import client


class Method(Enum):
    """Available HTTP/S methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class Request:
    """HTTP/S request template.

    Args:
        url (str): The URL to send the request to. This is not the full path, but a suffix that is added
            to the base client URL.
        timeout(int): Request timeout in seconds.
        valid_status_codes (Sequence[int]): Acceptable returned status codes.
        params(Optional[dict]): Parameters for the payload.
        method (Method): Method name.
    """

    url: str
    timeout: int
    valid_status_codes: Sequence[int]
    params: Optional[dict]
    method: Method


class ResourceManager(ABC):
    """Manage Cherry Servers resources through the public API.

    Each resource manager should extend this ABC.
    """

    def __init__(self, module: utils.AnsibleModule):
        self.module = module
        self.api_client = client.CherryServersClient(module)

    @property
    @abstractmethod
    def name(self) -> str:
        """Cherry Servers resource name."""

    @abstractmethod
    def _normalize(self, resource: dict) -> dict:
        """Normalize a resource.

        Usually this means removing unnecessary fields and/or replacing objects with their IDs.
        """

    def perform_request(self, req: Request) -> Union[Optional[dict], List[dict]]:
        """Perform a request for the Cherry Servers API.

        This method will handle the method specific checks and operations required.
        All returned resources are normalized.

        Args:
            req (Request): Request object.

        Returns:
            Union[Optional[dict], List[dict]]: Response from the Cherry Servers API.
                Returns None for DELETE requests and GET requests where the status code is valid, but the
                resource is not found.
                Returns a dict that contains the resource for POST and PUT method requests.
                Returns a list of dicts for GET requests that return a sequence of resources.
        """
        if req.params:
            status, resp = self.api_client.send_request(
                req.method.value, req.url, req.timeout, **req.params
            )
        else:
            status, resp = self.api_client.send_request(
                req.method.value, req.url, req.timeout
            )
        if status not in req.valid_status_codes:
            self.module.fail_json(
                msg=f"error {status} on attempt to {req.method} for {self.name}: {resp}"
            )
        if req.method.value == "DELETE":
            return None
        if req.method.value == "GET" and status == 200:
            if isinstance(resp, dict):
                return self._normalize(resp)
            if isinstance(resp, Sequence):
                normalized_resources = []
                for resource in resp:
                    normalized_resources.append(self._normalize(resource))
                return normalized_resources
        if req.method.value in ("POST", "PUT"):
            return self._normalize(resp)
        return None
