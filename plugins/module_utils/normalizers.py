# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Cherry Servers resource normalizers.

These normalizers help prepare various Cherry Servers resources for working with ansible modules.

Functions:

    normalize_ip(ip: dict): Normalize an IP resource.

"""
from ansible.module_utils import basic as utils
from ..module_utils import client
from ..module_utils import constants


def normalize_fip(fip: dict) -> dict:
    """Normalize Cherry Servers floating IP resource."""
    return {
        "a_record": fip.get("a_record", None),
        "address": fip.get("address", None),
        "cidr": fip.get("cidr", None),
        "id": fip.get("id", None),
        "ptr_record": fip.get("ptr_record", None),
        "region": fip.get("region", {}).get("slug", None),
        "tags": fip.get("tags", None),
        "target_server_id": fip.get("targeted_to", {}).get("id", None),
        "route_ip_id": fip.get("routed_to", {}).get("id", None),
        "project_id": fip.get("project", {}).get("id", None),
        "type": fip.get("type", None),
    }


def get_server_image_slug(  # the module will fail, if it doesn't return str, so pylint: disable=inconsistent-return-statements
    server: dict, api_client: client.CherryServersClient, module: utils.AnsibleModule
) -> str:
    """Get server image slug.

    This is required because the server object retrieved from the API only
    knows the full name of its image, but not the slug, even though the
    slug is what's typically used for configuration.
    """

    plan = server.get("plan", {}).get("slug", None)
    status, resp = api_client.send_request(
        "GET", f"plans/{plan}/images", constants.SERVER_TIMEOUT
    )

    if status != 200:
        module.fail_json(
            msg=f"failed to retrieve server plan images, status code: {status}"
        )

    if server["image"] == "unknown":
        return "unknown"

    for image in resp:
        if image["name"] == server["image"]:
            return image["slug"]

    module.fail_json(msg=f"no server image slug found for image: {server['image']}")


def normalize_server(
    server: dict, api_client: client.CherryServersClient, module: utils.AnsibleModule
) -> dict:
    """Normalize Cherry Servers server resource."""

    ips = []
    for ip in server.get("ip_addresses", []):
        ips.append(
            {
                "id": ip.get("id", None),
                "type": ip.get("type", None),
                "address": ip.get("address", None),
                "address_family": ip.get("address_family", None),
                "CIDR": ip.get("cidr", None),
            }
        )

    ssh_keys = []
    for ssh_key in server.get("ssh_keys", []):
        ssh_keys.append(ssh_key["id"])

    image_slug = get_server_image_slug(server, api_client, module)

    return {
        "hostname": server.get("hostname", None),
        "id": server.get("id", None),
        "image": image_slug,
        "image_full": server.get("image", None),
        "ip_addresses": ips,
        "name": server.get("name", None),
        "plan": server.get("plan", {}).get("slug", None),
        "project_id": server.get("project", {}).get("id", None),
        "region": server.get("region", {}).get("slug", None),
        "spot_market": server.get("spot_instance", None),
        "ssh_keys": ssh_keys,
        "status": server.get("status", None),
        "storage_id": server.get("storage", {}).get("id", None),
        "tags": server.get("tags", {}),
    }
