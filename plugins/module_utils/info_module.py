# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Cherry Servers ansible info module.

Classes:
    InfoModule

"""
from abc import ABC, abstractmethod
from typing import List, Optional

from . import module


class InfoModule(module.Module, ABC):
    """Cherry Servers ansible info module base class."""

    @abstractmethod
    def _filter(self, resource: dict) -> bool:
        """Check if the provided resource should be included in the response.

        Check if the resource matches the provided module arguments for gathering.

        Args:

            resource (dict): Resource to be checked.

        Returns:

            bool: True if the resource should be included in the response, False otherwise.
        """

    @abstractmethod
    def _resource_uniquely_identifiable(self) -> bool:
        """Check if the module has unique identifiers provided.

        Returns:
            bool: True if the module has arguments that can uniquely identify a resource.
        False otherwise.
        """

    @abstractmethod
    def _get_single_resource(self) -> Optional[dict]:
        """Get a single resource, typically by its ID.

        Returns:
            Optional[dict]: Normalized Cherry Servers resource. None if resource doesn't exist.
        """

    @abstractmethod
    def _get_resource_list(self) -> List[dict]:
        """Get a list of resources, typically by project ID.

        Returns:
            List[dict]: A list of normalized Cherry Servers resources.
        """

    def run(self):
        """Default execution logic for the info module."""
        resources = []
        if self._resource_uniquely_identifiable():
            resource = self._get_single_resource()
            if resource:
                resources.append(resource)
            else:
                self._module.fail_json(msg=f"no {self.name} resource found")
        else:
            resources = self._get_resource_list()

        filtered_resources = []
        for resource in resources:
            if self._filter(resource):
                filtered_resources.append(resource)
        self._module.exit_json(changed=False, **{self.name: filtered_resources})
