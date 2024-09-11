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

from typing import Optional, Tuple
from ansible.module_utils import basic as utils
from ..module_utils import client
from ..module_utils import common
from ..module_utils import constants
from ..module_utils import normalizers


def run_module():
    """Execute the ansible module."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ["id"], True),
        ],
    )

    api_client = client.CherryServersClient(module)

    if module.params["state"] == "absent":
        absent_state(api_client, module)
    elif module.params["id"]:
        update_state(api_client, module)
    else:
        creation_state(api_client, module)


def creation_state(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Execute creation state logic."""
    params = module.params

    if any(params[k] is None for k in ["project_id", "region", "size"]):
        module.fail_json(
            "project_id, region and size are required parameters for storage volume creation"
        )

    attach_param_validation(module)

    if module.check_mode:
        module.exit_json(changed=True)

    status, resp = api_client.send_request(
        "POST",
        f"projects/{params['project_id']}/storages",
        constants.STORAGE_TIMEOUT,
        region=params["region"],
        size=params["size"],
        description=params["description"],
    )

    if status != 201:
        module.fail_json(msg=f"Failed to create storage volume: {resp}")

    if params["state"] == "attached":
        attach_storage(api_client, module, resp["id"])

    # We need to do another GET request, because the object returned from POST
    # doesn't contain all the necessary data.

    storage_volume = get_storage(api_client, module, resp["id"])
    module.exit_json(changed=True, cherryservers_storage=storage_volume)


def attach_param_validation(module: utils.AnsibleModule):
    """Validate that all server attachment parameters are set correctly.

    Fails the module if they are not set correctly.
    """
    params = module.params
    if params["state"] == "attached" and params["target_server_id"] is None:
        module.fail_json("target_server_id is required if state is attached")

    if params["state"] == "detached" and params["target_server_id"]:
        module.fail_json("can't use target_server_id with detached storage state")


def attach_storage(
    api_client: client.CherryServersClient,
    module: utils.AnsibleModule,
    storage_id: int,
):
    """Attach storage volume to server.

    Fail the module if attachment fails.
    """
    status, resp = api_client.send_request(
        "POST",
        f"storages/{storage_id}/attachments",
        constants.STORAGE_TIMEOUT,
        attach_to=module.params["target_server_id"],
    )

    if status != 201:
        module.fail_json(msg=f"Failed to attach storage volume: {resp}")


def detach_storage(
    api_client: client.CherryServersClient, module: utils.AnsibleModule, storage_id: int
):
    """Detach storage volume from server."""
    status, resp = api_client.send_request(
        "DELETE",
        f"storages/{storage_id}/attachments",
        constants.STORAGE_TIMEOUT,
    )

    if status != 204:
        module.fail_json(msg=f"Failed to detach storage volume: {resp}")


def absent_state(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Execute deletion state logic."""
    storage = get_storage(api_client, module, module.params["id"])
    if storage:
        if module.check_mode:
            module.exit_json(changed=True)
        delete_storage(api_client, module, storage)
        module.exit_json(changed=True)
    else:
        module.exit_json(changed=False)


def get_storage(
    api_client: client.CherryServersClient, module: utils.AnsibleModule, storage_id: str
) -> Optional[dict]:
    """Retrieve a normalized Cherry Servers storage volume resource."""
    url = f"storages/{storage_id}"
    status, resp = api_client.send_request(
        "GET",
        url,
        constants.STORAGE_TIMEOUT,
    )

    if status not in (200, 404):
        module.fail_json(msg=f"Error getting storage volume: {resp}")
    if status == 200:
        return normalizers.normalize_storage(resp)
    return None


def update_state(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Execute update state logic."""
    storage = get_storage(api_client, module, module.params["id"])
    if storage is None:
        module.fail_json(
            msg=f"Failed to get storage volume with id: {module.params['id']}"
        )

    req, changed = get_update_request(module.params, storage)
    attach_required = False

    if module.params["state"] == "attached":
        if (
            module.params["target_server_id"] is not None
            and storage["target_server_id"] != module.params["target_server_id"]
        ):
            changed = True
            attach_required = True
        elif (
            module.params["target_server_id"] is None
            and storage["target_server_id"] is None
        ):
            module.fail_json("target_server_id is required if state is attached")
    elif module.params["state"] == "detached":
        if module.params["target_server_id"] is not None:
            module.fail_json("can't use target_server_id with detached storage state")
        if storage["target_server_id"] is not None:
            changed = True

    if module.check_mode:
        if changed:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)
    else:
        if not changed:
            module.exit_json(changed=False, cherryservers_storage=storage)

    if module.params["state"] == "detached" and storage["target_server_id"] is not None:
        detach_storage(api_client, module, storage["id"])
    if attach_required:
        if storage["target_server_id"] is not None:
            detach_storage(api_client, module, storage["id"])
        attach_storage(api_client, module, storage["id"])

    status, resp = api_client.send_request(
        "PUT", f"storages/{storage['id']}", constants.STORAGE_TIMEOUT, **req
    )
    if status != 201:
        module.fail_json(msg=f"Failed to update storage volume: {resp}")

    storage = get_storage(api_client, module, storage["id"])
    module.exit_json(changed=True, cherryservers_storage=storage)


def delete_storage(
    api_client: client.CherryServersClient, module: utils.AnsibleModule, storage: dict
):
    """Delete a storage volume."""
    if storage["target_server_id"]:
        detach_storage(api_client, module, storage["id"])

    status, resp = api_client.send_request(
        "DELETE", f"storages/{module.params['id']}", constants.STORAGE_TIMEOUT
    )
    if status != 204:
        module.fail_json(msg=f"Failed to delete storage volume: {resp}")

    module.exit_json(changed=True)


def get_update_request(params: dict, storage: dict) -> Tuple[dict, bool]:
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

    for k in ["size", "description"]:
        if params[k] is not None and params[k] != storage[k]:
            changed = True
            req[k] = params[k]

    return req, changed


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
    run_module()


if __name__ == "__main__":
    main()
