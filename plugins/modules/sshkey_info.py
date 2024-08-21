#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: sshkey_info

short_description: Gather information about your Cherry Servers SSH keys

version_added: "0.1.0"

description:
  - Gather information about your Cherry Servers SSH keys.
  - Returns SSH keys that match all of your provided options.
  - If you provide no options, returns all your SSH keys.

options:
    key:
        description:
            - The public SSH key.
        type: str
    label:
        description:
            - The label of the SSH key.
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


extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get SSH key by ID
  local.cherryservers.sshkey_info:
    auth_token: "{{ auth_token }}"
    id: 0000
  register: result
"""

RETURN = r"""
cherryservers_sshkeys:
  description: SSH key data.
  returned: always
  type: list
  elements: dict
  contains:
    created:
      description: Timestamp of key creation.
      returned: always
      type: str
      sample: "2024-08-06T07:56:16+00:00"
    fingerprint:
      description: SSH key fingerprint.
      returned: always
      type: str
      sample: "54:8e:84:11:bb:29:59:41:36:cb:e2:k2:0c:4a:77:1d"
    href:
      description: SSH key href.
      returned: always
      type: str
      sample: /ssh-keys/7955
    id:
      description: SSH key ID.
      returned: always
      type: int
      sample: 7955
    key:
      description: Public SSH key.
      returned: always
      type: str
      sample: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBYe+GfpsnLP02tfLOJWWFnGKJNpgrzLYE5VZhclrFy0 example@example.com
    label:
      description: SSH key label.
      returned: always
      type: str
      sample: my-label
    updated:
      description: Timestamp of last key update.
      returned: always
      type: str
      sample: "2024-08-06T07:56:16+00:00"
"""

from ansible.module_utils import basic as utils
from ..module_utils import client
from ..module_utils import common
from ..module_utils import constants


def run_module():
    """Execute the ansible module."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    api_client = client.CherryServersClient(module)

    status, resp = api_client.send_request(
        "GET",
        "ssh-keys",
        constants.SSH_TIMEOUT,
    )
    if status != 200:
        module.fail_json(msg=f"Failed to get SSH keys: {resp}")

    temp_keys = []

    for key in resp:
        if sshkey_filter(module.params, key):
            temp_keys.append(key)

    resp = temp_keys

    # We delete 'user' from the response because of an API peculiarity:
    # each returned SSH key contains a `user` field, that
    # contains all the SSH keys the user has. This results in significant duplication.

    for key in resp:
        del key["user"]

    module.exit_json(changed=False, cherryservers_sshkeys=resp)


def get_module_args() -> dict:
    """Return a dictionary with the modules argument specification."""
    module_args = common.get_base_argument_spec()

    module_args.update(
        {
            "label": {
                "type": "str",
                "aliases": ["name"],
            },
            "key": {
                "type": "str",
                "no_log": False,
            },
            "id": {"type": "int"},
            "fingerprint": {"type": "str"},
        }
    )

    return module_args


def sshkey_filter(module_params: dict, sshkey: dict) -> bool:
    """Check if the key should be included in the response."""
    return all(
        module_params[k] is None or sshkey[k] == module_params[k]
        for k in ("id", "fingerprint", "label", "key")
    )


def main():
    """Main function."""
    run_module()


if __name__ == "__main__":
    main()
