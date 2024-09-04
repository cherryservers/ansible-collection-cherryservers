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

from typing import Optional, Tuple
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
        mutually_exclusive=[["route_ip_id", "target_server_id"]],
    )

    api_client = client.CherryServersClient(module)

    # If ID is not provided, we assume that creation is the intended operation.
    if module.params["id"]:
        if module.params["state"] == "absent":
            absent_state(api_client, module)
        else:
            update_state(api_client, module)
    else:
        creation_state(api_client, module)


def creation_state(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Execute creation state logic."""
    params = module.params

    if params["project_id"] is None or params["region"] is None:
        module.fail_json("project_id and region are required for creating SSH keys.")

    if module.check_mode:
        module.exit_json(changed=True)

    status, resp = api_client.send_request(
        "POST",
        f"projects/{params['project_id']}/ips",
        constants.IP_TIMEOUT,
        region=params["region"],
        routed_to=params["route_ip_id"],
        targeted_to=params["target_server_id"],
        ptr_record=params["ptr_record"],
        a_record=params["a_record"],
        ddos_scrubbing=params["ddos_scrubbing"],
        tags=params["tags"],
    )

    if status != 201:
        module.fail_json(msg=f"Failed to create floating IP: {resp}")

    # We need to do another GET request, because the object returned from POST
    # doesn't contain all the necessary data.

    fip = get_fip(api_client, module, resp["id"])
    module.exit_json(changed=True, cherryservers_floating_ip=fip)


def absent_state(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Execute deletion state logic."""
    fip = get_fip(api_client, module, module.params["id"])
    if fip:
        if module.check_mode:
            module.exit_json(changed=True)
        delete_fip(api_client, module, fip)
        module.exit_json(changed=True)
    else:
        module.exit_json(changed=False)


def get_fip(
    api_client: client.CherryServersClient, module: utils.AnsibleModule, fip_id: str
) -> Optional[dict]:
    """Retrieve a normalized Cherry Servers floating IP resource."""
    url = f"ips/{fip_id}"
    status, resp = api_client.send_request(
        "GET",
        url,
        constants.IP_TIMEOUT,
    )
    #  Code 403 can also be returned for a deleted resource, if enough time hasn't passed.
    if status not in (200, 403, 404):
        module.fail_json(msg=f"Error getting floating IP: {resp}")
    if status == 200:
        return normalizers.normalize_fip(resp)
    return None


def update_state(api_client: client.CherryServersClient, module: utils.AnsibleModule):
    """Execute update state logic."""
    fip = get_fip(api_client, module, module.params["id"])
    req, changed = get_update_request(module.params, fip)

    if module.check_mode:
        if changed:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)
    else:
        if not changed:
            module.exit_json(changed=False, cherryservers_floating_ip=fip)

    status, resp = api_client.send_request(
        "PUT", f"ips/{fip['id']}", constants.IP_TIMEOUT, **req
    )
    if status != 200:
        module.fail_json(msg=f"Failed to update floating IP address: {resp}")

    fip = get_fip(api_client, module, fip["id"])
    module.exit_json(changed=True, cherryservers_floating_ip=fip)


def delete_fip(
    api_client: client.CherryServersClient, module: utils.AnsibleModule, fip: dict
):
    """Delete a single floating IP."""
    if fip["target_server_id"]:
        untarget_fip(api_client, module, fip["id"])

    status, resp = api_client.send_request(
        "DELETE", f"ips/{module.params['id']}", constants.IP_TIMEOUT
    )
    if status != 204:
        module.fail_json(msg=f"Failed to delete floating IP: {resp}")

    module.exit_json(changed=True)


def get_update_request(params: dict, fip: dict) -> Tuple[dict, bool]:
    """Generate the necessary update request data fields."""
    req = {}
    changed = False

    ptr_org, a_org, target_server_id_org = (
        fip["ptr_record"],
        fip["a_record"],
        fip["target_server_id"],
    )

    # prepare for comparison
    if fip["ptr_record"] is not None and fip["ptr_record"][-1] == ".":
        fip["ptr_record"] = fip["ptr_record"][:-1]
    else:
        fip["ptr_record"] = ""

    if fip["a_record"] is not None:
        fip["a_record"] = fip["a_record"].split(".cloud.cherryservers.net")[0]
    else:
        fip["a_record"] = ""

    if fip["target_server_id"] is None:
        fip["target_server_id"] = 0

    for k in ("ptr_record", "a_record", "tags"):
        if params[k] is not None and params[k] != fip[k]:
            req[k] = params[k]
            changed = True

    if (
        params["route_ip_id"] is not None
        and params["route_ip_id"] != fip["route_ip_id"]
    ):
        req["routed_to"] = params["route_ip_id"]
        changed = True

    if (
        params["target_server_id"] is not None
        and params["target_server_id"] != fip["target_server_id"]
    ):
        req["targeted_to"] = params["target_server_id"]
        changed = True

    fip["ptr_record"] = ptr_org
    fip["a_record"] = a_org
    fip["target_server_id"] = target_server_id_org

    return req, changed


def untarget_fip(
    api_client: client.CherryServersClient, module: utils.AnsibleModule, fip_id: str
):
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
    run_module()


if __name__ == "__main__":
    main()
