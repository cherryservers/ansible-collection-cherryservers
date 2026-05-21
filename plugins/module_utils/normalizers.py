# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Cherry Servers resource normalizers."""


def normalize_ssh_key(key: dict) -> dict:
    """Normalize a Cherry Servers SSH key resource."""
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


def normalize_project(project: dict) -> dict:
    """Normalize Cherry Servers project resource."""

    return {
        "id": project.get("id", None),
        "name": project.get("name", None),
        "bgp": project.get("bgp", None),
    }


def normalize_prebuilt_plan(plan: dict) -> dict:
    """Normalize Cherry Servers prebuilt plan resource."""

    cpu = plan.get("specs", {}).get("cpus", {})
    memory = plan.get("specs", {}).get("memory", {})
    storage = plan.get("specs", {}).get("storage", [])
    nics = plan.get("specs", {}).get("nics", {})
    traffic = plan.get("specs", {}).get("bandwidth", {}).get("name")

    return {
        "id": plan.get("id"),
        "stock_qty": plan.get("stock_qty"),
        "specs": {
            "cpus": {
                "count": cpu.get("count"),
                "name": cpu.get("name"),
                "cores": cpu.get("cores"),
                "frequency": cpu.get("frequency"),
                "unit": cpu.get("unit"),
            },
            "memory": {
                "count": memory.get("count"),
                "total": memory.get("total"),
                "unit": memory.get("unit"),
                "name": memory.get("name"),
            },
            "storage": [
                {
                    "count": x.get("count"),
                    "name": x.get("name"),
                    "size": x.get("size"),
                    "unit": x.get("unit"),
                    "type": x.get("type"),
                }
                for x in storage
            ],
            "nics": {
                "name": nics.get("name"),
            },
        },
        "traffic": traffic,
        "pricing": [
            {
                "unit": x.get("unit"),
                "price": x.get("price"),
                "currency": x.get("currency"),
            }
            for x in plan.get("pricing", [])
        ],
    }
