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
    - If you set options that require rebuilding an existing server,
    - it will become temporarily inactive.

options:
    state:
        description:
            - The state of the server.
            - V(present) will ensure the server exists.
            - V(active) will ensure the server exists and is active.
            - V(absent) will ensure the server doesn't exist.
        choices: ['present', 'active', 'absent']
        type: str
        default: active
    id:
        description:
            - ID of the server.
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
            - Setting this option for an existing server requires rebuilding.
        type: str
    os_partition_size:
        description:
            - Server OS partition size in GB.
            - Setting this option for an existing server requires rebuilding.
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
            - Setting this option for an existing server requires rebuilding.
        type: list
        elements: str
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
            - Setting this option for an existing server requires rebuilding.
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
  register: user_data_file
- name: Create a server with more options
  local.cherryservers.server:
    project_id: "213668"
    region: "eu_nord_1"
    plan: "cloud_vps_1"
    image: "fedora_39_64bit"
    ssh_keys: ["1234"]
    hostname: "cantankerous-crow"
    extra_ip_addresses: ["5ab09cbd-80f2-8fcd-064e-c260e44b0ae9"]
    user_data: "{{ user_data_file['content'] }}"
    tags:
      env: "test"
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
      description: Slug of the server operating system.
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
    password:
      description: Server password credential.
      returned: if exists. Not available while server is pending and is scrubbed after 24 hours.
      type: str
      sample: "K85uf6Kx"
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
    state:
      description: Server state.
      returned: always
      type: str
      sample: "active"
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
    username:
      description: Server username credential.
      returned: if exists. Not available while server is pending and is scrubbed after 24 hours.
      type: str
      sample: "root"
"""

import base64
import binascii
import time
from typing import Optional
from ansible.module_utils import basic as utils
from ..module_utils import client
from ..module_utils import common
from ..module_utils import constants
from ..module_utils import normalizers


def run_module():
    """Execute the ansible module."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    api_client = client.CherryServersClient(module)

    if module.params["id"]:
        modification_state(api_client, module)
    else:
        creation_state(api_client, module)


def modification_state(
    api_client: client.CherryServersClient, module: utils.AnsibleModule
):
    """Execute modification state logic."""
    absent_state(api_client, module)


def creation_state(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Execute creation state logic."""
    params = module.params

    if any(params[k] is None for k in ("project_id", "region", "plan")):
        module.fail_json(msg="Missing required options for server creation.")

    if params["user_data"] is not None:
        try:
            base64.b64decode(params["user_data"], validate=True)
        except binascii.Error as e:
            module.fail_json(msg=f"Invalid user_data string: {e}")

    if module.check_mode:
        module.exit_json(changed=True)

    server = create_server(api_client, module)

    if module.params["state"] == "active":
        wait_for_active(server, api_client, module)

    # We need to do another GET request, because the object returned from POST
    # doesn't contain all the necessary data.

    server = get_server(api_client, module, server["id"])

    module.exit_json(changed=True, cherryservers_server=server)


def absent_state(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Execute deletion state logic."""
    server = get_server(api_client, module, module.params["id"])
    if server:
        if module.check_mode:
            module.exit_json(changed=True)
        delete_server(api_client, module, server["id"])
        module.exit_json(changed=True)
    else:
        module.exit_json(changed=False)


def get_server(
    api_client: client.CherryServersClient, module: utils.AnsibleModule, server_id: int
) -> Optional[dict]:
    """Retrieve a normalized Cherry Servers server resource."""
    status, resp = api_client.send_request(
        "GET", f"servers/{server_id}", constants.SERVER_TIMEOUT
    )
    if status not in (200, 404):
        module.fail_json(msg=f"Error getting server: {resp}")
    if status == 200:
        return normalizers.normalize_server(resp)
    return None


def create_server(
    api_client: client.CherryServersClient, module: utils.AnsibleModule
) -> Optional[dict]:
    """Create a new server.

    Will fail the module if an error occurs.

    Returns:
        Optional[dict]: Normalized server resource.
    """
    params = module.params

    status, resp = api_client.send_request(
        "POST",
        f"projects/{params.get('project_id')}/servers",
        constants.SERVER_TIMEOUT,
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
        module.fail_json(msg=f"Failed to create server: {resp}")

    return normalizers.normalize_server(resp)


def wait_for_active(
    server: dict, api_client: client.CherryServersClient, module: utils.AnsibleModule
):
    """Wait for server to become active."""
    time_passed = 0

    while server["state"] != "active":
        resp = get_server(api_client, module, server["id"])
        server = resp

        time.sleep(10)
        time_passed += 10

        if time_passed >= module.params["active_timeout"]:
            module.fail_json(msg="Timed out waiting for server to become active")


def delete_server(
    api_client: client.CherryServersClient, module: utils.AnsibleModule, server_id: int
):
    """Delete a server."""
    status, resp = api_client.send_request(
        "DELETE", f"servers/{server_id}", constants.SERVER_TIMEOUT
    )
    if status != 204:
        module.fail_json(f"Failed to delete server: {resp}")


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
            "ssh_keys": {"type": "list", "elements": "str", "no_log": False},
            "extra_ip_addresses": {"type": "list", "elements": "str"},
            "user_data": {"type": "str"},
            "tags": {
                "type": "dict",
            },
            "spot_market": {"type": "bool", "default": False},
            "storage_id": {"type": "int"},
            "active_timeout": {"type": "int", "default": 1800},
        }
    )

    return module_args


def main():
    """Main function."""
    run_module()


if __name__ == "__main__":
    main()
