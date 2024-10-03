# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
name: cherryservers
short_description: Cherry Servers inventory plugin.
description:
  - Cherry Servers inventory plugin.
  - Get project server list.
  - Configuration file must end with C(cherryservers.yml) or C(cherryservers.yaml).
author:
  - Martynas Deveikis (@caliban0)
version_added: "0.1.0"
requirements:
  - python >= 3.9
extends_documentation_fragment:
  - inventory_cache
  - constructed

options:
  plugin:
    description:
      - Inventory plugin to use.
      - Should always be V(cherryservers.cloud.cherryservers).
    required: true
    choices: ['cherryservers.cloud.cherryservers']
  auth_token:
    description:
      - API authentication token for Cherry Servers public API.
      - Can be supplied via E(CHERRY_AUTH_TOKEN) and E(CHERRY_AUTH_KEY) environment variables.
    type: str
    required: true
    env:
      - name: CHERRY_AUTH_TOKEN
      - name: CHERRY_AUTH_KEY
  project_id:
    description:
      - ID of the project to get servers from.
    type: int
    required: true
  variable_prefix:
    description:
      - Host variable prefix.
    type: str
    default: "cs_"
  region:
    description:
      - Populate inventory with instances that belong to this region slug.
    type: str
    required: false
  status:
    description:
      - Populate inventory with instances that have this status,
      - for example V(deployed).
    type: str
    required: false
  tags:
    description:
      - Populate inventory with instances that have these tags.
    type: dict
    required: false
"""

EXAMPLES = """
# Get all servers from a project.
plugin: cherryservers.cloud.cherryservers
project_id: 123456
auth_token: "my_api_key"

# Get all servers from a specified region and that have the specified tags.
plugin: cherryservers.cloud.cherryservers
project_id: 123456
auth_token: "my_api_key"
region: "eu_nord_1"
tags:
  env: "test"

# Use grouping.
plugin: cherryservers.cloud.cherryservers
project_id: 123456
auth_token: "my_api_key"
keyed_groups:
  - key: cs_region
    prefix: region
    separator: "_"
groups:
  deployed: "cs_status == 'deployed'"
"""

import json

from ansible.errors import AnsibleParserError
from ansible.module_utils.urls import Request
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, Constructable
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ..module_utils import normalizers


class InventoryModule(BaseInventoryPlugin, Cacheable, Constructable):
    """Inventory plugin class for Cherry Servers."""

    NAME = "cherryservers.cloud.cherryservers"

    def verify_file(self, path):
        """Determine if the inventory source file is valid."""
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(("cherryservers.yml", "cherryservers.yaml")):
                valid = True

        return valid

    def _get_inventory(self):
        auth_token = self.get_option("auth_token")
        auth_token = self.templar.template(auth_token)

        project_id = self.get_option("project_id")
        project_id = self.templar.template(project_id)

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        url = f"https://api.cherryservers.com/v1/projects/{project_id}/servers"

        req = Request(headers=headers, timeout=30)

        try:
            response = json.load(req.get(url))
        except (URLError, HTTPError) as e:
            raise AnsibleParserError(e) from e

        return response

    def _filter(self, server: dict) -> bool:
        region = self.get_option("region")
        status = self.get_option("status")
        tags = self.get_option("tags")

        exclude = False

        if region and region != server["region"]:
            exclude = True

        if status and status != server["status"]:
            exclude = True

        if tags and not tags.items() <= server["tags"].items():
            exclude = True

        return exclude

    def _populate(self, servers):
        variable_prefix = self.get_option("variable_prefix")
        strict = self.get_option("strict")

        for server in servers:
            server = normalizers.normalize_server(server)
            if self._filter(server):
                continue
            self.inventory.add_host(server["hostname"])
            host_vars = {}
            for k, v in server.items():
                host_vars[variable_prefix + k] = v
            for k, v in host_vars.items():
                self.inventory.set_variable(server["hostname"], k, v)

            self._set_composite_vars(
                self.get_option("compose"), host_vars, server["hostname"], strict=True
            )

            self._add_host_to_composed_groups(
                self.get_option("groups"), host_vars, server["hostname"], strict=strict
            )
            self._add_host_to_keyed_groups(
                self.get_option("keyed_groups"),
                host_vars,
                server["hostname"],
                strict=strict,
            )

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        self._read_config_data(path)
        cache_key = self.get_cache_key(path)

        user_cache_setting = self.get_option("cache")
        attempt_to_read_cache = user_cache_setting and cache
        cache_needs_update = user_cache_setting and not cache

        servers = None
        if attempt_to_read_cache:
            try:
                servers = self._cache[cache_key]
            except KeyError:
                cache_needs_update = True
        if not attempt_to_read_cache or cache_needs_update:
            servers = self._get_inventory()
        if cache_needs_update and servers:
            self._cache[cache_key] = servers

        self._populate(servers)
