#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: floating_ip_info

short_description: Gather information about your Cherry Servers floating IPs

version_added: "0.1.0"

description:
  - Gather information about your Cherry Servers floating IPs.
  - Returns floating IPs that match all your provided options in the given project.
  - Alternatively, you can gather information directly by floating IP ID, all other arguments will be ignored.

options:
    id:
        description:
            - ID of the floating IP.
            - Required if O(project_id) is not provided.
        type: str
    address:
        description:
            - IP address of the floating IP.
        type: str
    project_id:
        description:
            - ID of the project the floating IP belongs to.
            - Required if O(id) is not provided.
        type: int
    tags:
        description:
            - Tags of the floating IP.
        type: dict
    region:
        description:
            - Slug of the floating IP region.
        type: str
    target_server_id:
        description:
            - ID of the server to which the floating IP is attached.
        type: int

extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get single floating IP
  cherryservers.cloud.floating_ip_info:
    auth_token: "{{ auth_token }}"
    id: "497f6eca-6276-4993-bfeb-53cbbbba6f08"
  register: result

- name: Get all project floating IPs
  cherryservers.cloud.floating_ip_info:
    auth_token: "{{ auth_token }}"
    project_id: 123456
  register: result

- name: 'Get all floating IPs in the EU Nord-1 region, that have the env: dev tag'
  cherryservers.cloud.floating_ip_info:
    auth_token: "{{ auth_token }}"
    region: "eu_nord_1"
    project_id: 123456
    tags:
      env: "dev"
  register: result
"""

RETURN = r"""
cherryservers_floating_ips:
  description: Floating IP data.
  returned: always
  type: list
  elements: dict
  contains:
    a_record:
      description: DNS A record.
      returned: if exists
      type: str
      sample: "test.cloud.cherryservers.net."
    address:
      description: IP address.
      returned: always
      type: str
      sample: "5.199.174.84"
    cidr:
      description: CIDR notation.
      returned: always
      type: str
      sample: "5.199.174.84/32"
    id:
      description: ID of the IP address.
      returned: always
      type: str
      sample: "a0ff92c9-21f6-c387-33d0-5c941c0435f0"
    ptr_record:
      description: DNS pointer record.
      returned: if exists
      type: str
      sample: "test."
    region:
      description: Slug of the region which the IP belongs to.
      returned: always
      type: str
      sample: "eu_nord_1"
    tags:
      description: Tags of the floating IP.
      returned: always
      type: dict
      sample:
        env: "dev"
    target_server_id:
      description: ID of the server to which the floating IP is targeted to.
      returned: if exists
      type: int
      sample: 123456
    route_ip_id:
      description: ID of the IP to which the floating IP is routed to.
      returned: if exists
      type: str
      sample: "fe8b01f4-2b85-eae9-cbfb-3288c507f318"
    project_id:
      description: Cherry Servers project ID, associated with the floating IP.
      returned: always
      type: int
      sample: 123456
    type:
      description: Type of the IP. Should always be 'floating-ip'
      returned: always
      type: str
      sample: "floating-ip"
"""

from typing import List, Optional
from ansible.module_utils import basic as utils
from ..module_utils.resource_managers import floating_ip_manager
from ..module_utils import info_module


class FloatingIPModule(info_module.InfoModule):
    """Floating IP info module"""

    def __init__(self):
        super().__init__()
        self._resource_manager = floating_ip_manager.FloatingIPManager(self._module)

    def _filter(self, resource: dict) -> bool:
        params = self._module.params

        if resource["type"] != "floating-ip":
            return False

        if all(
            params[k] is None or params[k] == resource[k]
            for k in ["id", "address", "project_id", "region", "target_server_id"]
        ) and (
            params["tags"] is None
            or all(params["tags"][k] == resource["tags"].get(k) for k in params["tags"])
        ):
            return True
        return False

    def _resource_uniquely_identifiable(self) -> bool:
        if self._module.params.get("id") is None:
            return False
        return True

    def _get_single_resource(self) -> Optional[dict]:
        return self._resource_manager.get_by_id(self._module.params.get("id"))

    def _get_resource_list(self) -> List[dict]:
        return self._resource_manager.get_by_project_id(
            self._module.params.get("project_id")
        )

    @property
    def name(self) -> str:
        """Cherry Servers resource name."""
        return "cherryservers_floating_ips"

    @property
    def _arg_spec(self) -> dict:
        return {
            "tags": {
                "type": "dict",
            },
            "region": {"type": "str"},
            "id": {"type": "str"},
            "address": {"type": "str"},
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
    FloatingIPModule().run()


if __name__ == "__main__":
    main()
