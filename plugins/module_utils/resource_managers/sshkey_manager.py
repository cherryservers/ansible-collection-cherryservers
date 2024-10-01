# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""

from .resource_manager import RequestTemplate, ResourceManager
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

    @property
    def _get_by_id_request(self) -> RequestTemplate:
        return RequestTemplate(
            url_template="ssh-keys/{id}",
            timeout=self.GET_TIMEOUT,
            valid_status_codes=(200,),
        )

    @property
    def _get_by_project_id_request(self) -> RequestTemplate:
        return RequestTemplate(
            url_template="projects/{project_id}/ssh-keys",
            timeout=self.GET_TIMEOUT,
            valid_status_codes=(200,),
        )

    def get_all(self):
        """TODO"""
        status, resp = self.api_client.send_request("GET", "ssh-keys", self.GET_TIMEOUT)
        if status != 200:
            self.module.fail_json(msg=self._build_api_error_msg("get", status, resp))
        normalized_resources = []
        for resource in resp:
            normalized_resources.append(self._normalize(resource))
        return normalized_resources
