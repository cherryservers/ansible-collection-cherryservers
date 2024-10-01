#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: server_info

short_description: Gather information about your Cherry Servers servers

version_added: "0.1.0"

description:
  - Gather information about your Cherry Servers servers.
  - Returns servers that match all your provided options in the given project.
  - Alternatively, you can get a single server by specifying its ID, all other arguments ar ignored.

options:
    id:
        description:
            - ID of the server.
            - Required if O(project_id) is not provided.
        type: int
    project_id:
        description:
            - The ID of the project the server belongs to.
            - Required if O(id) is not provided.
        type: int
    plan:
        description:
            - Slug of the server plan.
        type: str
    image:
        description:
            - Server OS image slug.
        type: str
    region:
        description:
            - Slug of the server region.
        type: str
    hostname:
        description:
            - Server hostname.
        type: str
    tags:
        description:
            - Server tags.
        type: dict
    spot_market:
        description:
            - Whether the server is a spot instance.
        type: bool
    storage_id:
        description:
            - Elastic block storage ID.
        type: int
extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get single server
  local.cherryservers.server_info:
    id: 593462
  register: result

- name: Get all project servers
  local.cherryservers.server_info:
    project_id: "213668"
  register: result

- name: 'Get all servers in the EU Nord-1 region, that have the env: test-upd tag'
  local.cherryservers.server_info:
    region: "eu_nord_1"
    project_id: "213668"
    tags:
      env: "test-upd"
  register: result

- name: Get servers by plan
  local.cherryservers.server_info:
    project_id: "213668"
    plan: cloud_vps_1
  register: result
"""

RETURN = r"""
cherryservers_servers:
  description: Server data.
  returned: always
  type: list
  elements: dict
  contains:
    hostname:
      description: Server hostname.
      returned: always
      type: str
      sample: "honest-toucan"
    id:
      description: Server ID.
      returned: always
      type: int
      sample: "123456"
    image:
      description: Server OS image slug.
      returned: always
      type: str
      sample: "fedora_39_64bit"
    ip_addresses:
      description: Server IP addresses.
      returned: always
      type: list
      elements: dict
      contains:
        CIDR:
          description: CIDR block of the IP.
          returned: always
          type: str
          sample: "10.168.101.0/24"
        address:
          description: IP address.
          returned: always
          type: str
          sample: "10.168.101.0"
        address_family:
          description: IP address family (IPv4 or IPv6).
          returned: always
          type: int
          sample: 4
        id:
          description: IP address ID.
          returned: always
          type: str
          sample: "16a70e80-d338-1b1e-f6ef-d5aacf9f3718"
        type:
          description: IP address type.
          returned: always
          type: str
          sample: "floating-ip"
    name:
      description: Server name.
      returned: always
      type: str
      sample: "Cloud VPS 1"
    plan:
      description: Slug of the server plan.
      returned: always
      type: str
      sample: "cloud_vps_1"
    project_id:
      description: Cherry Servers project ID, associated with the server.
      returned: always
      type: int
      sample: 123456
    region:
      description: Slug of the server region.
      returned: always
      type: str
      sample: "eu_nord_1"
    spot_market:
      description: Whether the server is a spot market instance.
      returned: always
      type: bool
      sample: false
    ssh_keys:
      description: Set of the SSH key IDs allowed to SSH to the server.
      returned: always
      type: list
      elements: int
      sample: [0000, 1111]
    status:
      description: Server status.
      returned: always
      type: str
      sample: "deploying"
    storage_id:
      description: Server storage block ID. Null if doesn't exist.
      returned: always
      type: int
      sample: 593063
    tags:
      description: Key/value metadata for server tagging.
      returned: always
      type: dict
      sample:
        env: "dev"
"""

from typing import List
from ansible.module_utils import basic as utils
from ..module_utils import info_module
from ..module_utils.resource_managers import server_manager


class ServerInfoModule(info_module.InfoModule):
    """Server info module."""

    def __init__(self):
        super().__init__()
        self._resource_manager = server_manager.ServerManager(self._module)

    def _resource_uniquely_identifiable(self) -> bool:
        if self._module.params.get("id") is None:
            return False
        return True

    def _filter(self, resource: dict) -> bool:
        params = self._module.params
        if all(
            params[k] is None or params[k] == resource[k]
            for k in (
                "region",
                "hostname",
                "plan",
                "image",
                "id",
                "project_id",
                "spot_market",
                "storage_id",
            )
        ) and (
            params["tags"] is None
            or all(params["tags"][k] == resource["tags"].get(k) for k in params["tags"])
        ):
            return True
        return False

    def _get_single_resource(self) -> dict:
        return self._resource_manager.get_by_id(self._module.params["id"])

    def _get_resource_list(self) -> List[dict]:
        return self._resource_manager.get_by_project_id(
            self._module.params["project_id"]
        )

    @property
    def name(self) -> str:
        """Server resource name"""
        return "cherryservers_servers"

    @property
    def _arg_spec(self) -> dict:
        return {
            "tags": {
                "type": "dict",
            },
            "region": {"type": "str"},
            "hostname": {"type": "str"},
            "plan": {"type": "str"},
            "image": {"type": "str"},
            "id": {"type": "int"},
            "project_id": {"type": "int"},
            "spot_market": {"type": "bool"},
            "storage_id": {"type": "int"},
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
            required_one_of=[("project_id", "id")],
        )


def main():
    """Main function."""
    ServerInfoModule().run()


if __name__ == "__main__":
    main()
