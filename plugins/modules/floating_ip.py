#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: floating_ip

short_description: Create and manage floating IPs on Cherry Servers

version_added: "0.1.0"

description:
    - Create, update and delete floating IPs on Cherry Servers.
    - If you want to manage an existing floating IP, set O(id) along with state and other desired options.

options:
    state:
        description:
            - The state of the floating IP.
        choices: ['absent', 'present']
        type: str
        default: present
    id:
        description:
            - ID of the floating IP.
            - Used to identify existing floating IPs.
            - Required if floating IP exists.
        type: str
    project_id:
        description:
            - ID of the project the floating IP belongs to.
            - Required if floating IP doesn't exist.
            - Cannot be set for an existing floating IP.
        type: int
    region:
        description:
            - Slug of the floating IP region.
            - Required if floating IP doesn't exist.
            - Cannot be set for an existing floating IP.
        type: str
    route_ip_id:
        description:
            - Subnet or primary-ip type IP ID to which the floating IP is routed.
            - Mutually exclusive with O(target_server_id).
        type: str
    target_server_id:
        description:
            - ID of the server to which the floating IP is attached.
            - Set V(0) to unattach.
            - Mutually exclusive with O(route_ip_id).
        type: int
    ptr_record:
        description:
            - Reverse DNS name for the IP address.
        type: str
    a_record:
        description:
            - Relative DNS name for the IP address.
            - Resulting FQDN will be '<relative-dns-name>.cloud.cherryservers.net' and must be globally unique.
        type: str
    ddos_scrubbing:
        description:
            - If true, DDOS scrubbing protection will be applied in real-time.
            - Cannot be set for an existing floating IP.
        default: false
        type: bool
    tags:
        description:
            - Tags of the floating IP.
        type: dict

extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create a floating IP
  local.cherryservers.floating_ip:
    project_id: 213668
    region: "eu_nord_1"
    target_server_id: "590738"
    ptr_record: "moduletestptr"
    a_record: "moduletesta"
    tags:
      env: "test"
  register: result

- name: Update a floating IP
  local.cherryservers.floating_ip:
    id: "a0ff92c9-21f6-c387-33d0-5c941c0435f0"
    target_server_id: 590738
    ptr_record: "anstest"
    a_record: "anstest"
    tags:
      env: "test"
  register: result

- name: Delete floating IP
  local.cherryservers.floating_ip:
    state: absent
    id: "497f6eca-6276-4993-bfeb-53cbbbba6f08"
"""

RETURN = r"""
cherryservers_floating_ip:
  description: Floating IP data.
  returned: O(state=present) and not in check mode
  type: dict
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
      sample: "123456"
    project_id:
      description: Cherry Servers project ID, associated with the floating IP.
      returned: always
      type: int
      sample: 123456
    route_ip_id:
      description: ID of the IP to which the floating IP is routed to.
      returned: if exists
      type: str
      sample: "fe8b01f4-2b85-eae9-cbfb-3288c507f318"
"""

from typing import Optional
from ansible.module_utils import basic as utils
from ..module_utils import standard_module
from ..module_utils.resource_managers import floating_ip_manager


class FloatingIPModule(standard_module.StandardModule):
    """TODO"""

    def __init__(self):
        super().__init__()
        self._fip_manager = floating_ip_manager.FloatingIPManager(self._module)

    def _get_resource(self) -> Optional[dict]:
        if self._module.params["id"]:
            return self._fip_manager.get_by_id(self._module.params["id"])
        return None

    def _perform_deletion(self, resource: dict):
        if resource["target_server_id"]:
            self._fip_manager.update(resource["id"], {"targeted_to": 0})

        self._fip_manager.delete(resource["id"])

    def _get_update_requests(self, resource: dict) -> dict:
        req = {}
        params = self._module.params

        ptr_org, a_org, target_server_id_org = (
            resource["ptr_record"],
            resource["a_record"],
            resource["target_server_id"],
        )

        # prepare for comparison
        if resource["ptr_record"] is not None and resource["ptr_record"][-1] == ".":
            resource["ptr_record"] = resource["ptr_record"][:-1]
        else:
            resource["ptr_record"] = ""

        if resource["a_record"] is not None:
            resource["a_record"] = resource["a_record"].split(
                ".cloud.cherryservers.net"
            )[0]
        else:
            resource["a_record"] = ""

        if resource["target_server_id"] is None:
            resource["target_server_id"] = 0

        for k in ("ptr_record", "a_record", "tags"):
            if params[k] is not None and params[k] != resource[k]:
                req[k] = params[k]

        if (
            params["route_ip_id"] is not None
            and params["route_ip_id"] != resource["route_ip_id"]
        ):
            req["routed_to"] = params["route_ip_id"]

        if (
            params["target_server_id"] is not None
            and params["target_server_id"] != resource["target_server_id"]
        ):
            req["targeted_to"] = params["target_server_id"]

        resource["ptr_record"] = ptr_org
        resource["a_record"] = a_org
        resource["target_server_id"] = target_server_id_org

        return {"update": req}

    def _perform_update(self, requests: dict, resource: dict) -> dict:
        if requests.get("update", None):
            self._fip_manager.update(resource["id"], requests["update"])

        return self._fip_manager.get_by_id(resource["id"])

    def _perform_creation(self) -> dict:
        params = self._module.params

        fip = self._fip_manager.create(
            project_id=params["project_id"],
            params={
                "region": params["region"],
                "routed_to": params["route_ip_id"],
                "targeted_to": params["target_server_id"],
                "ptr_record": params["ptr_record"],
                "a_record": params["a_record"],
                "ddos_scrubbing": params["ddos_scrubbing"],
                "tags": params["tags"],
            },
        )

        return self._fip_manager.get_by_id(fip["id"])

    def _validate_creation_params(self):
        if (
            self._module.params["project_id"] is None
            or self._module.params["region"] is None
        ):
            self._module.fail_json(
                "project_id and region are required for creating floating ips"
            )

    @property
    def name(self) -> str:
        """Cherry Servers floating IP module name."""
        return "cherryservers_floating_ip"

    @property
    def _arg_spec(self) -> dict:
        return {
            "state": {
                "choices": ["absent", "present"],
                "default": "present",
                "type": "str",
            },
            "id": {"type": "str"},
            "project_id": {"type": "int"},
            "region": {"type": "str"},
            "route_ip_id": {"type": "str"},
            "target_server_id": {"type": "int"},
            "ptr_record": {"type": "str"},
            "a_record": {"type": "str"},
            "ddos_scrubbing": {"type": "bool", "default": False},
            "tags": {
                "type": "dict",
            },
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
            mutually_exclusive=[["route_ip_id", "target_server_id"]],
            required_if=[
                ("state", "absent", ["id"], True),
            ],
        )


def main():
    """Main function."""
    FloatingIPModule().run()


if __name__ == "__main__":
    main()
