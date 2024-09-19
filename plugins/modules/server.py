#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: server

short_description: Create and manage servers on Cherry Servers

version_added: "0.1.0"

description:
    - Create, update and delete servers on Cherry Servers.
    - If you want to manage an existing server, set O(id) along with state and other desired options.

options:
    state:
        description:
            - The state of the server.
            - V(present) will ensure the server exists.
            - V(active) will ensure the server exists and is active.
            - V(absent) will ensure that the server with the provided O(id) does not exist.
        choices: ['present', 'active', 'absent']
        type: str
        default: active
    id:
        description:
            - ID of the server.
            - Used to identify existing servers.
            - Required if server exists.
        type: int
    project_id:
        description:
            - The ID of the project the server belongs to.
            - Required if server doesn't exist.
            - Cannot be set for an existing server.
        type: str
    plan:
        description:
            - Slug of the server plan.
            - Required if server doesn't exist.
            - Cannot be set for an existing server.
        type: str
    image:
        description:
            - Slug of the server image.
            - Setting this option for an existing server requires O(allow_reinstall=true).
        type: str
    os_partition_size:
        description:
            - Server OS partition size in GB.
            - Setting this option for an existing server requires O(allow_reinstall=true).
            - This option is not tracked in server state, so setting it for an existing server
            - will always cause a re-install.
        type: int
    region:
        description:
            - Slug of the server region.
            - Required if server doesn't exist.
            - Cannot be set for an existing server.
        type: str
    hostname:
        description:
            - Server hostname.
        type: str
    ssh_keys:
        description:
            - SSH key IDs, that are added to the server.
            - Setting this option for an existing server requires O(allow_reinstall=true).
        type: list
        elements: int
    extra_ip_addresses:
        description:
            - Extra floating IP IDs that are added to the server.
            - Cannot be updated after creation.
            - If you wish to add extra floating IPs to a server after it has been created,
            - use the C(floating_ip) module instead.
        type: list
        elements: str
    user_data:
        description:
            - Base64 encoded user-data blob. It should be a bash or cloud-config script.
            - Setting this option for an existing server requires O(allow_reinstall=true).
            - This option is not tracked in server state, so setting it for an existing server
            - will always cause a re-install.
        type: str
    tags:
        description:
            - Server tags.
        type: dict
    spot_market:
        description:
            - Whether the server is a spot instance.
            - Cannot be updated after creation.
        type: bool
        default: false
    storage_id:
        description:
            - Elastic block storage ID.
            - TODO.
        type: int
    active_timeout:
        description:
            - How long to wait for the server to become active, in seconds.
        type: int
        default: 1800
    allow_reinstall:
        description:
            - Setting this to true will allow reinstalling the server.
            - This parameter is not saved in server state and you need to set it to V(true)
            - every time you need to do so.
            - Reinstalling will make the server temporarily inactive.
        type: bool
        default: false
extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create a server and wait for it to become active
  local.cherryservers.server:
    state: "active"
    project_id: "213668"
    region: "eu_nord_1"
    plan: "cloud_vps_1"
    tags:
      env: "test"
    active_timeout: 600
  register: result

- name: Read user data
  ansible.builtin.slurp:
    src: "/home/mypath/cloud-init.yaml"
  register: userdata
- name: Create a server with more options
  local.cherryservers.server:
    project_id: "213668"
    region: "eu_nord_1"
    plan: "cloud_vps_1"
    image: "fedora_39_64bit"
    ssh_keys: [1234]
    hostname: "cantankerous-crow"
    extra_ip_addresses: ["5ab09cbd-80f2-8fcd-064e-c260e44b0ae9"]
    user_data: "{{ userdata['content'] }}"
    tags:
      env: "test"
  register: result

- name: Update a server
  local.cherryservers.server:
    state: "active"
    id: 593462
    tags:
      env: "upd-test"
    active_timeout: 600
    hostname: "upd-test"
  register: result

- name: Get user data
  ansible.builtin.slurp:
    src: "/home/mypath/cloud-init.yaml"
  register: userdata
- name: Update a server with rebuilding
  local.cherryservers.server:
    state: "active"
    id: 593462
    hostname: "test"
    tags:
      env: "test-upd"
    active_timeout: 600
    image: "fedora_39_64bit"
    ssh_keys: [7630]
    user_data: "{{ userdata['content']}}"
    allow_reinstall: true
  register: result

- name: Delete a server
  local.cherryservers.server:
    state: "absent"
    id: 593225
  register: result
"""

RETURN = r"""
cherryservers_server:
  description: Server data.
  returned: O(state=present) and not in check mode
  type: dict
  contains:
    hostname:
      description: Server hostname.
      returned: always
      type: str
      sample: "honest-toucan"
    id:
      description: Server ID.
      returned: always
      type: int
      sample: "123456"
    image:
      description: Server OS image slug.
      returned: always
      type: str
      sample: "fedora_39_64bit"
    ip_addresses:
      description: Server IP addresses.
      returned: always
      type: list
      elements: dict
      contains:
        CIDR:
          description: CIDR block of the IP.
          returned: always
          type: str
          sample: "10.168.101.0/24"
        address:
          description: IP address.
          returned: always
          type: str
          sample: "10.168.101.0"
        address_family:
          description: IP address family (IPv4 or IPv6).
          returned: always
          type: int
          sample: 4
        id:
          description: IP address ID.
          returned: always
          type: str
          sample: "16a70e80-d338-1b1e-f6ef-d5aacf9f3718"
        type:
          description: IP address type.
          returned: always
          type: str
          sample: "floating-ip"
    name:
      description: Server name.
      returned: always
      type: str
      sample: "Cloud VPS 1"
    plan:
      description: Slug of the server plan.
      returned: always
      type: str
      sample: "cloud_vps_1"
    project_id:
      description: Cherry Servers project ID, associated with the server.
      returned: always
      type: int
      sample: 123456
    region:
      description: Slug of the server region.
      returned: always
      type: str
      sample: "eu_nord_1"
    spot_market:
      description: Whether the server is a spot market instance.
      returned: always
      type: bool
      sample: false
    ssh_keys:
      description: Set of the SSH key IDs allowed to SSH to the server.
      returned: always
      type: list
      elements: int
      sample: [0000, 1111]
    status:
      description: Server status.
      returned: always
      type: str
      sample: "deploying"
    storage_id:
      description: Server storage block ID. Null if doesn't exist.
      returned: always
      type: int
      sample: 593063
    tags:
      description: Key/value metadata for server tagging.
      returned: always
      type: dict
      sample:
        env: "dev"
"""

import base64
import binascii
import time
from typing import Optional, Tuple, Any
from ansible.module_utils import basic as utils
from ..module_utils import client, common, normalizers, base_module


class ServerModule(base_module.BaseModule):
    """TODO"""

    timeout = 20

    def _normalize(self, resource: dict) -> dict:
        return normalizers.normalize_server(resource, self._api_client, self._module)

    def _read_by_id(self, resource_id: Any) -> Optional[dict]:
        status, resp = self._api_client.send_request(
            "GET", f"servers/{resource_id}", self.timeout
        )
        if status not in (200, 404):
            self._module.fail_json(msg=f"error {status} getting {self.name}: {resp}")
        if status == 200:
            return resp
        return None

    @property
    def name(self) -> str:
        """TODO"""
        return "cherryservers_server"

    def _create(self):
        params = self._module.params

        if any(params[k] is None for k in ("project_id", "region", "plan")):
            self._module.fail_json(msg="missing required options for server creation.")

        if params["user_data"] is not None:
            try:
                base64.b64decode(params["user_data"], validate=True)
            except binascii.Error as e:
                self._module.fail_json(msg=f"invalid user_data string: {e}")

        if self._module.check_mode:
            self._module.exit_json(changed=True)

        status, resp = self._api_client.send_request(
            "POST",
            f"projects/{params.get('project_id')}/servers",
            self.timeout,
            **{
                "plan": params["plan"],
                "image": params["image"],
                "os_partition_size": params["os_partition_size"],
                "region": params["region"],
                "hostname": params["hostname"],
                "ssh_keys": params["ssh_keys"],
                "ip_addresses": params["extra_ip_addresses"],
                "user_data": params["user_data"],
                "spot_market": params["spot_market"],
                "storage_id": params["storage_id"],
                "tags": params["tags"],
            },
        )

        if status != 201:
            self._module.fail_json(
                msg=f"error {status}, failed to create {self.name}: {resp}"
            )

        self.resource = resp

        if self._module.params["state"] == "active":
            self._wait_for_active()

        self._exit_with_return()

    def _wait_for_active(self):
        """Wait for server to become active."""
        time_passed = 0

        while self.resource["status"] != "deployed":
            self.resource = self._read_by_id(self.resource["id"])

            time.sleep(10)
            time_passed += 10

            if time_passed >= self._module.params["active_timeout"]:
                self._module.fail_json(
                    msg=f"timed out waiting for {self.name} to become active"
                )

    def _update(self):
        basic_req, basic_changed = self._get_basic_server_update_request()
        rebuild_req, rebuild_changed = self._get_reinstall_server_update_request()
        changed = basic_changed or rebuild_changed

        self._exit_if_no_change_for_update(changed)

        if rebuild_changed:
            if self._module.params["allow_reinstall"]:
                self._reinstall_server(rebuild_req)
            else:
                self._module.fail_json(
                    msg="the options you've selected require server reinstalling."
                )

        if basic_changed:
            status, resp = self._api_client.send_request(
                "PUT", f"servers/{self.resource['id']}", self.timeout, **basic_req
            )
            if status != 201:
                self._module.fail_json(
                    msg=f"error {status}, failed to update {self.name}: {resp}"
                )
            self.resource = resp

        self._exit_with_return()

    def _get_basic_server_update_request(self) -> Tuple[dict, bool]:
        """Get Cherry Servers server update API request.

        Check for differences between current server state and module options
        and add the options that have diverged to the update request.

        Returns:
            Tuple[dict, bool]: A dictionary with the request parameters
            and a boolean indicating whether there is any difference between the server state
            and module options.
        """
        params = self._module.params
        req = {}
        changed = False

        for k in ("hostname", "tags"):
            if params[k] is not None and params[k] != self.resource[k]:
                req[k] = params[k]
                changed = True

        return req, changed

    def _get_reinstall_server_update_request(self) -> Tuple[dict, bool]:
        """Get Cherry Servers server re-install API request.

        Check for differences between current server state and module options
        and add the options that have diverged to the re-installation request.
        Options 'user_data' and 'os_partition_size' are not tracked in server state,
        so any provided option will be considered different from state.

        Returns:
            Tuple[dict, bool]: A dictionary with the request parameters
            and a boolean indicating whether there is any difference between the server state
            and module options.
        """
        req = {}
        changed = False
        params = self._module.params

        for k in ("user_data", "os_partition_size"):
            if params[k] is not None:
                req[k] = params[k]
                changed = True

        if params["ssh_keys"] is not None:
            params["ssh_keys"].sort()
        if self.resource["ssh_keys"] is not None:
            self.resource["ssh_keys"].sort()

        for k in ("image", "ssh_keys"):
            if params[k] is not None and params[k] != self.resource[k]:
                req[k] = params[k]
                changed = True
        req["password"] = common.generate_password(16)
        req["type"] = "reinstall"

        return req, changed

    def _reinstall_server(
        self,
        reinstall_req: dict,
    ):
        """Re-install Cherry Servers server.

        If re-installation fails, fail the self._module.
        """
        status, resp = self._api_client.send_request(
            "POST",
            f"servers/{self.resource['id']}/actions",
            self.timeout,
            **reinstall_req,
        )
        if status not in (201, 202):
            self._module.fail_json(
                msg=f"error {status}, failed to reinstall {self.name}: {resp}"
            )

        self.resource = resp

        if self._module.params["state"] == "active":
            self._wait_for_active()

    def _delete(self):
        self._exit_if_no_change_for_delete()
        status, resp = self._api_client.send_request(
            "DELETE", f"servers/{self.resource['id']}", self.timeout
        )
        if status != 204:
            self._module.fail_json(
                f"error {status}, failed to delete {self.name}: {resp}"
            )

        self._module.exit_json(changed=True)


def get_module_args() -> dict:
    """Return a dictionary with the modules argument specification."""
    module_args = common.get_base_argument_spec()

    module_args.update(
        {
            "state": {
                "choices": ["present", "active", "absent"],
                "default": "active",
                "type": "str",
            },
            "id": {"type": "int"},
            "project_id": {"type": "str"},
            "plan": {"type": "str"},
            "image": {"type": "str"},
            "os_partition_size": {"type": "int"},
            "region": {"type": "str"},
            "hostname": {"type": "str"},
            "ssh_keys": {"type": "list", "elements": "int", "no_log": False},
            "extra_ip_addresses": {"type": "list", "elements": "str"},
            "user_data": {"type": "str"},
            "tags": {
                "type": "dict",
            },
            "spot_market": {"type": "bool", "default": False},
            "storage_id": {"type": "int"},
            "active_timeout": {"type": "int", "default": 1800},
            "allow_reinstall": {"type": "bool", "default": False},
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

    server_module = ServerModule(module, api_client)

    server_module.run()


if __name__ == "__main__":
    main()
