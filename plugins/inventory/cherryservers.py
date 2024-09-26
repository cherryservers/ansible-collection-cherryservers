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
  
options:
  plugin:
    description:
      - Inventory plugin to use.
      - Should always be O(local.cherryservers.cherryservers).
    required: true
    choices: ['local.cherryservers.cherryservers']
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
      - ID of the project to get server list for.
    type: int
    required: true
  variable_prefix:
    description:
      - Host variable prefix.
    type: str
    default: "cs_"
  
"""

import json

from ansible.errors import AnsibleParserError
from ansible.module_utils.urls import Request
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ..module_utils import normalizers

class InventoryModule(BaseInventoryPlugin, Cacheable):
    NAME = "local.cherryservers.cherryservers"

    def verify_file(self, file_path):
        valid = False
        if super(InventoryModule, self).verify_file(file_path):
            if file_path.endswith(("cherryservers.yml", "cherryservers.yaml")):
                valid = True

        return valid

    def get_inventory(self):
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

    def populate(self, servers):
        variable_prefix = self.get_option("variable_prefix")
        for server in servers:
            self.inventory.add_host(server["hostname"])
            server = normalizers.normalize_server(server)
            host_vars = {}
            for k, v in server.items():
                host_vars[variable_prefix + k] = v
            for k, v in host_vars.items():
                self.inventory.set_variable(server["hostname"], k, v)

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
            servers = self.get_inventory()
        if cache_needs_update and servers:
            self._cache[cache_key] = servers

        self.populate(servers)
