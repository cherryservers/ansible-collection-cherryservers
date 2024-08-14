#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: server

short_description: Create and manage servers on Cherry Servers

version_added: "0.1.0"

description:
    - Create, update and delete floating IPs on Cherry Servers.
    - If you wish to update or delete existing floating IPs,
    - you must provide O(id) or the combination of O(project_id) and O(address),
    - as identifiers, along with state and other desired options.
    - If you wish to create new floating IPs,
    - you must provide O(project_id) and O(region_slug) along other desired options.

options:
    state:
        description:
            - The state of the server.
            - V(present) will ensure the server exists.
            - V(absent) will ensure the server does not exist.
            - V(rescue) will ensure the server exists and is in rescue mode.
            - V(rebooted) will ensure the server exists and is rebooted.
            - V(running) will ensure the server exists, is powered on and running.
            - V(stopped) will ensure the server exists and is powered off.
        choices: ['present', 'absent', 'rescue', 'rebooted', 'running', 'stopped']
        type: str
        default: present
    project_id:
        description:
            - The ID of the project the server belongs to.
            - Required if not O(state=absent) and server doesn't exist.
            - Only used on server creation.
        type: str
    plan_slug:
        description:
            - Slug of the server plan.
            - Required if not O(state=absent) and server doesn't exist.
            - Only used on server creation.
        aliases: [plan]
        type: str
    image_slug:
        description:
            - Slug of the server image.
            - Only used on server creation.
        aliases: [image]
        type: str
    os_partition_size:
        description:
            - Server OS partition size in GB.
            - Only used on server creation.
        type: int
    region_slug:
        description:
            - Slug of the server region.
            - Required if not O(state=absent) and server doesn't exist.
            - Only used on server creation.
        type: str
    hostname:
        description:
            - Server hostname.
        type: str
    ssh_keys:
        description:
            - SSH key IDs or labels, that are added to the server.
            - Only used on server creation and for rescue mode.
        type: list
        elements: str
    extra_ips:
        description:
            - Extra floating IP IDs or addresses to add to the server.
            - Only used on server creation.
        type: list
        elements: str
    user_data_file:
        description:
            - Path to a userdata file for server initialization.
            - Only used on server creation.
        type: str
    tags:
        description:
            - Server tags.
        type: dict
    spot_market:
        description:
            - Whether the server is a spo instance.
        type: bool
        default: false
    storage_id:
        description:
            - Elastic block storage ID.
        type: int
            
    
    

extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create a floating IP
  local.cherryservers.floating_ip:
    project_id: "213668"
    region_slug: "eu_nord_1"
    target_server_id: "590738"
    ptr_record: "moduletestptr"
    a_record: "moduletesta"
    tags:
      env: "test"
  register: result

- name: Update a floating IP by using its ID
  local.cherryservers.floating_ip:
    id: "a0ff92c9-21f6-c387-33d0-5c941c0435f0"
    target_server_id: 590738
    ptr_record: "anstest"
    a_record: "anstest"
    tags:
      env: "test"
  register: result

- name: Update a floating IP by using its address and project ID.
  local.cherryservers.floating_ip:
    address: "5.199.174.84"
    project_id: 213668
    target_server_id: 0
    ptr_record: ""
    a_record: ""
  register: result

- name: Delete floating IP
  local.cherryservers.floating_ip:
    state: absent
    id: "497f6eca-6276-4993-bfeb-53cbbbba6f08"
"""

RETURN = r"""
cherryservers_floating_ip:
  description: Floating IP data.
  returned: O(state=present) and not in check mode
  type: dict
  contains:
    a_record:
      description: DNS A record.
      returned: if exists
      type: str
      sample: "test.cloud.cherryservers.net."
    address:
      description: IP address.
      returned: always
      type: str
      sample: "5.199.174.84"
    cidr:
      description: CIDR notation.
      returned: always
      type: str
      sample: "5.199.174.84/32"
    id:
      description: ID of the IP address.
      returned: always
      type: str
      sample: "a0ff92c9-21f6-c387-33d0-5c941c0435f0"
    ptr_record:
      description: DNS pointer record.
      returned: if exists
      type: str
      sample: "test."
    region_slug:
      description: Slug of the region which the IP belongs to.
      returned: always
      type: str
      sample: "eu_nord_1"
    tags:
      description: Tags of the floating IP.
      returned: always
      type: dict
      sample:
        env: "dev"
    target_server_id:
      description: ID of the server to which the floating IP is targeted to.
      returned: if exists
      type: int
      sample: "123456"
    route_ip_id:
      description: ID of the IP to which the floating IP is routed to.
      returned: if exists
      type: str
      sample: "fe8b01f4-2b85-eae9-cbfb-3288c507f318"
"""
