# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Manage Cherry Servers floating IP resources."""
from typing import Optional, List

from .resource_manager import ResourceManager, Request, Method
from .. import normalizers


class FloatingIPManager(ResourceManager):
    """Manage Cherry Servers floating IP resources."""

    DEFAULT_TIMEOUT = 120

    @property
    def name(self) -> str:
        """Cherry Servers floating IP resource name."""
        return "floating ip"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_fip(resource)

    def create(
        self, project_id: int, params: dict, timeout: int = DEFAULT_TIMEOUT
    ) -> dict:
        """Create a Cherry Servers floating IP resource."""
        return self.perform_request(
            Request(
                method=Method.POST,
                url=f"projects/{project_id}/ips",
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def delete(self, fip_id: str, timeout: int = DEFAULT_TIMEOUT):
        """Delete a Cherry Servers floating IP resource."""
        return self.perform_request(
            Request(
                method=Method.DELETE,
                url=f"ips/{fip_id}",
                timeout=timeout,
                valid_status_codes=(204,),
                params=None,
            )
        )

    def update(self, fip_id: str, params: dict, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """Update a Cherry Servers floating IP resource."""
        return self.perform_request(
            Request(
                method=Method.PUT,
                url=f"ips/{fip_id}",
                timeout=timeout,
                valid_status_codes=(200,),
                params=params,
            )
        )

    def get_by_id(self, fip_id: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[dict]:
        """Get a single Cherry Servers floating IP resource by ID."""
        return self.perform_request(
            Request(
                method=Method.GET,
                url=f"ips/{fip_id}",
                timeout=timeout,
                valid_status_codes=(200, 403, 404),
                params=None,
            )
        )

    def get_by_project_id(
        self, project_id: str, timeout: int = DEFAULT_TIMEOUT
    ) -> List[dict]:
        """Get a list of Cherry Servers floating IP resource by project ID."""
        return self.perform_request(
            Request(
                method=Method.GET,
                url=f"projects/{project_id}/ips",
                timeout=timeout,
                valid_status_codes=(200,),
                params=None,
            )
        )
