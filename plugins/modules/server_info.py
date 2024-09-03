#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: server_info

short_description: Gather information about your Cherry Servers servers

version_added: "0.1.0"

description:
  - Gather information about your Cherry Servers servers.
  - Returns servers that match all your provided options in the given project.
  - Alternatively, you can get a single server by specifying its ID.

options:
    id:
        description:
            - ID of the server.
        type: int
    project_id:
        description:
            - The ID of the project the server belongs to.
            - Required if O(id) is not provided.
        type: int
    plan:
        description:
            - Slug of the server plan.
        type: str
    image:
        description:
            - Server OS image slug.
        type: str
    region:
        description:
            - Slug of the server region.
        type: str
    hostname:
        description:
            - Server hostname.
        type: str
    tags:
        description:
            - Server tags.
        type: dict
    spot_market:
        description:
            - Whether the server is a spot instance.
        type: bool
    storage_id:
        description:
            - Elastic block storage ID.
            - TODO.
        type: int
extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get single server
  local.cherryservers.server_info:
    id: 593462
  register: result

- name: Get all project servers
  local.cherryservers.server_info:
    project_id: "213668"
  register: result

- name: 'Get all servers in the EU Nord-1 region, that have the env: test-upd tag'
  local.cherryservers.server_info:
    region: "eu_nord_1"
    project_id: "213668"
    tags:
      env: "test-upd"
  register: result

- name: Get non existing server
  local.cherryservers.server_info:
    id: 999999
  register: result

- name: Get servers by plan
  local.cherryservers.server_info:
    project_id: "213668"
    plan: cloud_vps_1
  register: result
"""

RETURN = r"""
cherryservers_servers:
  description: Server data.
  returned: always
  type: list
  elements: dict
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

from typing import List
from ansible.module_utils import basic as utils
from ..module_utils import common
from ..module_utils import client
from ..module_utils import normalizers
from ..module_utils import constants


def run_module():
    """Execute the ansible module."""

    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_one_of=[("project_id", "id")],
    )

    api_client = client.CherryServersClient(module)

    if module.params["id"] is not None:
        servers = get_single_server(api_client, module)
    else:
        servers = get_multiple_servers(api_client, module)

    r = []

    for server in servers:
        server = normalizers.normalize_server(server, api_client, module)
        if server_filter(module.params, server):
            r.append(server)

    module.exit_json(changed=False, cherryservers_servers=r)


def get_single_server(api_client: client, module: utils.AnsibleModule) -> List[dict]:
    """Get a single server from the Cherry Servers client.

    This server is returned as a single dictionary entry in a list, for easier
    compatibility with multiple server returning functionality.
    """
    status, resp = api_client.send_request(
        "GET", f"servers/{module.params['id']}", constants.SERVER_TIMEOUT
    )

    servers = []

    if status == 200:
        servers.append(resp)
    elif status != 404:
        module.fail_json(msg=f"Unexpected client error: {resp}")

    return servers


def get_multiple_servers(api_client: client, module: utils.AnsibleModule) -> List[dict]:
    """Get multiple servers from the Cherry Servers client."""
    params = module.params

    status, resp = api_client.send_request(
        "GET", f"projects/{params['project_id']}/servers", constants.SERVER_TIMEOUT
    )

    if status not in (200, 404):
        module.fail_json(msg=f"Unexpected client error: {resp}")

    return resp


def get_module_args() -> dict:
    """Return a dictionary with the modules argument specification."""
    module_args = common.get_base_argument_spec()

    module_args.update(
        {
            "tags": {
                "type": "dict",
            },
            "region": {"type": "str"},
            "hostname": {"type": "str"},
            "plan": {"type": "str"},
            "image": {"type": "str"},
            "id": {"type": "int"},
            "project_id": {"type": "int"},
            "spot_market": {"type": "bool"},
            "storage_id": {"type": "int"},
        }
    )

    return module_args


def server_filter(module_params: dict, server: dict) -> bool:
    """Check if the server should be included in the response."""
    if all(
        module_params[k] is None or module_params[k] == server[k]
        for k in (
            "region",
            "hostname",
            "plan",
            "image",
            "id",
            "project_id",
            "spot_market",
            "storage_id",
        )
    ) and (
        module_params["tags"] is None
        or all(
            module_params["tags"][k] == server["tags"].get(k)
            for k in module_params["tags"]
        )
    ):
        return True
    return False


def main():
    """Main function."""
    run_module()


if __name__ == "__main__":
    main()
