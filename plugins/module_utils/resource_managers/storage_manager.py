# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
from typing import List

from .. import normalizers
from .resource_manager import ResourceManager, Request, Method


class StorageManager(ResourceManager):
    """TODO"""

    GET_TIMEOUT = 20

    @property
    def name(self) -> str:
        """TODO"""
        return "storage"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_storage(resource)

    def get_by_id(self, storage_id: int) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                url=f"storages/{storage_id}",
                method=Method.GET,
                timeout=self.GET_TIMEOUT,
                valid_status_codes=(200, 404),
                params=None,
            )
        )

    def get_by_project_id(self, project_id: int) -> List[dict]:
        """TODO"""
        return self.perform_request(
            Request(
                url=f"projects/{project_id}/storages",
                method=Method.GET,
                timeout=self.GET_TIMEOUT,
                valid_status_codes=(200,),
                params=None,
            )
        )

    def create(self, project_id: str, params: dict, timeout: int = 30) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                url=f"projects/{project_id}/storages",
                method=Method.POST,
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def update(self, storage_id: int, params: dict, timeout: int = 30) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                url=f"storages/{storage_id}",
                method=Method.PUT,
                timeout=timeout,
                valid_status_codes=(201,),
                params=params,
            )
        )

    def delete(self, storage_id: int, timeout: int = 30):
        """TODO"""
        self.perform_request(
            Request(
                url=f"storages/{storage_id}",
                method=Method.DELETE,
                timeout=timeout,
                valid_status_codes=(204,),
                params=None,
            )
        )

    def attach(self, storage_id: int, server_id: int, timeout: int = 30) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                url=f"storages/{storage_id}/attachments",
                method=Method.POST,
                timeout=timeout,
                valid_status_codes=(201,),
                params={"attach_to": server_id},
            )
        )

    def detach(self, storage_id: int, timeout: int = 30):
        """TODO"""
        self.perform_request(
            Request(
                url=f"storages/{storage_id}/attachments",
                method=Method.DELETE,
                timeout=timeout,
                valid_status_codes=(204,),
                params=None,
            )
        )
