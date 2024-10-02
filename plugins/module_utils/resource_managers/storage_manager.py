# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""TODO"""

from .. import normalizers
from .resource_manager import ResourceManager, RequestTemplate


class StorageManager(ResourceManager):
    """TODO"""
    GET_TIMEOUT = 20

    @property
    def name(self) -> str:
        """TODO"""
        return "storage"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_storage(resource)

    @property
    def _get_by_id_request(self) -> RequestTemplate:
        return RequestTemplate(
            url_template="storages/{id}",
            timeout=self.GET_TIMEOUT,
            valid_status_codes=(200, 404)
        )

    @property
    def _get_by_project_id_request(self) -> RequestTemplate:
        return RequestTemplate(
            url_template="projects/{project_id}/storages",
            timeout=self.GET_TIMEOUT,
            valid_status_codes=(200,)
        )
