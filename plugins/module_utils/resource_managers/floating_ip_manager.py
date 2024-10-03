# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from typing import Optional, List

from .resource_manager import ResourceManager, Request, Method
from .. import normalizers


class FloatingIPManager(ResourceManager):
    """TODO"""

    GET_TIMEOUT = 30

    @property
    def name(self) -> str:
        """TODO"""
        return "floating ip"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_fip(resource)

    def create(self, project_id: int, params: dict, timeout: int = 30) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.POST,
                url=f"projects/{project_id}/ips",
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def delete(self, fip_id: str, timeout: int = 30):
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.DELETE,
                url=f"ips/{fip_id}",
                timeout=timeout,
                valid_status_codes=(204,),
                params=None,
            )
        )

    def update(self, fip_id: str, params: dict, timeout: int = 30) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.PUT,
                url=f"ips/{fip_id}",
                timeout=timeout,
                valid_status_codes=(200,),
                params=params,
            )
        )

    def get_by_id(self, fip_id: str, timeout: int = 30) -> Optional[dict]:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.GET,
                url=f"ips/{fip_id}",
                timeout=timeout,
                valid_status_codes=(200, 403, 404),
                params=None,
            )
        )

    def get_by_project_id(self, project_id: str, timeout: int = 30) -> List[dict]:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.GET,
                url=f"projects/{project_id}/ips",
                timeout=timeout,
                valid_status_codes=(200,),
                params=None,
            )
        )
