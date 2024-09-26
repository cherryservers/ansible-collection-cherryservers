# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from abc import ABC, abstractmethod
from typing import Optional, List

from . import module


class InfoModule(module.Module, ABC):
    """TODO"""

    @abstractmethod
    def _filter(self, resource: dict) -> bool:
        """TODO"""

    @abstractmethod
    def _resource_uniquely_identifiable(self) -> bool:
        pass

    @abstractmethod
    def _get_single_resource(self) -> Optional[dict]:
        pass

    @abstractmethod
    def _get_resource_list(self) -> List[dict]:
        pass

    def run(self):
        """TODO"""
        resources = []
        if self._resource_uniquely_identifiable():
            resource = self._get_single_resource()
            if resource:
                resources.append(resource)
        else:
            resources = self._get_resource_list()

        filtered_resources = []
        for resource in resources:
            if self._filter(resource):
                filtered_resources.append(resource)
        self._module.exit_json(changed=False, **{self.name: filtered_resources})
