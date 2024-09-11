# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from abc import ABC, abstractmethod
from typing import List

from ansible.module_utils import basic as utils
from . import client


class APIError(Exception):
    """Unexpected Cherry Servers API error."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InfoModuleBase(ABC):
    """TODO"""

    def __init__(
        self, api_client: client.CherryServersClient, module: utils.AnsibleModule
    ):
        self.api_client = api_client
        self.module = module

    @property
    @abstractmethod
    def _name(self) -> str:
        """TODO"""

    @property
    @abstractmethod
    def _timeout(self) -> int:
        """TODO"""

    @property
    @abstractmethod
    def _get_by_id_url(self) -> str:
        """TODO"""

    @property
    @abstractmethod
    def _get_by_project_id_url(self) -> str:
        """TODO"""

    @abstractmethod
    def _normalize(self, raw_resource: dict) -> dict:
        """TODO"""

    @abstractmethod
    def _filter(self, resource: dict) -> bool:
        """TODO"""

    def _status_check(self, status_code: int, response: dict) -> bool:
        """TODO"""
        if status_code == 200:
            return True
        if status_code == 404:
            return False
        raise APIError(
            f"api error {status_code}, when retrieving {self._name} resource: {response}"
        )

    def _get_by_id(self) -> List[dict]:
        """TODO"""
        status, resp = self.api_client.send_request(
            "GET",
            self._get_by_id_url.format(id=self.module.params["id"]),
            self._timeout,
        )

        r = []

        try:
            if self._status_check(status, resp):
                r.append(resp)
        except APIError as e:
            self.module.fail_json(msg=str(e))

        return r

    def _get_by_project_id(self) -> List[dict]:
        """TODO"""
        status, resp = self.api_client.send_request(
            "GET",
            self._get_by_project_id_url.format(
                project_id=self.module.params["project_id"]
            ),
            self._timeout,
        )

        try:
            self._status_check(status, resp)
        except APIError as e:
            self.module.fail_json(msg=str(e))

        return resp

    def run(self):
        """TODO"""
        params = self.module.params

        if params["id"] is not None:
            resources = self._get_by_id()
        else:
            resources = self._get_by_project_id()

        r = []

        for resource in resources:
            resource = self._normalize(resource)
            if self._filter(resource):
                r.append(resource)

        self.module.exit_json(changed=False, **{self._name: r})
