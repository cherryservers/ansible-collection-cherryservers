# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Cherry Servers resource normalizers.

These normalizers help prepare various Cherry Servers resources for working with ansible modules.

Functions:

    normalize_ip(ip: dict): Normalize an IP resource.

"""


def normalize_ssh_key(key: dict) -> dict:
    """TODO"""
    return {
        "id": key.get("id", None),
        "label": key.get("label", None),
        "key": key.get("key", None),
        "fingerprint": key.get("fingerprint", None),
        "updated": key.get("updated", None),
        "created": key.get("created", None),
    }


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


def normalize_storage(storage: dict) -> dict:
    """Normalize Cherry Servers storage resource."""
    description = storage.get("description", None)
    if description == "":
        description = None

    target_server_id = storage.get("attached_to", {}).get("id", None)
    state = "detached"
    if target_server_id is not None:
        state = "attached"

    return {
        "id": storage.get("id", None),
        "region": storage.get("region", {}).get("slug", None),
        "size": storage.get("size", None),
        "description": description,
        "target_server_id": target_server_id,
        "vlan_id": storage.get("vlan_id", None),
        "vlan_ip": storage.get("vlan_ip", None),
        "initiator": storage.get("initiator", None),
        "portal_ip": storage.get("discovery_ip", None),
        "name": storage.get("name", None),
        "state": state,
    }


def normalize_server(
    server: dict,
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

    return {
        "hostname": server.get("hostname", None),
        "id": server.get("id", None),
        "image": server.get("deployed_image", {}).get("slug", None),
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
