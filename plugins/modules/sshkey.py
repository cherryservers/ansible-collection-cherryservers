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
    - it will be updated, deleted or a new key will be created.

options:
    state:
        description:
            - The state of the SSH key.
        default: present
        choices: ['absent', 'present']
        type: str
    key:
        description:
            - The public SSH key.
            - Required if the key doesn't exist.
        type: str
    label:
        description:
            - The label of the SSH key.
            - Required if the key doesn't exist.
        type: str
    id:
        description:
            - The ID of the SSH key.
            - Ignored if O(state=present) and the key doesn't exist.
        type: int
    fingerprint:
        description:
            - The fingerprint of the SSH key.
            - Ignored if O(state=present) and the key doesn't exist.
        type: str


extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create SSH key
  local.cherryservers.sshkey:
    auth_token: "{{ auth_token }}"
    label: "SSH-test-key"
    key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBYe+GfpsnLP02tfLOJWWFnGKJNpgrzLYE5VZhclrFy0 example@example.com"
    state: present
  register: result

- name: Update SSH key
  local.cherryservers.sshkey:
    auth_token: "{{ auth_token }}"
    label: "SSH-test-key-updated"
    id: "{{ result.cherryservers_sshkey.id }}"
    state: present

- name: Delete SSH key
  local.cherryservers.sshkey:
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

from ansible.module_utils import basic as utils
from typing import Any, Optional, Tuple
from ..module_utils import client, common, normalizers, base_module


class SSHKeyModule(base_module.BaseModule):
    """TODO"""

    timeout = 10

    @property
    def name(self) -> str:
        """TODO"""
        return "cherryservers_sshkey"

    def _load_resource(self):
        """TODO"""
        status, resp = self._api_client.send_request("GET", "ssh-keys", self.timeout)
        if status != 200:
            self._module.fail_json(
                msg=f"error {status}, failed to get {self.name}: {resp}"
            )

        current_key = None
        for key in resp:
            if any(
                self._module.params[k] is not None and self._module.params[k] == key[k]
                for k in ("fingerprint", "id", "label", "key")
            ):
                if current_key is not None:
                    self._module.fail_json(msg="error, multiple matching keys found")
                current_key = key

        self.resource = current_key

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_ssh_key(resource)

    def _update(self):
        req, changed = self._get_update_request()

        self._exit_if_no_change_for_update(changed)

        status, resp = self._api_client.send_request(
            "PUT", f"ssh-keys/{self.resource['id']}", self.timeout, **req
        )
        if status != 201:
            self._module.fail_json(
                msg=f"error {status}, failed to update {self.name}: {resp}"
            )

        self.resource = resp
        self._exit_with_return()

    def _delete(self):
        self._exit_if_no_change_for_delete()

        status, resp = self._api_client.send_request(
            "DELETE", f"ssh-keys/{self.resource['id']}", self.timeout
        )
        if status != 204:
            self._module.fail_json(
                msg=f"error {status}, failed to delete {self.name}: {resp}"
            )

        self._module.exit_json(changed=True)

    def _read_by_id(self, resource_id: Any) -> Optional[dict]:
        status, resp = self._api_client.send_request(
            "GET",
            f"ssh-keys/{resource_id}",
            self.timeout,
        )
        if status not in (200, 404):
            self._module.fail_json(msg=f"error {status} getting {self.name}: {resp}")
        if status == 200:
            return resp
        return None

    def _create(self):
        if self._module.params["label"] is None or self._module.params["key"] is None:
            self._module.fail_json("label and key are required for creating SSH keys.")

        if self._module.check_mode:
            self._module.exit_json(changed=True)

        status, resp = self._api_client.send_request(
            "POST",
            "ssh-keys",
            self.timeout,
            label=self._module.params["label"],
            key=self._module.params["key"],
        )
        if status != 201:
            self._module.fail_json(
                msg=f"error {status}, failed to create {self.name}: {resp}"
            )

        self.resource = resp
        self._exit_with_return()

    def _get_update_request(self) -> Tuple[dict, bool]:
        """Generate the necessary update request data fields."""
        req = {}
        changed = False
        params = self._module.params

        for k in ("label", "key"):
            if params[k] is not None and params[k] != self.resource[k]:
                changed = True
                req[k] = params[k]

        return req, changed


def get_module_args() -> dict:
    """Return a dictionary with the modules argument specification."""
    module_args = common.get_base_argument_spec()

    module_args.update(
        {
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
    )

    return module_args


def main():
    """Main function."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    api_client = client.CherryServersClient(module)
    ssh_key_module = SSHKeyModule(module, api_client)
    ssh_key_module.run()


if __name__ == "__main__":
    main()
