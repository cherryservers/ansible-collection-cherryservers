# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
import time
from typing import Optional, List

from .. import normalizers
from .resource_manager import ResourceManager, Request, Method


class ServerManager(ResourceManager):
    """TODO"""

    GET_TIMEOUT = 20

    @property
    def name(self) -> str:
        """TODO"""
        return "server"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_server(resource)

    def get_by_id(self, server_id: int) -> Optional[dict]:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.GET,
                url=f"servers/{server_id}",
                valid_status_codes=(200, 404),
                timeout=self.GET_TIMEOUT,
                params=None,
            )
        )

    def get_by_project_id(self, project_id: int) -> List[dict]:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.GET,
                url=f"projects/{project_id}/servers",
                valid_status_codes=(200,),
                timeout=self.GET_TIMEOUT,
                params=None,
            )
        )

    def create_server(self, project_id: int, params: dict, timeout: int = 1800) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.POST,
                url=f"projects/{project_id}/servers",
                valid_status_codes=(201,),
                timeout=timeout,
                params=params,
            )
        )

    def update_server(self, server_id: int, params: dict, timeout: int = 180) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.PUT,
                url=f"servers/{server_id}",
                valid_status_codes=(201,),
                timeout=timeout,
                params=params,
            )
        )

    def reinstall_server(
        self, server_id: int, params: dict, timeout: int = 1800
    ) -> dict:
        """TODO"""
        return self.perform_request(
            Request(
                method=Method.POST,
                url=f"servers/{server_id}/actions",
                valid_status_codes=(201, 202),
                timeout=timeout,
                params=params,
            )
        )

    def delete_server(self, server_id: int, timeout: int = 30):
        """TODO"""
        self.perform_request(
            Request(
                method=Method.DELETE,
                url=f"servers/{server_id}",
                timeout=timeout,
                params=None,
                valid_status_codes=(204,),
            )
        )

    def wait_for_active(self, server: dict, timeout: int = 1800) -> dict:
        """TODO"""
        time_passed = 0

        while server["status"] != "deployed":
            time.sleep(10)
            time_passed += 10

            server = self.get_by_id(server["id"])

            if time_passed >= timeout:
                self.module.fail_json(
                    msg=f"timed out waiting for {self.name} to become active"
                )

        return server
