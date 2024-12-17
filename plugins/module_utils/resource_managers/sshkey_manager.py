# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Manage Cherry Servers SSH key resources."""
from typing import Optional, List

from .resource_manager import ResourceManager, Request, Method
from .. import normalizers


class SSHKeyManager(ResourceManager):
    """Manage Cherry Servers SSH key resources."""

    DEFAULT_TIMEOUT = 120

    @property
    def name(self) -> str:
        """Cherry Servers SSH key resource name."""
        return "ssh key"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_ssh_key(resource)

    def get_all(self) -> List[dict]:
        """Get all Cherry Servers SSH key resources."""
        return self.perform_request(
            Request(
                url="ssh-keys",
                method=Method.GET,
                timeout=self.DEFAULT_TIMEOUT,
                valid_status_codes=(200,),
                params=None,
            )
        )

    def get_by_id(self, key_id: int) -> Optional[dict]:
        """Get a single Cherry Servers SSH key resource by ID."""
        return self.perform_request(
            Request(
                url=f"ssh-keys/{key_id}",
                method=Method.GET,
                timeout=self.DEFAULT_TIMEOUT,
                valid_status_codes=(200,),
                params=None,
            )
        )

    def create(self, params: dict, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """Create a single Cherry Servers SSH key resource."""
        return self.perform_request(
            Request(
                url="ssh-keys",
                method=Method.POST,
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def update(self, key_id: int, params: dict, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """Update a Cherry Servers SSH key resource."""
        return self.perform_request(
            Request(
                url=f"ssh-keys/{key_id}",
                method=Method.PUT,
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def delete(self, key_id: int, timeout: int = DEFAULT_TIMEOUT):
        """Delete a Cherry Servers SSH key resource."""
        self.perform_request(
            Request(
                url=f"ssh-keys/{key_id}",
                method=Method.DELETE,
                timeout=timeout,
                valid_status_codes=(204,),
                params=None,
            )
        )
