# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Common module utilities.

Contains various shared module utilities.
Used by ansible modules for common tasks, such as shared argument specs and resource getters.

Functions:

    get_base_argument_spec -> dict: Returns the base argument spec for the module.
    find_resource(api_client: client.CherryServersClient, module: utils.AnsibleModule,
        keys: Sequence[Sequence[str]], url: str, timeout: int) -> Optional[dict]:
        Find the resource that matches the modules identifying parameters.

"""
from collections.abc import Sequence
from typing import Optional

from . import client
from ansible.module_utils import basic as utils


def get_base_argument_spec() -> dict:
    """Return a dictionary with the base module argument spec."""
    return {
        "auth_token": {
            "type": "str",
            "no_log": True,
            "fallback": (utils.env_fallback, ["CHERRY_AUTH_TOKEN", "CHERRY_AUTH_KEY"]),
        },
    }


def find_resource(
    api_client: client.CherryServersClient,
    module: utils.AnsibleModule,
    keys: Sequence[Sequence[str]],
    url: str,
    timeout: int,
) -> Optional[dict]:
    """Find the resource that matches the modules identifying parameters.

    Try to find the resource specified by the resource identifying module parameters,
    from a list of possible resources.
    If multiple matching resources are found, fails the module.

    Args:

        api_client (client.CherryServersClient): Cherry Servers API client.
        module (utils.AnsibleModule): Ansible module to find the resource for.
        keys (Sequence[Sequence[str]]):
            Sequence that contains sequences of identifying dictionary keys.
            The first inner sequence contains the resource identifying keys.
            The second inner sequence contains the module parameter identifying keys.
            The keys must be arranged in a matching order.
            For example: [["id", "address", "region"], ["id", "address", "region_slug"]]
            This parameter is necessary for matching values
            that are named differently in the module and resource.
        url (str): The URL from which to get the resource list.
        timeout (int): Timeout in seconds.

    """
    params = module.params

    if len(keys) != 2 or len(keys[0]) != len(keys[1]):
        module.fail_json(msg=f"Invalid key sequence: {keys}")

    status, resp = api_client.send_request("GET", url, timeout)
    if status != 200:
        module.fail_json(msg=f"Failed to get resources: {resp}")

    matching_resources = []

    for resource in resp:
        if any(
            resource[k_resource] == params[k_param]
            for (k_resource, k_param) in zip(keys[0], keys[1])
        ):
            matching_resources.append(resource)

    if len(matching_resources) > 1:
        module.fail_json(msg=f"Multiple matching resources found: {matching_resources}")

    if not matching_resources:
        return None

    return matching_resources[0]
