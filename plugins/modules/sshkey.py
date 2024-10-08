#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: sshkey

short_description: Create and manage SSH keys on Cherry Servers

version_added: "0.1.0"

description:
    - Create, update and delete SSH keys on Cherry Servers.
    - The module will attempt to find a key, that matches the provided options.
    - If multiple matching keys are found, the module fails.
    - Otherwise, depending on O(state) and if the key was found or not,
      it will be updated, deleted or a new key will be created.

options:
    state:
        description:
            - SSH key state.
        default: present
        choices: ['absent', 'present']
        type: str
    key:
        description:
            - Public SSH key.
            - Required if the key doesn't exist.
        type: str
    label:
        description:
            - SSH key label.
            - Required if the key doesn't exist.
        type: str
    id:
        description:
            - SSH key ID.
            - Ignored if O(state=present) and the key doesn't exist.
        type: int
    fingerprint:
        description:
            - SSH key fingerprint.
            - Ignored if O(state=present) and the key doesn't exist.
        type: str


extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create SSH key
  cherryservers.cloud.sshkey:
    auth_token: "{{ auth_token }}"
    label: "SSH-test-key"
    key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBYe+GfpsnLP02tfLOJWWFnGKJNpgrzLYE5VZhclrFy0 example@example.com"
    state: present
  register: result

- name: Update SSH key
  cherryservers.cloud.sshkey:
    auth_token: "{{ auth_token }}"
    label: "SSH-test-key-updated"
    id: "{{ result.cherryservers_sshkey.id }}"
    state: present

- name: Delete SSH key
  cherryservers.cloud.sshkey:
    auth_token: "{{ auth_token }}"
    label: "SSH-test-key-updated"
    state: absent
"""

RETURN = r"""
cherryservers_sshkey:
    description: SSH key data.
    returned: when O(state=present) and not in check mode
    type: dict
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

from typing import Optional
from ansible.module_utils import basic as utils
from ..module_utils import standard_module
from ..module_utils.resource_managers import sshkey_manager


class SSHKeyModule(standard_module.StandardModule):
    """Cherry Servers SSH key module."""

    def __init__(self):
        super().__init__()
        self._sshkey_manager = sshkey_manager.SSHKeyManager(self._module)

    def _get_resource(self) -> Optional[dict]:
        keys = self._sshkey_manager.get_all()

        current_key = None
        for key in keys:
            if any(
                self._module.params[k] is not None and self._module.params[k] == key[k]
                for k in ("fingerprint", "id", "label", "key")
            ):
                if current_key is not None:
                    self._module.fail_json(msg="error, multiple matching keys found")
                current_key = key

        return current_key

    def _perform_deletion(self, resource: dict):
        self._sshkey_manager.delete(resource["id"])

    def _perform_update(self, requests: dict, resource: dict) -> dict:
        if requests.get("update", None):
            self._sshkey_manager.update(resource["id"], requests["update"])

        return self._sshkey_manager.get_by_id(resource["id"])

    def _validate_creation_params(self):
        if self._module.params["label"] is None or self._module.params["key"] is None:
            self._module.fail_json("label and key are required for creating SSH keys.")

    def _get_update_requests(self, resource: dict) -> dict:
        req = {}
        params = self._module.params

        for k in ("label", "key"):
            if params[k] is not None and params[k] != resource[k]:
                req[k] = params[k]

        if req:
            return {"update": req}
        return {}

    def _perform_creation(self) -> dict:
        key = self._sshkey_manager.create(
            params={
                "label": self._module.params["label"],
                "key": self._module.params["key"],
            }
        )

        return self._sshkey_manager.get_by_id(key["id"])

    @property
    def name(self) -> str:
        """Cherry Servers SSH key module name."""
        return "cherryservers_sshkey"

    @property
    def _arg_spec(self) -> dict:
        return {
            "state": {
                "choices": ["absent", "present"],
                "default": "present",
                "type": "str",
            },
            "label": {
                "type": "str",
            },
            "key": {
                "type": "str",
                "no_log": False,
            },
            "id": {"type": "int"},
            "fingerprint": {"type": "str"},
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
        )


def main():
    """Main function."""
    SSHKeyModule().run()


if __name__ == "__main__":
    main()
