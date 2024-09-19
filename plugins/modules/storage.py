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
            - The state of the volume.
            - Attaching and detaching volumes requires additional manual server configuration,
            - see Cherry Servers EBS documentation for detailed instructions.
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
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create a detached storage volume
  local.cherryservers.storage:
    state: "detached"
    project_id: 213668
    region: "eu_nord_1"
    size: 1
  register: result

- name: Create an attached storage volume
  local.cherryservers.storage:
    project_id: 213668
    region: "eu_nord_1"
    size: 1
    target_server_id: 596908
  register: result

- name: Delete a storage volume
  local.cherryservers.storage:
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

from typing import Optional, Tuple, Any
from ansible.module_utils import basic as utils
from ..module_utils import client, common, normalizers, base_module


class StorageModule(base_module.BaseModule):
    """TODO"""

    timeout = 20

    @property
    def name(self) -> str:
        """TODO"""
        return """cherryservers_storage"""

    def _attach_storage(self, target_server_id: int):
        """Attach storage volume to server.

        Fail the module if attachment fails.
        """
        status, resp = self._api_client.send_request(
            "POST",
            f"storages/{self.resource['id']}/attachments",
            self.timeout,
            attach_to=target_server_id,
        )

        if status != 201:
            self._module.fail_json(
                msg=f"error {status}, failed to attach {self.name}: {resp}"
            )

    def _detach_storage(self):
        """Detach storage volume from server."""
        status, resp = self._api_client.send_request(
            "DELETE",
            f"storages/{self.resource['id']}/attachments",
            self.timeout,
        )

        if status != 204:
            self._module.fail_json(
                msg=f"error {status}, failed to detach {self.name}: {resp}"
            )

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_storage(resource)

    def _create(self):
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

        if self._module.check_mode:
            self._module.exit_json(changed=True)

        status, resp = self._api_client.send_request(
            "POST",
            f"projects/{params['project_id']}/storages",
            self.timeout,
            region=params["region"],
            size=params["size"],
            description=params["description"],
        )

        if status != 201:
            self._module.fail_json(
                msg=f"error {status}, failed to create {self.name}: {resp}"
            )

        self.resource = resp

        if params["state"] == "attached":
            self._attach_storage(self._module.params["target_server_id"])

        self._exit_with_return()

    def _update(self):
        """Execute update state logic."""

        req, resize_changed = self._get_resize_update_request()
        detach_required = False
        attach_required = False

        params = self._module.params

        if params["state"] == "detached" and params["target_server_id"] is not None:
            self._module.fail_json(
                msg="can't use target_server_id with detached storage state"
            )

        if (
            params["target_server_id"] is not None
            and params["target_server_id"] != self.resource["target_server_id"]
        ):
            attach_required = True

        if self.resource["state"] == "attached":
            if attach_required or params["state"] == "detached":
                detach_required = True

        changed = resize_changed or detach_required or attach_required
        self._exit_if_no_change_for_update(changed)

        if detach_required:
            self._detach_storage()
        if attach_required:
            self._attach_storage(self._module.params["target_server_id"])

        if resize_changed:
            status, resp = self._api_client.send_request(
                "PUT", f"storages/{self.resource['id']}", self.timeout, **req
            )
            if status != 201:
                self._module.fail_json(
                    msg=f"error {status}, failed to resize {self.name}: {resp}"
                )

            self.resource = resp

        self._exit_with_return()

    def _get_resize_update_request(self) -> Tuple[dict, bool]:
        """Get Cherry Servers storage volume update API request.

        Check for differences between current volume state and module options
        and add the options that have diverged to the update request.

        Returns:
            Tuple[dict, bool]: A dictionary with the request parameters
            and a boolean indicating whether there is any difference between the volume state
            and module options.
        """
        req = {}
        changed = False
        params = self._module.params

        for k in ["size", "description"]:
            if params[k] is not None and params[k] != self.resource[k]:
                changed = True
                req[k] = params[k]

        return req, changed

    def _delete(self):
        self._exit_if_no_change_for_delete()

        if self.resource["state"] == "attached":
            self._detach_storage()

        status, resp = self._api_client.send_request(
            "DELETE", f"storages/{self.resource['id']}", self.timeout
        )
        if status != 204:
            self._module.fail_json(
                msg=f"error {status}, failed to delete {self.name}: {resp}"
            )

        self._module.exit_json(changed=True)

    def _read_by_id(self, resource_id: Any) -> Optional[dict]:
        status, resp = self._api_client.send_request(
            "GET",
            f"storages/{resource_id}",
            self.timeout,
        )
        if status not in (200, 404):
            self._module.fail_json(msg=f"error {status} getting {self.name}: {resp}")
        if status == 200:
            return resp
        return None


def get_module_args() -> dict:
    """Return a dictionary with the modules argument specification."""
    module_args = common.get_base_argument_spec()

    module_args.update(
        {
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
    )

    return module_args


def main():
    """Main function."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ["id"], True),
        ],
    )

    api_client = client.CherryServersClient(module)
    storage_module = StorageModule(module, api_client)
    storage_module.run()


if __name__ == "__main__":
    main()
