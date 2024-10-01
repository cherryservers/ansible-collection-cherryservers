# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""
import time

from .. import normalizers
from .resource_manager import ResourceManager, RequestTemplate


class ServerManager(ResourceManager):
    """TODO"""

    GET_TIMEOUT = 20

    @property
    def name(self) -> str:
        """TODO"""
        return "server"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_server(resource)

    @property
    def _get_by_id_request(self) -> RequestTemplate:
        return RequestTemplate(
            url_template="servers/{id}",
            timeout=self.GET_TIMEOUT,
            valid_status_codes=(200,),
        )

    @property
    def _get_by_project_id_request(self) -> RequestTemplate:
        return RequestTemplate(
            url_template="projects/{project_id}/servers",
            timeout=self.GET_TIMEOUT,
            valid_status_codes=(200,),
        )

    def create_server(self, project_id: int, params: dict, timeout: int = 1800) -> dict:
        """TODO"""
        req_template = RequestTemplate(
            url_template="projects/{id}/servers",
            timeout=timeout,
            valid_status_codes=(201,),
        )
        return self.post_by_id(project_id, req_template, params)

    def update_server(self, server_id: int, params: dict, timeout: int = 180) -> dict:
        """TODO"""
        req_template = RequestTemplate(
            url_template="servers/{id}", timeout=timeout, valid_status_codes=(201,)
        )
        return self.put_by_id(server_id, req_template, params)

    def reinstall_server(
            self, server_id: int, params: dict, timeout: int = 1800
    ) -> dict:
        """TODO"""
        req_template = RequestTemplate(
            url_template="servers/{id}/actions",
            timeout=timeout,
            valid_status_codes=(201, 202),
        )
        return self.post_by_id(server_id, req_template, params)

    def delete_server(self, server_id: int, timeout: int = 30):
        """TODO"""
        req_template = RequestTemplate(
            url_template="servers/{id}", timeout=timeout, valid_status_codes=(204,)
        )
        self.delete_by_id(server_id, req_template)

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
