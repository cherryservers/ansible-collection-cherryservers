# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""

from abc import ABC, abstractmethod
from typing import Optional

from . import module


class StandardModule(module.Module, ABC):
    """TODO"""

    @abstractmethod
    def _get_resource(self) -> Optional[dict]:
        """TODO"""

    @abstractmethod
    def _perform_deletion(self, resource: dict):
        """TODO"""

    def _delete_resource(self, resource: Optional[dict]):
        """TODO"""
        if resource:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
        else:
            self._module.exit_json(changed=False)
        self._perform_deletion(resource)
        self._module.exit_json(changed=True)

    @abstractmethod
    def _get_update_requests(self, resource: dict) -> dict:
        """ "TODO"""

    @abstractmethod
    def _perform_update(self, requests: dict, resource: dict) -> dict:
        """TODO"""

    def _update_resource(self, resource: dict):
        """TODO"""
        requests = self._get_update_requests(resource)

        if self._module.check_mode:
            if requests:
                self._module.exit_json(changed=True)
            else:
                self._module.exit_json(changed=False)
        else:
            if not requests:
                self._module.exit_json(changed=False, **{self.name: resource})

        resource = self._perform_update(requests, resource)

        self._module.exit_json(changed=True, **{self.name: resource})

    @abstractmethod
    def _validate_creation_params(self):
        """TODO"""

    @abstractmethod
    def _perform_creation(self) -> dict:
        """TODO"""

    def _create_resource(self):
        self._validate_creation_params()

        if self._module.check_mode:
            self._module.exit_json(changed=True)

        resource = self._perform_creation()

        self._module.exit_json(changed=True, **{self.name: resource})

    def run(self):
        """Default module execution logic."""
        resource = self._get_resource()
        if self._module.params["state"] == "absent":
            self._delete_resource(resource)
        if resource:
            self._update_resource(resource)
        else:
            self._create_resource()
