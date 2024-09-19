# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""

from abc import ABC, abstractmethod
from typing import Optional, Any

from ansible.module_utils import basic as utils
from . import client


class BaseModule(ABC):
    """TODO"""

    def __init__(
        self, module: utils.AnsibleModule, api_client: client.CherryServersClient
    ):
        self._module = module
        self._api_client = api_client
        self.resource = self._read_by_id(self._module.params["id"])

    def run(self):
        """TODO"""
        if self._module.params["state"] == "absent":
            self._delete()
        elif self._module.params["id"]:
            self._update()
        else:
            self._create()

    @property
    @abstractmethod
    def name(self) -> str:
        """TODO"""

    @property
    def resource(self) -> Optional[dict]:
        """TODO"""
        return self._resource

    @resource.setter
    def resource(self, resource: Optional[dict]):
        if resource is not None:
            self._resource = self._normalize(resource)
        else:
            self._resource = None

    @abstractmethod
    def _normalize(self, resource: dict) -> dict:
        """TODO"""

    @abstractmethod
    def _create(self):
        """TODO"""

    def _exit_if_no_change_for_update(self, changed: bool):
        """TODO"""
        module = self._module
        if module.check_mode:
            if changed:
                module.exit_json(changed=True)
            else:
                module.exit_json(changed=False)
        else:
            if not changed:
                self._module.exit_json(changed=False, **{self.name: self.resource})

    @abstractmethod
    def _update(self):
        """TODO"""

    def _exit_if_no_change_for_delete(self):
        """TODO"""
        if self.resource:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
        else:
            self._module.exit_json(changed=False)

    @abstractmethod
    def _delete(self):
        """TODO"""

    @abstractmethod
    def _read_by_id(self, resource_id: Any) -> Optional[dict]:
        """TODO"""
