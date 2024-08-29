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
import random
import string
from collections.abc import Sequence
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


def generate_password(length: int) -> str:
    """Generate a random password.

    The password is guaranteed to:
        1. Be at least 8 characters long, but no longer than 24 characters.
        2. Have at least one lowercase letter.
        3. Have at least one uppercase letter, that is not the first character.
        4. Have at least one digit, that is not the last character.
        5. Not have any of ' " ` ! $ % & ; % #
    """
    if length < 8:
        length = 8

    if length > 24:
        length = 24

    lowercase = random.choice(string.ascii_lowercase)
    uppercase = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    remaining = "".join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _1 in range(length - 3)
    )
    return f"{lowercase}{uppercase}{digit}{remaining}"


def find_resources(
    api_client: client.CherryServersClient,
    module: utils.AnsibleModule,
    keys: Sequence[str],
    url: str,
    timeout: int,
) -> List[dict]:
    """Find the resources that match the modules identifying parameters.

    Try to find the resources specified by the resource identifying module parameters.

    Args:

        api_client (client.CherryServersClient): Cherry Servers API client.
        module (utils.AnsibleModule): Ansible module to find the resource for.
        keys (Sequence[str]):
            Sequence that contains resource and module parameter identifying keys.
            The module parameters and the resource both must have these keys.
        url (str): The URL from which to get the resource list.
        timeout (int): Timeout in seconds.

    """
    params = module.params

    status, resp = api_client.send_request("GET", url, timeout)
    if status != 200:
        module.fail_json(msg=f"Failed to get resources: {resp}")

    matching_resources = []

    for resource in resp:
        if any(resource[k] == params[k] for k in keys):
            matching_resources.append(resource)

    return matching_resources
