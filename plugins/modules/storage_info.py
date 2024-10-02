#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: storage_info

short_description: Gather information about your Cherry Servers EBS volumes

version_added: "0.1.0"

description:
  - Gather information about your Cherry Servers elastic block storage volumes.
  - Returns volumes that match all your provided options in the given project.
  - Alternatively, you can gather information directly by volume ID.

options:
    state:
        description:
            - The state of the volume.
        choices: ['attached', 'detached']
        type: str
    id:
        description:
            - ID of the volume.
            - Required if O(project_id) is not provided.
        type: int
    description:
        description:
            - User configured description of the volume.
        type: str
    project_id:
        description:
            - ID of the project the volume belongs to.
            - Required if O(id) is not provided.
        type: int
    region:
        description:
            - Slug of the volume region.
        type: str
    target_server_id:
        description:
            - ID of the server that the volume is attached to.
        type: int

extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get a storage volume by ID
  local.cherryservers.storage_info:
    auth_token: "{{ auth_token }}"
    id: 123456
  register: result

- name: Get all project storage volumes
  local.cherryservers.storage_info:
    auth_token: "{{ auth_token }}"
    project_id: 123456
  register: result

- name: Get all project storage volumes, that are detached and have test description
  local.cherryservers.storage_info:
    auth_token: "{{ auth_token }}"
    project_id: 123456
    state: "detached"
    description: "test"
  register: result
"""

RETURN = r"""
cherryservers_storages:
  description: EBS storage volume data.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: EBS volume ID.
      returned: always
      type: int
      sample: 123456
    region:
      description: Slug of the region that the EBS volume belongs to.
      returned: always
      type: str
      sample: "eu_nord_1"
    size:
      description: Size of the volume, in GB.
      returned: always
      type: int
      sample: 100
    description:
      description: User defined volume description.
      returned: if exists
      type: str
      sample: "my storage"
    target_server_id:
      description: ID of the server that the volume is attached to.
      returned: if exists
      type: int
      sample: 123456
    vlan_id:
      description: ID of the EBS volume VLAN.
      returned: if exists
      type: str
      sample: "1234"
    vlan_ip:
      description: IP address of the EBS volume VLAN.
      returned: if exists
      type: str
      sample: "10.168.143.200"
    initiator:
      description: EBS volume initiator.
      returned: if exists
      type: str
      sample: "iqn.2019-03.com.cherryservers:initiator-123456-123456"
    portal_ip:
      description: EBS volume portal/discovery IP address.
      returned: if exists
      type: str
      sample: "10.168.143.200"
    name:
      description: EBS volume name.
      returned: always
      type: str
      sample: "cs-volume-123456-123456"
    state:
      description: EBS volume state. Can be 'attached' or 'detached'.
      returned: always
      type: str
      sample: "detached"
"""

from typing import List, Optional
from ansible.module_utils import basic as utils
from ..module_utils import info_module
from ..module_utils.resource_managers.storage_manager import StorageManager


class StorageInfoModule(info_module.InfoModule):
    """Storage info module."""

    def __init__(self):
        super().__init__()
        self._resource_manager = StorageManager(self._module)

    def _filter(self, resource: dict) -> bool:
        params = self._module.params
        if all(
            params[k] is None or params[k] == resource[k]
            for k in ["id", "description", "region", "target_server_id", "state"]
        ):
            return True
        return False

    def _get_resource_list(self) -> List[dict]:
        return self._resource_manager.get_by_project_id(
            self._module.params["project_id"]
        )

    def _get_single_resource(self) -> Optional[dict]:
        return self._resource_manager.get_by_id(self._module.params["id"])

    def _resource_uniquely_identifiable(self) -> bool:
        if self._module.params["id"] is None:
            return False
        return True

    @property
    def name(self) -> str:
        """Storage resource name."""
        return "cherryservers_storages"

    @property
    def _arg_spec(self) -> dict:
        return {
            "state": {
                "choices": ["attached", "detached"],
                "type": "str",
            },
            "region": {"type": "str"},
            "id": {"type": "int"},
            "description": {"type": "str"},
            "project_id": {"type": "int"},
            "target_server_id": {"type": "int"},
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
            required_one_of=[("project_id", "id")],
        )


def main():
    """Main function."""
    StorageInfoModule().run()


if __name__ == "__main__":
    main()
