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

description: Create, update and delete floating IPs on Cherry Servers.

options:
    state:
        description:
            - The state of the floating IP.
            - If V(absent), all floating IPs that match all of the provided options will be deleted.
        choices: ['absent', 'present']
        type: str
        default: present
    id:
        description:
            - ID of the floating IP.
            - Ignored if O(state=present) floating IP doesn't exist.
            - Required if O(state=absent) and O(project_id) is not provided.
        type: str
    address:
        description:
            - Address of the floating IP.
            - Ignored if O(state=present) floating IP doesn't exist.
        type: str
    project_id:
        description:
            - The ID of the project the floating IP belongs to.
            - Required if O(state=present) and floating IP doesn't exist.
            - Required if O(state=absent) and O(id) is not provided.
        type: str
    region_slug:
        description:
            - The region slug of the floating IP.
            - Required if O(state=present) and floating IP doesn't exist.
        aliases: [region]
        type: str
    route_ip_id:
        description:
            - Subnet or primary-ip type IP ID to which the floating IP is routed.
            - Mutually exclusive with O(target_server_id).
        type: str
    target_server_id:
        description:
            - The ID of the server to which the floating IP is attached.
            - Mutually exclusive with O(route_ip_id).
        type: str
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
    project_id: "213668"
    region_slug: "eu_nord_1"
    target_server_id: "590738"
    ptr_record: "moduletestptr"
    a_record: "moduletesta"
    tags:
      env: "test"
  register: result

- name: Delete single floating IP
  local.cherryservers.floating_ip:
    state: absent
    id: "497f6eca-6276-4993-bfeb-53cbbbba6f08"

- name: "Delete IPs targeted to server 590738, that have the 'env: test' tag"
  local.cherryservers.floating_ip:
    state: "absent"
    project_id: "213668"
    target_server_id: "590738"
    tags:
      env: "test"
  register: result
"""

RETURN = r"""
cherryservers_floating_ips:
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


def run_module():
    """Execute the ansible module."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[["route_ip_id", "target_server_id"]],
        required_if=[
            ("state", "absent", ("id", "project_id"), True),
        ],
    )

    api_client = client.CherryServersClient(module)

    if module.params["state"] == "present":
        create_ip(api_client, module)
    elif module.params["state"] == "absent":
        if module.params["id"] is not None and module.params["project_id"] is None:
            delete_single_ip(api_client, module)
        else:
            delete_multi_ips(api_client, module)


def create_ip(api_client: client, module: utils.AnsibleModule):
    """Create a new floating IP address."""
    params = module.params

    status, resp = api_client.send_request(
        "POST",
        f"projects/{params['project_id']}/ips",
        constants.IP_TIMEOUT,
        region=params["region_slug"],
        routed_to=params["route_ip_id"],
        targeted_to=params["target_server_id"],
        ptr_record=params["ptr_record"],
        a_record=params["a_record"],
        ddos_scrubbing=params["ddos_scrubbing"],
        tags=params["tags"],
    )

    if status != 201:
        module.fail_json(msg=f"Failed to create floating IP: {resp}")

    # We need to another GET request, because the object returned from POST
    # doesn't contain all the necessary data.

    status, resp = api_client.send_request("GET", f"ips/{resp['id']}", constants.IP_TIMEOUT)

    if status != 200:
        module.fail_json(
            msg=f"Failed to retrieve floating IP after creating it: {resp}"
        )

    common.trim_ip(resp)
    module.exit_json(changed=True, cherryservers_floating_ip=resp)


def delete_single_ip(api_client: client, module: utils.AnsibleModule):
    """Delete a single floating IP."""
    status, resp = api_client.send_request("GET", f"ips/{module.params['id']}", constants.IP_TIMEOUT)
    if status == 404:
        module.exit_json(changed=False)
    elif status != 200:
        module.fail_json(
            msg=f"Unknown error when checking if floating IP exists: {resp}"
        )

    if resp["targeted_to"] != 0:
        untarget_fip(api_client, module, resp["id"])

    if module.check_mode:
        module.exit_json(changed=True)

    status, resp = api_client.send_request("DELETE", f"ips/{module.params['id']}", constants.IP_TIMEOUT)
    if status != 204:
        module.fail_json(msg=f"Failed to delete floating IP: {resp}")

    module.exit_json(changed=True)


def delete_multi_ips(api_client: client, module: utils.AnsibleModule):
    """Delete any floating IPs that match the modules argument_spec parameters."""
    params = module.params

    status, resp = api_client.send_request(
        "GET", f"projects/{params['project_id']}/ips", constants.IP_TIMEOUT
    )

    fips_to_delete = common.filter_fips(params, resp)

    if module.check_mode and fips_to_delete:
        module.exit_json(changed=True)
    elif not fips_to_delete:
        module.exit_json(changed=False)

    failures = []
    for fip in fips_to_delete:
        fip_id = fip["id"]

        if fip["targeted_to"] != 0:
            untarget_fip(api_client, module, fip_id)

        status, _2 = api_client.send_request(
            "DELETE",
            f"ips/{fip_id}",
            constants.IP_TIMEOUT,
        )
        if status != 204:
            failures.append(f"Failed to delete floating IP: {fip_id}")
    if failures:
        module.fail_json(changed=True, msg="\n".join(failures))
    module.exit_json(changed=True)


def untarget_fip(api_client: client, module: utils.AnsibleModule, fip_id: str):
    """Set floating IP target server ID to 0."""
    status, resp = api_client.send_request(
        "PUT",
        f"ips/{fip_id}",
        constants.IP_TIMEOUT,
        targeted_to=0,
    )
    if status != 200:
        module.fail_json(msg=f"Failed to untarget floating IP: {resp}")


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
            "address": {"type": "str"},
            "project_id": {"type": "str"},
            "region_slug": {"type": "str", "aliases": ["region"]},
            "route_ip_id": {"type": "str"},
            "target_server_id": {"type": "str"},
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
    run_module()


if __name__ == "__main__":
    main()
