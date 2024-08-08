# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Common module utilities.

Contains various shared module utilities.

Used by ansible modules for common tasks, such as getters and shared argument specs.

Functions:

    get_keys(api_client: client.CherryServersClient, module: utils.AnsibleModule) -> List[dict]

"""
from typing import List

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


def get_keys(
    api_client: client.CherryServersClient, module: utils.AnsibleModule
) -> List[dict]:
    """Search for and retrieve SSH keys that match the provided criteria.

    Returns:

            List[dict]: SSH keys that match the modules argument_spec parameters.

    """
    params = module.params

    status, resp = api_client.send_request("GET", "ssh-keys", constants.SSH_TIMEOUT)
    if status != 200:
        module.fail_json(msg=f"Failed to get SSH keys: {resp}")

    matching_keys = []

    for sshkey in resp:
        if (
            any(sshkey[k] == params[k] for k in ["id", "fingerprint", "label"])
            or sshkey["key"] == params["public_key"]
        ):
            matching_keys.append(sshkey)

    return matching_keys


def filter_fips(module_params: dict, fips: List[dict]) -> List[dict]:
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
            trim_ip(ip)
            result.append(ip)

    return result


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
