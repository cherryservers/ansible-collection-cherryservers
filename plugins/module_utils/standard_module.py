# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Standard module for a Cherry Servers resource."""

from abc import ABC, abstractmethod
from typing import Optional

from . import module


class StandardModule(module.Module, ABC):
    """Standard module for a Cherry Servers resource."""

    @abstractmethod
    def _get_resource(self) -> Optional[dict]:
        """Get a Cherry Servers resource.

        Returns:
            Optional[dict]: Normalized Cherry Servers resource, or None, if the resource can't be found.
        """

    @abstractmethod
    def _perform_deletion(self, resource: dict):
        """Perform the actual deletion of the resource.

        Args:
            resource (dict): A normalized Cherry Servers resource.
        """

    def _delete_resource(self, resource: Optional[dict]):
        """Cherry Servers Ansible module resource deletion logic.

        Args:
            resource (Optional[dict]): A normalized Cherry Servers resource, or None, if the resource can't be found.
        """
        if resource:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
        else:
            self._module.exit_json(changed=False)
        self._perform_deletion(resource)
        self._module.exit_json(changed=True)

    @abstractmethod
    def _get_update_requests(self, resource: dict) -> dict:
        """Get the update request params.

        Args:
            resource (dict): A normalized Cherry Servers resource.
        Returns:
            dict: A dictionary of dictionaries containing the update request params.
            Each inner dictionaries key should be the name of update (for example, 'basic' or 'reinstall'), while the
            value should be the param payload.
        """

    @abstractmethod
    def _perform_update(self, requests: dict, resource: dict) -> dict:
        """Perform the actual updating of the resource.

        Args:
            requests (dict): A dictionary of dictionaries containing the update request params.
            resource (dict): A normalized Cherry Servers resource.
        Returns:
            dict: A normalized Cherry Servers resource.
        """

    def _update_resource(self, resource: dict):
        """Cherry Servers Ansible module resource update logic."""
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
        """Validate that all the required arguments for resource creation have been provided.

        Fail the module if they have not.
        """

    @abstractmethod
    def _perform_creation(self) -> dict:
        """Perform the actual creation of the resource."""

    def _create_resource(self):
        """Cherry Servers Ansible module resource creation logic."""
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
