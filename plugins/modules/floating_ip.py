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

from typing import Optional, Tuple, Any
from ansible.module_utils import basic as utils
from ..module_utils import client, common, normalizers, base_module


class FloatingIPModule(base_module.BaseModule):
    """TODO"""

    timeout = 30

    @property
    def name(self) -> str:
        """TODO"""
        return "cherryservers_floating_ip"

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_fip(resource)

    def _create(self):
        params = self._module.params

        if params["project_id"] is None or params["region"] is None:
            self._module.fail_json(
                "project_id and region are required for creating floating ips"
            )

        if self._module.check_mode:
            self._module.exit_json(changed=True)

        status, resp = self._api_client.send_request(
            "POST",
            f"projects/{params['project_id']}/ips",
            self.timeout,
            region=params["region"],
            routed_to=params["route_ip_id"],
            targeted_to=params["target_server_id"],
            ptr_record=params["ptr_record"],
            a_record=params["a_record"],
            ddos_scrubbing=params["ddos_scrubbing"],
            tags=params["tags"],
        )

        if status != 201:
            self._module.fail_json(
                msg=f"error {status}, failed to create {self.name}: {resp}"
            )

        self.resource = resp
        self._exit_with_return()

    def _read_by_id(self, resource_id: Any) -> Optional[dict]:
        status, resp = self._api_client.send_request(
            "GET",
            f"ips/{resource_id}",
            self.timeout,
        )
        #  Code 403 can also be returned for a deleted resource, if enough time hasn't passed.
        if status not in (200, 403, 404):
            self._module.fail_json(msg=f"error {status} getting {self.name}: {resp}")
        if status == 200:
            return resp
        return None

    def _update(self):
        req, changed = self._get_update_request()

        self._exit_if_no_change_for_update(changed)

        status, resp = self._api_client.send_request(
            "PUT", f"ips/{self._resource['id']}", self.timeout, **req
        )
        if status != 200:
            self._module.fail_json(
                msg=f"error {status}, failed to update {self.name}: {resp}"
            )

        self.resource = resp
        self._exit_with_return()

    def _get_update_request(self) -> Tuple[dict, bool]:
        """Generate the necessary update request data fields."""
        req = {}
        changed = False
        params = self._module.params

        ptr_org, a_org, target_server_id_org = (
            self.resource["ptr_record"],
            self.resource["a_record"],
            self.resource["target_server_id"],
        )

        # prepare for comparison
        if (
            self.resource["ptr_record"] is not None
            and self.resource["ptr_record"][-1] == "."
        ):
            self.resource["ptr_record"] = self.resource["ptr_record"][:-1]
        else:
            self.resource["ptr_record"] = ""

        if self.resource["a_record"] is not None:
            self.resource["a_record"] = self.resource["a_record"].split(
                ".cloud.cherryservers.net"
            )[0]
        else:
            self.resource["a_record"] = ""

        if self.resource["target_server_id"] is None:
            self.resource["target_server_id"] = 0

        for k in ("ptr_record", "a_record", "tags"):
            if params[k] is not None and params[k] != self.resource[k]:
                req[k] = params[k]
                changed = True

        if (
            params["route_ip_id"] is not None
            and params["route_ip_id"] != self.resource["route_ip_id"]
        ):
            req["routed_to"] = params["route_ip_id"]
            changed = True

        if (
            params["target_server_id"] is not None
            and params["target_server_id"] != self.resource["target_server_id"]
        ):
            req["targeted_to"] = params["target_server_id"]
            changed = True

        self.resource["ptr_record"] = ptr_org
        self.resource["a_record"] = a_org
        self.resource["target_server_id"] = target_server_id_org

        return req, changed

    def _delete(self):
        self._exit_if_no_change_for_delete()

        if self._resource["target_server_id"]:
            self._untarget_fip()

        status, resp = self._api_client.send_request(
            "DELETE", f"ips/{self.resource['id']}", self.timeout
        )
        if status != 204:
            self._module.fail_json(
                msg=f"error {status}, failed to delete {self.name}: {resp}"
            )

        self._module.exit_json(changed=True)

    def _untarget_fip(self):
        """Set floating IP target server ID to 0."""
        status, resp = self._api_client.send_request(
            "PUT",
            f"ips/{self._resource['id']}",
            self.timeout,
            targeted_to=0,
        )
        if status != 200:
            self._module.fail_json(
                msg=f"error {status}, failed to untarget {self.name}: {resp}"
            )


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
    )

    return module_args


def main():
    """Main function."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[["route_ip_id", "target_server_id"]],
        required_if=[
            ("state", "absent", ["id"], True),
        ],
    )

    api_client = client.CherryServersClient(module)
    fip_module = FloatingIPModule(module, api_client)
    fip_module.run()


if __name__ == "__main__":
    main()
