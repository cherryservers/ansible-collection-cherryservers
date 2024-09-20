# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Sequence, Any

from plugins.module_utils import client
from ansible.module_utils.basic import utils


class APIError(Exception):
    """Unexpected Cherry Servers API error."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class Request(ABC):
    """TODO"""

    def __init__(
        self,
        api_client: client.CherryServersClient,
        method: str,
        valid_status_codes: Collection[int],
    ):
        self.api_client = api_client
        self.method = method
        self.valid_status_codes = valid_status_codes

    def _validate_status_code(self, status_code: int):
        if status_code not in self.valid_status_codes:
            raise APIError(f"error {status_code}")

    @abstractmethod
    def perform(
        self, path_params: Sequence[str], query_params: dict, timeout: int
    ) -> Any:
        """TODO"""


class Module(ABC):
    """TODO"""

    def __init__(self):
        param_spec = get_base_param_spec()
        param_spec.update(self.param_spec)
        self.module = self._load_ansible_module(param_spec)
        self.api_client = client.CherryServersClient(self.module)

    @property
    @abstractmethod
    def param_spec(self) -> dict:
        """TODO"""

    @abstractmethod
    def _load_ansible_module(self, params: dict) -> utils.AnsibleModule:
        """TODO"""

    @abstractmethod
    def run(self):
        """TODO"""

    def get_single_resource(self, get_resource: Request):
        """TODO"""


def get_base_param_spec() -> dict:
    """Return a dictionary with the base module argument spec."""
    return {
        "auth_token": {
            "type": "str",
            "no_log": True,
            "fallback": (utils.env_fallback, ["CHERRY_AUTH_TOKEN", "CHERRY_AUTH_KEY"]),
        },
    }
