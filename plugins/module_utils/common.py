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

    status, resp = api_client.send_request(
        "GET",
        "ssh-keys",
    )
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
