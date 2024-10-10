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

version_added: "1.0.0"

description:
  - Gather information about your Cherry Servers SSH keys.
  - Set O(id) to get a specific key (all other arguments are ignored).
  - You can also search for SSH keys that match all of your provided arguments, except O(id).

options:
    key:
        description:
            - Public SSH key.
        type: str
    label:
        description:
            - SSH key label.
        aliases: [name]
        type: str
    id:
        description:
            - SSH key ID.
            - Set this to get a specific key (all other arguments are ignored).
        type: int
    fingerprint:
        description:
            - SSH key fingerprint.
        type: str


extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get SSH key by ID
  cherryservers.cloud.sshkey_info:
    auth_token: "{{ auth_token }}"
    id: 0000
  register: result

- name: Get SSH key by label
  cherryservers.cloud.sshkey_info:
    auth_token: "{{ auth_token }}"
    label: "my-key"
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
from typing import List, Optional
from ansible.module_utils import basic as utils
from ..module_utils import info_module
from ..module_utils.resource_managers import sshkey_manager


class SSHKeyInfoModule(info_module.InfoModule):
    """SSH key info module."""

    def __init__(self):
        super().__init__()
        self._resource_manager = sshkey_manager.SSHKeyManager(self._module)

    def _resource_uniquely_identifiable(self) -> bool:
        if self._module.params.get("id") is None:
            return False
        return True

    def _filter(self, resource: dict) -> bool:
        params = self._module.params
        return all(
            params[k] is None or resource[k] == params[k]
            for k in ("id", "fingerprint", "label", "key")
        )

    def _get_single_resource(self) -> Optional[dict]:
        return self._resource_manager.get_by_id(self._module.params["id"])

    def _get_resource_list(self) -> List[dict]:
        return self._resource_manager.get_all()

    @property
    def name(self) -> str:
        """SSH key info module name."""
        return "cherryservers_sshkeys"

    @property
    def _arg_spec(self) -> dict:
        return {
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

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
        )


def main():
    """Main function."""
    SSHKeyInfoModule().run()


if __name__ == "__main__":
    main()
