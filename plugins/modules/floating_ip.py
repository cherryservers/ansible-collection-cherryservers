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
    - If you wish to update or delete existing floating IPs,
    - you must provide O(id) or the combination of O(project_id) and O(address),
    - as identifiers, along with state and other desired options.
    - If you wish to create new floating IPs,
    - you must provide O(project_id) and O(region_slug) along other desired options.

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
            - Required if floating IP exists and O(address) is not provided.
            - Mutually exclusive with O(address).
        type: str
    address:
        description:
            - Address of the floating IP.
            - Used to identify existing floating IPs.
            - Required if floating IP exists and O(id) is not provided.
            - Mutually exclusive with O(id).
        type: str
    project_id:
        description:
            - The ID of the project the floating IP belongs to.
            - Required if O(state=present) and floating IP doesn't exist.
            - Required by O(address).
            - Cannot be updated after creation.
        type: str
    region_slug:
        description:
            - The region slug of the floating IP.
            - Required if O(state=present) and floating IP doesn't exist.
            - Cannot be updated after creation.
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
            - Set V(0) to unattach.
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
            - Cannot be updated after creation.
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
from .. module_utils import cherry_module


class FloatingIPModule(cherry_module.CherryModule):
    """TODO"""

    def _create_resource(self):
        pass

    def _normalize_resource(self):
        pass

    def _update_resource(self):
        pass

    def _delete_resource(self):
        pass

    def _check_diff(self) -> bool:
        pass


def run_module():
    """Execute the ansible module."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[["route_ip_id", "target_server_id"], ["id", "address"]],
        required_one_of=[("project_id", "id")],
        required_by={"address": "project_id"},
    )

    api_client = client.CherryServersClient(module)

    if module.params["id"] is not None:
        url = f"ips/{module.params['id']}"
    else:
        url = f"projects/{module.params['project_id']}/ips"

    fip = common.find_resource_unique(
        api_client,
        module,
        constants.FIP_IDENTIFYING_KEYS,
        url,
        constants.IP_TIMEOUT,
    )

    fip = common.trim_ip(fip)

    if module.params["state"] == "present":
        if fip:
            if check_param_state_diff(module.params, fip):
                update_key(api_client, module, key["id"])
            elif module.check_mode:
                module.exit_json(changed=False)
            else:
                module.exit_json(changed=False, cherryservers_sshkey=key)
        else:
            create_key(api_client, module)
    elif module.params["state"] == "absent":
        if fip:
            delete_fip(api_client, module, fip)
        else:
            module.exit_json(changed=False)


def present_ip(api_client, module):
    """Perform the necessary actions to ensure 'present' floating IP state."""
    status, resp = api_client.send_request(
        "GET", f"projects/{module.params['project_id']}/ips", constants.IP_TIMEOUT
    )

    ips = []

    if status == 200:
        ips = common.filter_fips(module.params, resp)
    elif status != 404:
        module.fail_json(msg=f"Unexpected client error: {resp}")

    if len(ips) > 1:
        module.fail_json(msg="More than one floating IP matches the giver parameters.")
    if ips:
        if check_param_state_diff(module.params, ips[0]):
            update_ip(api_client, module, ips[0]["id"])
        else:
            module.exit_json(changed=False)
    else:
        create_ip(api_client, module)


def create_ip(api_client: client, module: utils.AnsibleModule):
    """Create a new floating IP address."""
    params = module.params

    if params["project_id"] is None or params["region_slug"] is None:
        module.fail_json(
            "project_id and region_slug are required for creating SSH keys."
        )

    if module.check_mode:
        module.exit_json(changed=True)

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

    # We need to do another GET request, because the object returned from POST
    # doesn't contain all the necessary data.

    status, resp = api_client.send_request(
        "GET", f"ips/{resp['id']}", constants.IP_TIMEOUT
    )

    if status != 200:
        module.fail_json(
            msg=f"Failed to retrieve floating IP after creating it: {resp}"
        )

    common.trim_ip(resp)
    module.exit_json(changed=True, cherryservers_floating_ip=resp)


def delete_fip(api_client: client, module: utils.AnsibleModule, fip: dict):
    """Delete a single floating IP."""
    if module.check_mode:
        module.exit_json(changed=True)

    if fip["targeted_to"] != 0:
        untarget_fip(api_client, module, fip["id"])

    status, resp = api_client.send_request(
        "DELETE", f"ips/{module.params['id']}", constants.IP_TIMEOUT
    )
    if status != 204:
        module.fail_json(msg=f"Failed to delete floating IP: {resp}")

    module.exit_json(changed=True)


def update_ip(api_client: client, module: utils.AnsibleModule, fip_id: str):
    """TODO"""
    pass


def check_param_state_diff(module_params: dict, fip: dict) -> bool:
    """Check if module parameters differ from actual resource state.

    Args:

        module_params (dict): Module parameters.
        fip (dict): Current floating IP state.

    Returns:

        bool: True if differs from actual floating IP state, False otherwise.

    """
    if module_params["route_ip_id"] is not None and module_params["route_ip_id"] != fip:
        return True
    if (
            module_params["public_key"] is not None
            and module_params["public_key"] != fip["key"]
    ):
        return True
    return False


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
