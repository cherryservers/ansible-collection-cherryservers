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

version_added: "1.0.0"

description:
    - Create, update and delete servers on Cherry Servers.
    - To update existing servers, you must use O(id) or a combination of O(project_id) and O(hostname) to identify them.
    - When both are provided, O(id) will take priority over O(hostname).

options:
    state:
        description:
            - Server state.
            - V(present) will ensure the server exists.
            - V(active) will ensure the server exists and is active.
            - V(absent) will ensure that the server doesn't exist.
        choices: ['present', 'active', 'absent']
        type: str
        default: active
    id:
        description:
            - ID of the server.
            - Used to identify existing servers.
            - Cannot be set.
            - Required if server exists and O(hostname) is not provided.
        type: int
    project_id:
        description:
            - ID of the project the server belongs to.
            - Required if server doesn't exist.
            - Required if server exists and O(id) is not provided.
            - Cannot be set for an existing server.
        type: int
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
              will always cause a re-install.
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
            - Can be used to identify existing servers.
            - Required if server exists and O(id) is not provided.
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
              use the C(floating_ip) module instead.
        type: list
        elements: str
    user_data:
        description:
            - Base64 encoded user-data blob. It should be a bash or cloud-config script.
            - Setting this option for an existing server requires O(allow_reinstall=true).
            - This option is not tracked in server state, so setting it for an existing server
              will always cause a re-install.
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
            - Cannot be updated after creation.
            - If you wish to attach storage to a server after it has been created,
              use the C(storage) module instead.
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
              every time you need to do so.
            - Reinstalling will wipe all server data and make it temporarily inactive.
        type: bool
        default: false
extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create a server and wait for it to become active
  cherryservers.cloud.server:
    state: "active"
    project_id: 213668
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
  cherryservers.cloud.server:
    project_id: 213668
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
  cherryservers.cloud.server:
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
  cherryservers.cloud.server:
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
  cherryservers.cloud.server:
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
      sample: 123456
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
import random
import string
from typing import Optional
from ansible.module_utils import basic as utils
from ..module_utils import standard_module
from ..module_utils.resource_managers.server_manager import ServerManager


class ServerModule(standard_module.StandardModule):
    """Cherry Servers server module."""

    def __init__(self):
        super().__init__()
        self._server_manager = ServerManager(self._module)

    def _get_resource(self) -> Optional[dict]:
        resource = None
        params = self._module.params
        if params["id"]:
            resource = self._server_manager.get_by_id(params["id"])
        elif params["hostname"] and params["project_id"]:
            possible_servers = self._server_manager.get_by_project_id(
                params["project_id"]
            )
            for server in possible_servers:
                if server["hostname"] == params["hostname"]:
                    resource = server

        return resource

    def _perform_deletion(self, resource: dict):
        self._server_manager.delete_server(resource["id"])

    def _get_update_requests(self, resource: dict) -> dict:
        params = self._module.params
        req = {}
        basic_req = {}
        reinstall_req = {}

        for k in ("hostname", "tags"):
            if params[k] is not None and params[k] != resource[k]:
                basic_req[k] = params[k]

        if basic_req:
            req["basic"] = basic_req

        for k in ("user_data", "os_partition_size"):
            if params[k] is not None:
                reinstall_req[k] = params[k]

        if params["ssh_keys"] is not None:
            params["ssh_keys"].sort()
        if resource["ssh_keys"] is not None:
            resource["ssh_keys"].sort()

        for k in ("image", "ssh_keys"):
            if params[k] is not None and params[k] != resource[k]:
                reinstall_req[k] = params[k]

        if reinstall_req:
            reinstall_req["password"] = generate_password(16)
            reinstall_req["type"] = "reinstall"
            req["reinstall"] = reinstall_req

        return req

    def _perform_update(self, requests: dict, resource: dict) -> dict:
        params = self._module.params
        if requests.get("reinstall", None):
            if not params["allow_reinstall"]:
                self._module.fail_json(msg="provided options require server reinstall")
            self._server_manager.reinstall_server(
                resource["id"],
                requests["reinstall"],
            )
            if params["state"] == "active":
                self._server_manager.wait_for_active(resource, params["active_timeout"])

        if requests.get("basic", None):
            self._server_manager.update_server(resource["id"], requests["basic"])

        return self._server_manager.get_by_id(resource["id"])

    def _validate_creation_params(self):
        params = self._module.params

        if any(params[k] is None for k in ("project_id", "region", "plan")):
            self._module.fail_json(msg="missing required options for server creation.")

        if params["user_data"] is not None:
            try:
                base64.b64decode(params["user_data"], validate=True)
            except binascii.Error as e:
                self._module.fail_json(msg=f"invalid user_data string: {e}")

    def _perform_creation(self) -> dict:
        params = self._module.params

        server = self._server_manager.create_server(
            project_id=self._module.params["project_id"],
            params={
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

        if params["state"] == "active":
            server = self._server_manager.wait_for_active(
                server, params["active_timeout"]
            )

        return self._server_manager.get_by_id(server["id"])

    @property
    def name(self) -> str:
        """Cherry Servers server module name."""
        return "cherryservers_server"

    @property
    def _arg_spec(self) -> dict:

        return {
            "state": {
                "choices": ["present", "active", "absent"],
                "default": "active",
                "type": "str",
            },
            "id": {"type": "int"},
            "project_id": {"type": "int"},
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

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
            required_if=[
                ("state", "absent", ("id", "hostname"), True),
                ("state", "absent", ("id", "project_id"), True),
            ],
        )


def generate_password(length: int) -> str:
    """Generate a random password.

    The password is guaranteed to:
        1. Be at least 8 characters long, but no longer than 24 characters.
        2. Have at least one lowercase letter.
        3. Have at least one uppercase letter, that is not the first character.
        4. Have at least one digit, that is not the last character.
        5. Not have any of ' " ` ! $ % & ; % #
    """
    length = max(8, length)
    length = min(24, length)

    lowercase = random.choice(string.ascii_lowercase)
    uppercase = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    remaining = "".join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _1 in range(length - 3)
    )
    return f"{lowercase}{uppercase}{digit}{remaining}"


def main():
    """Main function."""
    ServerModule().run()


if __name__ == "__main__":
    main()
