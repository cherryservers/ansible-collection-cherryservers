#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: storage

short_description: Create and manage elastic block storage volumes on Cherry Servers

version_added: "0.1.0"

description:
    - Create, update and delete elastic block storage volumes on Cherry Servers.
    - If you want to manage an existing volume, set O(id) along with state and other desired options.
    - EBS is currently only available in the EU-Nord-1 region and only for dedicated servers.

options:
    state:
        description:
            - Volume state.
            - Attaching and detaching volumes requires additional manual server configuration,
              see Cherry Servers EBS documentation for detailed instructions.
        choices: ['attached', 'detached', 'absent']
        type: str
        default: attached
    id:
        description:
            - ID of the volume.
            - Used to identify existing volumes.
            - Required if volume exists.
        type: int
    project_id:
        description:
            - ID of the project the volume belongs to.
            - Required if volume doesn't exist.
            - Cannot be set for an existing volume.
        type: int
    region:
        description:
            - Slug of the volume region.
            - Required if volume doesn't exist.
            - Cannot be set for an existing volume.
        type: str
    size:
        description:
            - Size of the volume, in GB.
            - Required if volume doesn't exist.
            - Volume size can't be downgraded. After resizing, a new volume ID will be set.
        type: int
    description:
        description:
            - Volume description.
        type: str
    target_server_id:
        description:
            - ID of the server that the volume is attached to.
            - Required if O(state=attached) and volume doesn't exist.
        type: int

seealso:
    - name: Cherry Servers EBS documentation.
      description: Cherry Servers EBS documentation.
      link: https://docs.cherryservers.com/knowledge/elastic-block-storage

extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create a detached storage volume
  cherryservers.cloud.storage:
    state: "detached"
    project_id: 213668
    region: "eu_nord_1"
    size: 1
  register: result

- name: Create an attached storage volume
  cherryservers.cloud.storage:
    project_id: 213668
    region: "eu_nord_1"
    size: 1
    target_server_id: 596908
  register: result

- name: Delete a storage volume
  cherryservers.cloud.storage:
    id: 596944
    state: "absent"
  register: result
"""

RETURN = r"""
cherryservers_storage:
  description: Elastic block storage volume data.
  returned: O(state=present) and not in check mode
  type: dict
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

from typing import Optional
from ansible.module_utils import basic as utils
from ..module_utils import standard_module
from ..module_utils.resource_managers import storage_manager


class StorageModule(standard_module.StandardModule):
    """Cherry Servers module for managing EBS resources."""

    def __init__(self):
        super().__init__()
        self._storage_manager = storage_manager.StorageManager(self._module)

    def _get_resource(self) -> Optional[dict]:
        if self._module.params["id"]:
            return self._storage_manager.get_by_id(self._module.params["id"])
        return None

    def _perform_deletion(self, resource: dict):
        if resource["state"] == "attached":
            self._storage_manager.detach(resource["id"])

        self._storage_manager.delete(resource["id"])

    def _get_update_requests(self, resource: dict) -> dict:
        resize_req = {}
        req = {}
        params = self._module.params
        attach_required = False

        for k in ["size", "description"]:
            if params[k] is not None and params[k] != resource[k]:
                resize_req[k] = params[k]

        if resize_req:
            req["resize"] = resize_req

        if params["state"] == "detached" and params["target_server_id"] is not None:
            self._module.fail_json(
                msg="can't use target_server_id with detached storage state"
            )

        if (
            params["target_server_id"] is not None
            and params["target_server_id"] != resource["target_server_id"]
        ):
            attach_required = True
            req["attach"] = {"target_server_id": params["target_server_id"]}

        if resource["state"] == "attached":
            if attach_required or params["state"] == "detached":
                req["detach"] = {"detach": True}

        return req

    def _perform_update(self, requests: dict, resource: dict) -> dict:

        if requests.get("detach", None):
            self._storage_manager.detach(resource["id"])
        if requests.get("attach", None):
            self._storage_manager.attach(
                resource["id"], requests["attach"]["target_server_id"]
            )
        if requests.get("resize", None):
            # We return here, because on update the storage changes ID, thus is inaccessible.
            return self._storage_manager.update(resource["id"], requests["resize"])

        return self._storage_manager.get_by_id(resource["id"])

    def _validate_creation_params(self):
        params = self._module.params
        if any(params[k] is None for k in ["project_id", "region", "size"]):
            self._module.fail_json(
                "project_id, region and size are required parameters for storage volume creation"
            )

        if params["state"] == "attached" and params["target_server_id"] is None:
            self._module.fail_json("target_server_id is required if state is attached")

        if params["state"] == "detached" and params["target_server_id"]:
            self._module.fail_json(
                "can't use target_server_id with detached storage state"
            )

    def _perform_creation(self) -> dict:
        params = self._module.params

        storage = self._storage_manager.create(
            project_id=params["project_id"],
            params={
                "region": params["region"],
                "size": params["size"],
                "description": params["description"],
            },
        )

        if params["state"] == "attached":
            self._storage_manager.attach(storage["id"], params["target_server_id"])

        return self._storage_manager.get_by_id(storage["id"])

    @property
    def name(self) -> str:
        """Cherry Servers storage volume name."""
        return "cherryservers_storage"

    @property
    def _arg_spec(self) -> dict:
        return {
            "state": {
                "choices": ["attached", "detached", "absent"],
                "default": "attached",
                "type": "str",
            },
            "id": {"type": "int"},
            "project_id": {"type": "int"},
            "region": {"type": "str"},
            "size": {"type": "int"},
            "description": {"type": "str"},
            "target_server_id": {"type": "int"},
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
            required_if=[
                ("state", "absent", ["id"], True),
            ],
        )


def main():
    """Main function."""
    StorageModule().run()


if __name__ == "__main__":
    main()
