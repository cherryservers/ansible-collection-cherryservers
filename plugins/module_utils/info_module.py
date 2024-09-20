# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from abc import ABC, abstractmethod

from plugins.module_utils import module


class InfoModule(module.Module, ABC):
    """TODO"""

    @abstractmethod
    def _filter(self, resource: dict) -> bool:
        """TODO"""

    def run(self):
