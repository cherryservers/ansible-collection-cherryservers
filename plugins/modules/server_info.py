#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: server_info

short_description: Gather information about your Cherry Servers servers

version_added: "0.1.0"

description:
  - Gather information about your Cherry Servers servers.
  - Returns servers that match all your provided options in the given project.
  - Alternatively, you can get a single server by specifying its ID.

options:
    id:
        description:
            - ID of the server.
        type: int
    project_id:
        description:
            - The ID of the project the server belongs to.
            - Required if O(id) is not provided.
        type: str
    plan:
        description:
            - Slug of the server plan.
        type: str
    image:
        description:
            - Slug of the server image.
        type: str
    region:
        description:
            - Slug of the server region.
        type: str
    hostname:
        description:
            - Server hostname.
        type: str
    ssh_keys:
        description:
            - SSH key IDs, that are added to the server.
        type: list
        elements: str
    tags:
        description:
            - Server tags.
        type: dict
    spot_market:
        description:
            - Whether the server is a spot instance.
        type: bool
        default: false
    storage_id:
        description:
            - Elastic block storage ID.
            - TODO.
        type: int
extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

RETURN = r"""
cherryservers_floating_ips:
  description: Floating IP data.
  returned: always
  type: list
  elements: dict
  contains:
    hostname:
      description: Server hostname.
      returned: always
      type: str
      sample: "honest-toucan"
    id:
      description: Server ID.
      returned: always
      type: int
      sample: "123456"
    image:
      description: Image of the server operating system.
      returned: always
      type: str
      sample: "Fedora 39 64bit"
    ip_addresses:
      description: Server IP addresses.
      returned: always
      type: list
      elements: dict
      contains:
        CIDR:
          description: CIDR block of the IP.
          returned: always
          type: str
          sample: "10.168.101.0/24"
        address:
          description: IP address.
          returned: always
          type: str
          sample: "10.168.101.0"
        address_family:
          description: IP address family (IPv4 or IPv6).
          returned: always
          type: int
          sample: 4
        id:
          description: IP address ID.
          returned: always
          type: str
          sample: "16a70e80-d338-1b1e-f6ef-d5aacf9f3718"
        type:
          description: IP address type.
          returned: always
          type: str
          sample: "floating-ip"
    name:
      description: Server name.
      returned: always
      type: str
      sample: "Cloud VPS 1"
    plan:
      description: Slug of the server plan.
      returned: always
      type: str
      sample: "cloud_vps_1"
    project_id:
      description: Cherry Servers project ID, associated with the server.
      returned: always
      type: int
      sample: 123456
    region:
      description: Slug of the server region.
      returned: always
      type: str
      sample: "eu_nord_1"
    spot_market:
      description: Whether the server is a spot market instance.
      returned: always
      type: bool
      sample: false
    ssh_keys:
      description: Set of the SSH key IDs allowed to SSH to the server.
      returned: always
      type: list
      elements: int
      sample: [0000, 1111]
    status:
      description: Server status.
      returned: always
      type: str
      sample: "deploying"
    storage_id:
      description: Server storage block ID. Null if doesn't exist.
      returned: always
      type: int
      sample: 593063
    tags:
      description: Key/value metadata for server tagging.
      returned: always
      type: dict
      sample:
        env: "dev"
"""

def run_module():
    """Execute the ansible module."""

def main():
    """Main function."""
    run_module()


if __name__ == "__main__":
    main()
