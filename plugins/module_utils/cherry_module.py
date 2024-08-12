# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""TODO"""
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional

from ansible.module_utils import basic as utils
from . import client


@dataclass
class ResourceURLs:
    """TODO"""

    creation_url: str
    removal_url: str
    update_url: str
    retrieval_url: str


@dataclass
class ResourceTimeouts:
    """TODO"""

    creation_timeout: int
    removal_timeout: int
    retrieval_timeout: int
    update_timeout: int


class CherryModule(ABC):
    """TODO"""

    def __init__(
        self,
        module: utils.AnsibleModule,
        urls: ResourceURLs,
        timeouts: ResourceTimeouts,
    ):
        self.module = module
        self.api_client = client.CherryServersClient(module)
        self.urls = urls
        self.timeouts = timeouts
        self.resource = self._get_resource(
            urls.retrieval_url, timeouts.retrieval_timeout
        )
        self._normalize_resource()

    @property
    @abstractmethod
    def resource_identifier_keys(self) -> Sequence[str]:
        """TODO"""

    @property
    @abstractmethod
    def resource_name(self) -> str:
        """TODO"""

    @property
    @abstractmethod
    def required_for_resource_creation(self) -> Sequence[str]:
        """TODO"""

    def run_state_logic(self):
        """TODO"""
        if self.module.params["state"] == "present":
            if self.resource:
                if self._check_diff():
                    self._update_resource()
                elif self.module.check_mode:
                    self.module.exit_json(changed=False)
                else:
                    self.module.exit_json(
                        changed=False, **{self.resource_name: self.resource}
                    )
            else:
                self._create_resource()
        elif self.module.params["state"] == "absent":
            if self.resource:
                self._delete_resource()
            else:
                self.module.exit_json(changed=False)

    def _get_resource(
        self,
        url: str,
        timeout: int,
    ) -> Optional[dict]:
        """TODO"""

        status, resp = self.api_client.send_request("GET", url, timeout)
        if status != 200:
            self.module.fail_json(msg=f"Failed to get resource: {resp}")

        matching_resources = []

        for resource in resp:
            if any(
                resource[k] == self.module.params[k]
                for k in self.resource_identifier_keys
            ):
                matching_resources.append(resource)

        if len(matching_resources) > 1:
            self.module.fail_json(
                msg=f"Multiple matching resources found: {matching_resources}"
            )

        if not matching_resources:
            return None

        return matching_resources[0]

    @abstractmethod
    def _normalize_resource(self):
        """TODO"""

    def _create_resource(
        self,
        **kwargs,
    ):
        """TODO"""
        params = self.module.params
        module = self.module

        if any(params[k] is None for k in self.required_for_resource_creation):
            module.fail_json(
                msg=f"Missing required parameters: {self.required_for_resource_creation}"
            )

        if module.check_mode:
            module.exit_json(changed=True)

        status, resp = self.api_client.send_request(
            "POST", self.urls.creation_url, self.timeouts.creation_timeout, **kwargs
        )

        if status != 201:
            module.fail_json(msg=f"Failed to create resource: {resp}")

        # We need to do another GET request, because the object returned from POST
        # doesn't always contain all the necessary data.

        status, resp = self.api_client.send_request(
            "GET", self.urls.retrieval_url, self.timeouts.retrieval_timeout
        )

        if status != 200:
            module.fail_json(
                msg=f"Failed to retrieve resource after creating it: {resp}"
            )

        self.resource = resp
        self._normalize_resource()
        module.exit_json(changed=True, **{self.resource_name: self.resource})

    def _update_resource(self):
        """TODO"""

    def _delete_resource(self):
        """TODO"""

    def _check_diff(self) -> bool:
        """TODO"""
