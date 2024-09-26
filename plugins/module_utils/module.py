# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from abc import ABC, abstractmethod

from ansible.module_utils import basic as utils


class Module(ABC):
    """TODO"""

    def __init__(self):
        param_spec = get_base_arg_spec()
        param_spec.update(self._arg_spec)
        self._module = self._get_ansible_module(param_spec)

    @property
    @abstractmethod
    def name(self) -> str:
        """TODO"""

    @property
    @abstractmethod
    def _arg_spec(self) -> dict:
        """TODO"""

    @abstractmethod
    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        """TODO"""

    @abstractmethod
    def run(self):
        """TODO"""


def get_base_arg_spec() -> dict:
    """Return a dictionary with the base module argument spec."""
    return {
        "auth_token": {
            "type": "str",
            "no_log": True,
            "fallback": (utils.env_fallback, ["CHERRY_AUTH_TOKEN", "CHERRY_AUTH_KEY"]),
        },
    }
