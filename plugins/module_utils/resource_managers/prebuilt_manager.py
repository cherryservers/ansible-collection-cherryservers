# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Manage Cherry Servers prebuilt plan resources."""

from typing import List

from .resource_manager import ResourceManager, Request, Method
from .. import normalizers


class PrebuiltManager(ResourceManager):
    """Manage Cherry Servers prebuilt plan resources."""

    DEFAULT_TIMEOUT = 120

    @property
    def name(self) -> str:
        """Cherry Servers prebuilt plan resource name."""
        return "prebuilt"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_prebuilt_plan(resource)

    def list(self, team_id: int, base_plan: str, region: str) -> List[dict]:
        """List Cherry Servers prebuilt plans."""
        return self.perform_request(
            Request(
                url=f"teams/{team_id}/plans/{base_plan}/prebuilts?region={region}",
                method=Method.GET,
                timeout=self.DEFAULT_TIMEOUT,
                valid_status_codes=(200,),
                params=None,
            )
        )
