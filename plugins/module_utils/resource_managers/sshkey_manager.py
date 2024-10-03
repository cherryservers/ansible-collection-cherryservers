# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from typing import Optional, List

from .resource_manager import ResourceManager, Request, Method
from .. import normalizers


class SSHKeyManager(ResourceManager):
    """TODO"""

    GET_TIMEOUT = 10

    @property
    def name(self) -> str:
        """TODO"""
        return "ssh key"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_ssh_key(resource)

    def get_all(self) -> List[dict]:
        """TODO"""
        return self.perform_request(
            Request(
                url="ssh-keys",
                method=Method.GET,
                timeout=self.GET_TIMEOUT,
                valid_status_codes=(200,),
                params=None,
            )
        )

    def get_by_id(self, key_id: int) -> Optional[dict]:
        """TODO"""
        return self.perform_request(
            Request(
                url=f"ssh-keys/{key_id}",
                method=Method.GET,
                timeout=self.GET_TIMEOUT,
                valid_status_codes=(200,),
                params=None,
            )
        )

    def create(self, params: dict, timeout: int = 15) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                url="ssh-keys",
                method=Method.POST,
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def update(self, key_id: int, params: dict, timeout: int = 15) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                url=f"ssh-keys/{key_id}",
                method=Method.PUT,
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def delete(self, key_id: int, timeout: int = 15):
        """TODO"""
        self.perform_request(
            Request(
                url=f"ssh-keys/{key_id}",
                method=Method.DELETE,
                timeout=timeout,
                valid_status_codes=(204,),
                params=None,
            )
        )
