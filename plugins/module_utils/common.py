# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Common module utilities.

Contains various shared module utilities.

Used by ansible modules for common tasks, such as getters and shared argument specs.

Functions:

    get_keys(api_client: client.CherryServersClient, module: utils.AnsibleModule) -> List[dict]

"""
from collections.abc import Sequence, Callable
from typing import List, Optional

from . import client
from . import constants
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


def find_resource_unique(
    api_client: client.CherryServersClient,
    module: utils.AnsibleModule,
    keys: Sequence[Sequence[str]],
    url: str,
    timeout: int,
) -> Optional[dict]:
    """TODO"""
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


def trim_ip(ip: dict):
    """Remove excess fields from IP resource."""
    to_trim = (
        "address_family",
        "href",
        "project",
        "gateway",
        "type",
        "routed_to",
        "targeted_to",
        "region",
    )
    target_id = ip.get("targeted_to", {}).get("id", 0)
    region_slug = ip.get("region", {}).get("slug")
    for t in to_trim:
        ip.pop(t, None)

    ip["targeted_to"] = target_id
    ip["region_slug"] = region_slug
