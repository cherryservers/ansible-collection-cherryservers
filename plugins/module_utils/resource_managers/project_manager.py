# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Manage Cherry Servers project resources."""
from typing import Optional, List

from .resource_manager import ResourceManager, Request, Method
from .. import normalizers


class ProjectManager(ResourceManager):
    """Manage Cherry Servers project resources."""

    GET_TIMEOUT = 10

    @property
    def name(self) -> str:
        """Cherry Servers project  resource name."""
        return "project"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_project(resource)

    def get_by_team_id(self, team_id: int) -> List[dict]:
        """Get a list of Cherry Servers project resources by team id."""
        return self.perform_request(
            Request(
                url=f"teams/{team_id}/projects",
                method=Method.GET,
                timeout=self.GET_TIMEOUT,
                valid_status_codes=(200,),
                params=None,
            )
        )

    def get_by_id(self, key_id: int) -> Optional[dict]:
        """Get a single Cherry Servers project resource by its ID."""
        return self.perform_request(
            Request(
                url=f"projects/{key_id}",
                method=Method.GET,
                timeout=self.GET_TIMEOUT,
                valid_status_codes=(200, 404),
                params=None,
            )
        )

    def create(self, team_id: int, params: dict, timeout: int = 15) -> dict:
        """Create a single Cherry Servers project resource."""
        return self.perform_request(
            Request(
                url=f"teams/{team_id}/projects",
                method=Method.POST,
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def update(self, key_id: int, params: dict, timeout: int = 15) -> dict:
        """Update a Cherry Servers project resource."""
        return self.perform_request(
            Request(
                url=f"projects/{key_id}",
                method=Method.PUT,
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def delete(self, key_id: int, timeout: int = 15):
        """Delete a Cherry Servers project resource."""
        self.perform_request(
            Request(
                url=f"projects/{key_id}",
                method=Method.DELETE,
                timeout=timeout,
                valid_status_codes=(204,),
                params=None,
            )
        )
