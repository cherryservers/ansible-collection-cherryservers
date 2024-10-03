# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Sequence, List, Optional, Union

from ansible.module_utils import basic as utils
from .. import client


class Method(Enum):
    """TODO"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class Request:
    """TODO"""

    url: str
    timeout: int
    valid_status_codes: Sequence[int]
    params: Optional[dict]
    method: Method


class ResourceManager(ABC):
    """TODO"""

    def __init__(self, module: utils.AnsibleModule):
        self.module = module
        self.api_client = client.CherryServersClient(module)

    @property
    @abstractmethod
    def name(self) -> str:
        """TODO"""

    @abstractmethod
    def _normalize(self, resource: dict) -> dict:
        """TODO"""

    def perform_request(self, req: Request) -> Union[Optional[dict], List[dict]]:
        """TODO"""
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
        if (
            req.method.value == "GET"
            and status == 200  # We want to return None on 404, when using GET.
        ):
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
