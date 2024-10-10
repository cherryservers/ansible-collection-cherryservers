#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: project_info

short_description: Gather information about your Cherry Servers projects

version_added: "0.1.0"

description:
  - Gather information about your Cherry Servers projects.
  - Returns projects that match all your provided options in the given team.
  - Alternatively, you can gather information directly by project ID.

options:
    id:
        description:
            - ID of the project.
            - Required if O(team_id) is not provided.
        type: int
    team_id:
        description:
            - ID of the team the project belongs to.
            - Required if O(id) is not provided.
        type: int
    name:
        description:
            - Project name.
        type: str
    bgp:
        description:
            - Whether the project has BGP enabled.
        type: bool

extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get a project by ID
  cherryservers.cloud.project_info:
    auth_token: "{{ auth_token }}"
    id: 123456
  register: result

- name: Get all team projects
  cherryservers.cloud.project_info:
    auth_token: "{{ auth_token }}"
    team_id: 123456
  register: result

- name: Get all team projects that have BGP disabled
  cherryservers.cloud.project_info:
    auth_token: "{{ auth_token }}"
    team_id: 123456
    bgp: False
  register: result
"""

RETURN = r"""
cherryservers_projects:
  description: Project data.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Project ID.
      returned: always
      type: int
      sample: 7955
    name:
      description: Project name.
      returned: always
      type: str
      sample: "my-project"
    bgp:
      description: Project BGP data.
      returned: always
      type: dict
      contains:
        enabled:
          description: Whether BGP is enabled for the project.
          returned: always
          type: bool
          sample: True
        local_asn:
          description: Project local ASN.
          returned: always
          type: int
          sample: 0
"""

from typing import List, Optional
from ansible.module_utils import basic as utils
from ..module_utils import info_module
from ..module_utils.resource_managers.project_manager import ProjectManager


class ProjectInfoModule(info_module.InfoModule):
    """Project info module."""

    def __init__(self):
        super().__init__()
        self._resource_manager = ProjectManager(self._module)

    def _filter(self, resource: dict) -> bool:
        params = self._module.params
        if all(
            params[k] is None or params[k] == resource[k] for k in ["id", "name"]
        ) and (params["bgp"] is None or params["bgp"] == resource["bgp"]["enabled"]):
            return True
        return False

    def _get_resource_list(self) -> List[dict]:
        return self._resource_manager.get_by_team_id(self._module.params["team_id"])

    def _get_single_resource(self) -> Optional[dict]:
        return self._resource_manager.get_by_id(self._module.params["id"])

    def _resource_uniquely_identifiable(self) -> bool:
        if self._module.params["id"] is None:
            return False
        return True

    @property
    def name(self) -> str:
        """Project info module name."""
        return "cherryservers_projects"

    @property
    def _arg_spec(self) -> dict:
        return {
            "id": {"type": "int"},
            "team_id": {"type": "int"},
            "name": {"type": "str"},
            "bgp": {"type": "bool"},
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
            required_one_of=[("team_id", "id")],
        )


def main():
    """Main function."""
    ProjectInfoModule().run()


if __name__ == "__main__":
    main()
