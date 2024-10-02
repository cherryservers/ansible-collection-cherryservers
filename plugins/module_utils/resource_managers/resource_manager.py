# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Sequence, Any, List, Optional, Union

from ansible.module_utils import basic as utils
from .. import client


@dataclass
class RequestTemplate:
    """TODO (rename this class later)"""

    url_template: str
    timeout: int
    valid_status_codes: Sequence[int]


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

    @property
    @abstractmethod
    def _get_by_id_request(self) -> RequestTemplate:
        """TODO"""

    @property
    @abstractmethod
    def _get_by_project_id_request(self) -> RequestTemplate:
        """TODO"""

    def _build_api_error_msg(
        self, operation: str, status_code: int, response: Any
    ) -> str:
        """TODO"""

        return (
            f"error {status_code} on attempt to {operation} for {self.name}: {response}"
        )

    def get_by_id(self, resource_id: Any) -> Optional[dict]:
        """TODO"""
        status, resp = self.api_client.send_request(
            "GET",
            self._get_by_id_request.url_template.format(id=resource_id),
            self._get_by_id_request.timeout,
        )
        if status not in self._get_by_id_request.valid_status_codes:
            self.module.fail_json(msg=self._build_api_error_msg("GET", status, resp))
        if status == 200:
            return self._normalize(resp)
        return None

    def get_by_project_id(self, project_id: int) -> List[dict]:
        """TODO"""
        status, resp = self.api_client.send_request(
            "GET",
            self._get_by_project_id_request.url_template.format(project_id=project_id),
            self._get_by_project_id_request.timeout,
        )
        if status not in self._get_by_project_id_request.valid_status_codes:
            self.module.fail_json(msg=self._build_api_error_msg("GET", status, resp))
        normalized_resources = []
        for resource in resp:
            normalized_resources.append(self._normalize(resource))
        return normalized_resources

    def post_by_id(
        self, resource_id: Union[str, int], request_templ: RequestTemplate, request_params: dict
    ) -> dict:
        """TODO"""
        status, resp = self.api_client.send_request(
            "POST",
            request_templ.url_template.format(id=resource_id),
            request_templ.timeout,
            **request_params,
        )
        if status not in request_templ.valid_status_codes:
            self.module.fail_json(msg=self._build_api_error_msg("POST", status, resp))
        return self._normalize(resp)

    def put_by_id(
        self, resource_id: Any, request_templ: RequestTemplate, request_params: dict
    ) -> dict:
        """TODO"""
        status, resp = self.api_client.send_request(
            "PUT",
            request_templ.url_template.format(id=resource_id),
            request_templ.timeout,
            **request_params,
        )
        if status not in request_templ.valid_status_codes:
            self.module.fail_json(msg=self._build_api_error_msg("PUT", status, resp))
        return self._normalize(resp)

    def delete_by_id(self, resource_id: Any, request_templ: RequestTemplate):
        """TODO"""
        status, resp = self.api_client.send_request(
            "DELETE",
            request_templ.url_template.format(id=resource_id),
            request_templ.timeout,
        )
        if status not in request_templ.valid_status_codes:
            self.module.fail_json(msg=self._build_api_error_msg("DELETE", status, resp))
