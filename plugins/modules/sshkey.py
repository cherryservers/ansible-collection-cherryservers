#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: sshkey

short_description: Create and manage SSH keys on Cherry Servers.

version_added: "0.1.0"

description: Create, update and delete SSH keys on Cherry Servers.

options:
    auth_token:
        description:
            - API authentication token for Cherry Servers public API.
            - Can be supplied via E(CHERRY_AUTH_TOKEN) and E(CHERRY_AUTH_KEY) environment variables.
            - See https://portal.cherryservers.com/settings/api-keys for more information.
        type: str
    state:
        description:
            - The state of the SSH key.
            - If V(present) an attempt to find the key will be made.
            - If multiple keys matching the provided options are found, the module will fail.
            - If the key doesn't exist, O(label) and O(public_key) are required, all other options are ignored.
            - If V(absent) and multiple options are provided, all keys matching any of the options will be removed.
        default: present
        choices: ['absent', 'present']
        type: str
    public_key:
        description:
            - The public SSH key.
            - Required if the key doesn't exist.
        type: str
    label:
        description:
            - The label of the SSH key.
            - Required if the key doesn't exist.
        aliases: [name]
        type: str
    id:
        description:
            - The ID of the SSH key.
        type: int
    fingerprint:
        description:
            - The fingerprint of the SSH key.
        type: str

notes:
  - This module supports check mode.
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: "Create SSH key"
  local.cherryservers.sshkey:
    auth_token: "{{ auth_token }}"
    name: "SSH test key"
    public_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBYe+GfpsnLP02tfLOJWWFnGKJNpgrzLYE5VZhclrFy0 example@example.com"
    state: present
  register: result
"""

RETURN = r"""
cherryservers_sshkey:
    description: SSH key data.
    returned: when C(state=present)
    type: dict
    sample: {
        "cherryservers_sshkey": {
            "created": "2024-07-31T05:33:08+00:00",
            "fingerprint": "54:8e:84:11:bb:29:59:41:36:cb:e2:k2:0c:4a:77:1d",
            "href": "/ssh-keys/0000",
            "id": 0000,
            "key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBYe+GfpsnLP02tfLOJWWFnGKJNpgrzLYE5VZhclrFy0 example@example.com",
            "label": "ansible-test",
            "updated": "2024-07-31T05:33:08+00:00"
        }
    }
"""

from ansible.module_utils import basic as utils
from ..module_utils import client
from typing import List


def run_module():
    """Execute the ansible module."""

    module_args = {
        "auth_token": {
            "type": "str",
            "no_log": True,
            "fallback": (utils.env_fallback, ["CHERRY_AUTH_TOKEN", "CHERRY_AUTH_KEY"]),
        },
        "state": {
            "choices": ["absent", "present"],
            "default": "present",
            "type": "str",
        },
        "label": {
            "type": "str",
            "aliases": ["name"],
        },
        "public_key": {
            "type": "str",
        },
        "id": {"type": "int"},
        "fingerprint": {"type": "str"},
    }

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("label", "public_key"), True),
        ],
    )

    api_client = client.CherryServersClient(module)

    if module.params["state"] == "present":
        existing_keys = get_keys(api_client, module)
        if len(existing_keys) > 1:
            module.fail_json(msg="More than one SSH key matches the given parameters.")
        if existing_keys:
            update_key(api_client, module)
        else:
            create_key(api_client, module)
    elif module.params["state"] == "absent":
        delete_keys(api_client, module)


def get_keys(
    api_client: client.CherryServersClient, module: utils.AnsibleModule
) -> List[int]:
    """Search for and retrieve SSH keys that match the provided criteria.

    Returns:

            List[int]: IDs of SSH keys that match the modules argument_spec parameters.

    """
    params = module.params

    _1, resp = api_client.send_request(
        "GET",
        "ssh-keys",
    )

    matching_ids = []

    for sshkey in resp:
        if (
            any(sshkey[k] == params[k] for k in ["id", "fingerprint", "label"])
            or sshkey["key"] == params["public_key"]
        ):
            matching_ids.append(sshkey["id"])

    return matching_ids


def create_key(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Create a new SSH key."""
    if module.params["label"] is None or module.params["public_key"] is None:
        module.fail_json("Label and public key are required for creating SSH keys.")

    if module.check_mode:
        module.exit_json(changed=True)

    status, resp = api_client.send_request(
        "POST",
        "ssh-keys",
        label=module.params["label"],
        key=module.params["public_key"],
    )
    if status != 201:
        module.fail_json(msg=f"Failed to create SSH key: {resp}")
    module.exit_json(changed=True, cherryservers_sshkey=resp)


def update_key(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Update an existing SSH key."""
    if module.params["label"] is None and module.params["public_key"] is None:
        module.exit_json(changed=False)

    if module.check_mode:
        module.exit_json(changed=True)

    status, resp = api_client.send_request(
        "PUT",
        "ssh-keys",
        label=module.params["label"],
        key=module.params["public_key"],
    )
    if status != 201:
        module.fail_json(msg=f"Failed to update SSH key: {resp}")
    module.exit_json(changed=True, cherryservers_sshkey=resp)


def delete_keys(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Delete any SSH keys that match the modules argument_spec parameters."""
    if all(
        module.params[k] is None for k in ["id", "fingerprint", "label", "public_key"]
    ):
        module.exit_json(changed=False)

    ssh_ids_to_delete = get_keys(api_client, module)

    if module.check_mode and ssh_ids_to_delete:
        module.exit_json(changed=True)
    elif not ssh_ids_to_delete:
        module.exit_json(changed=False)

    failures = []
    for key_id in ssh_ids_to_delete:
        status, _2 = api_client.send_request(
            "DELETE",
            f"ssh-keys/{key_id}",
        )
        if status != 204:
            failures.append(f"Failed to delete SSH key: {key_id}")
    if failures:
        module.fail_json(changed=True, msg="\n".join(failures))
    module.exit_json(changed=True)


def main():
    """Main function."""
    run_module()


if __name__ == "__main__":
    main()
