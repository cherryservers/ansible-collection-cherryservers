# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Cherry Servers resource normalizers.

These normalizers help prepare various Cherry Servers resources for working with ansible modules.

Functions:

    normalize_ip(ip: dict): Normalize an IP resource.

"""


def normalize_ip(ip: dict):
    """Normalize Cherry Servers IP resource.

    Modifies field keys to match module parameter keys,
    ensures that all keys have a value, even if it's None.
    Also, removes unnecessary keys.

    Args:

        ip (dict): Cherry Servers IP resource. This dictionary will be modified.
    """
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
    target_id = ip.get("targeted_to", {}).get("id", None)
    route_id = ip.get("routed_to", {}).get("id", None)
    region_slug = ip.get("region", {}).get("slug")
    for t in to_trim:
        ip.pop(t, None)

    ip["target_server_id"] = target_id
    ip["route_ip_id"] = route_id
    ip["region_slug"] = region_slug

    ip["ptr_record"] = ip.get("ptr_record", None)
    ip["a_record"] = ip.get("a_record", None)
