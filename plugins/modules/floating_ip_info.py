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
  - If you don't provide a project, only the IP ID is checked for a match.

options:
    id:
        description:
            - The ID of the floating IP.
            - Required if O(project_id) is not provided.
        type: str
    address:
        description:
            - The IP address of the floating IP.
        type: str
    project_id:
        description:
            - The ID of the project the floating IP belongs to.
            - Required if O(id) is not provided.
        type: str
    tags:
        description:
            - Tags of the floating IP.
        type: dict
    region_slug:
        description:
            - The region slug of the floating IP.
        aliases: [region]
        type: str
    available_only:
        description:
            - Whether to search for available floating IPs only.
        type: bool
        default: false

extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get single floating IP
  local.cherryservers.floating_ip_info:
    auth_token: "{{ auth_token }}"
    id: "497f6eca-6276-4993-bfeb-53cbbbba6f08"
  register: result

- name: Get all project floating IPs
  local.cherryservers.floating_ip_info:
    auth_token: "{{ auth_token }}"
    project_id: "123456"
  register: result

- name: 'Get all floating IPs in the EU Nord-1 region, that have the env: dev tag'
  local.cherryservers.floating_ip_info:
    auth_token: "{{ auth_token }}"
    region_slug: "eu_nord_1"
    project_id: "123456"
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
    region_slug:
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
    targeted_to:
      description: ID of the server to which the floating IP is targeted to. Value is 0 if IP is not targeted.
      returned: always
      type: int
      sample: "123456"
"""

from ansible.module_utils import basic as utils
from ..module_utils import client
from ..module_utils import common
from ..module_utils import constants
from typing import List


def run_module():
    """Execute the ansible module."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_one_of=[("project_id", "id")],
    )

    api_client = client.CherryServersClient(module)

    if module.params["project_id"] is None:
        ips = get_single_ip(api_client, module)
    else:
        ips = get_multiple_ips(api_client, module)

    module.exit_json(changed=False, cherryservers_floating_ips=ips)


def get_single_ip(api_client: client, module: utils.AnsibleModule) -> List[dict]:
    """Get a single floating IP from the Cherry Servers client.

    This IP is returned as a single dictionary entry in a list, for easier
    compatibility with multiple IP returning functionality.
    """
    status, resp = api_client.send_request(
        "GET", f"ips/{module.params['id']}", constants.IP_TIMEOUT
    )

    ip = []

    if status == 200 and resp["type"] == "floating-ip":
        common.trim_ip(resp)
        ip.append(resp)
    elif status != 404:
        module.fail_json(msg=f"Unexpected client error: {resp}")

    return ip


def get_multiple_ips(api_client: client, module: utils.AnsibleModule) -> List[dict]:
    """Get multiple floating IPs from the Cherry Servers client."""
    params = module.params

    if params["available_only"]:
        status, resp = api_client.send_request(
            "GET",
            f"projects/{params['project_id']}/available_ips",
            constants.IP_TIMEOUT,
        )
    else:
        status, resp = api_client.send_request(
            "GET", f"projects/{params['project_id']}/ips", constants.IP_TIMEOUT
        )

    ips = []

    if status == 200:
        ips = common.filter_fips(module.params, resp)
    elif status != 404:
        module.fail_json(msg=f"Unexpected client error: {resp}")

    return ips


def get_module_args() -> dict:
    """Return a dictionary with the modules argument specification."""
    module_args = common.get_base_argument_spec()

    module_args.update(
        {
            "tags": {
                "type": "dict",
            },
            "region_slug": {"type": "str", "aliases": ["region"]},
            "id": {"type": "str"},
            "address": {"type": "str"},
            "project_id": {"type": "str"},
            "available_only": {"type": "bool", "default": "false"},
        }
    )

    return module_args


def filter_fips(module_params: dict, fips: Sequence[dict]) -> List[dict]:
    """Filter floating IPs according to provided module parameters.

    We go through all the project IPs and add all the ones whose
    values match the user provided module parameters. If the parameter
    is None, we consider it matching, since the user did not provide it.

    """
    result = []

    for ip in fips:
        if ip["type"] != "floating-ip":
            continue
        if (
            all(
                module_params[k] is None or module_params[k] == ip[k]
                for k in ["id", "address"]
            )
            and (
                module_params["region_slug"] is None
                or module_params["region_slug"] == ip["region"]["slug"]
            )
            and (
                module_params["tags"] is None
                or all(
                    module_params["tags"][t] == ip["tags"].get(t)
                    for t in module_params["tags"]
                )
            )
        ):
            common.trim_ip(ip)
            result.append(ip)

    return result


def main():
    """Main function."""
    run_module()


if __name__ == "__main__":
    main()
