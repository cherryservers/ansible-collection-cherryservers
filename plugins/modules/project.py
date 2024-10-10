#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: project

short_description: Create and manage projects on Cherry Servers

version_added: "0.1.0"

description:
    - Create, update and delete projects on Cherry Servers.
    - To update existing projects, you must use O(id) or a combination of O(team_id) and O(name) to identify them.
    - When both are provided, O(id) will take priority over O(name).

options:
    state:
        description:
            - Project state.
        default: present
        choices: ['absent', 'present']
        type: str
    id:
        description:
            - ID of the project.
            - Cannot be set. Used to identify existing projects.
            - Required if project exists and O(name) is not provided.
        type: int
    team_id:
        description:
            - ID of the team the project belongs to.
            - Cannot be updated for an existing project.
            - Required if project exists and O(id) is not provided.
            - Required if project doesn't exist.
        type: int
    name:
        description:
            - Name of the project.
            - Can be used to identify existing projects.
            - Required if project exists and O(id) is not provided.
            - Required if project doesn't exist.
        type: str
    bgp:
        description:
            - Border Gateway Protocol enabled.
        type: bool
        default: false

extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Create a project
  cherryservers.cloud.project:
    auth_token: "{{ auth_token }}"
    name: 'ans-test'
    team_id: 148226
  register: result

- name: Update project
  cherryservers.cloud.project:
    auth_token: "{{ auth_token }}"
    name: "ans-test-updated"
    id: "{{ result.cherryservers_project.id }}"

- name: Delete project
  cherryservers.cloud.project:
    auth_token: "{{ auth_token }}"
    id: 123456
    state: absent
"""

RETURN = r"""
cherryservers_project:
    description: Project data.
    returned: when O(state=present) and not in check mode
    type: dict
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

from typing import Optional
from ansible.module_utils import basic as utils
from ..module_utils import standard_module
from ..module_utils.resource_managers import project_manager


class ProjectModule(standard_module.StandardModule):
    """Cherry Servers project module."""

    def __init__(self):
        super().__init__()
        self._project_manager = project_manager.ProjectManager(self._module)

    def _get_resource(self) -> Optional[dict]:
        resource = None
        params = self._module.params
        if params["id"]:
            resource = self._project_manager.get_by_id(params["id"])
        elif params["name"] and params["team_id"]:
            possible_projects = self._project_manager.get_by_team_id(params["team_id"])
            for project in possible_projects:
                if project["name"] == params["name"]:
                    resource = project

        return resource

    def _perform_deletion(self, resource: dict):
        self._project_manager.delete(resource["id"])

    def _perform_update(self, requests: dict, resource: dict) -> dict:
        if requests.get("update", None):
            self._project_manager.update(resource["id"], requests["update"])

        return self._project_manager.get_by_id(resource["id"])

    def _validate_creation_params(self):
        if (
            self._module.params["name"] is None
            or self._module.params["team_id"] is None
        ):
            self._module.fail_json(
                "name and team_id are required for creating projects."
            )

    def _get_update_requests(self, resource: dict) -> dict:
        req = {}
        params = self._module.params

        if params["name"] is not None and params["name"] != resource["name"]:
            req["name"] = params["name"]

        if params["bgp"] is not None and params["bgp"] != resource["bgp"]["enabled"]:
            req["bgp"] = params["bgp"]

        if req:
            return {"update": req}
        return {}

    def _perform_creation(self) -> dict:
        key = self._project_manager.create(
            team_id=self._module.params["team_id"],
            params={
                "name": self._module.params["name"],
                "bgp": self._module.params["bgp"],
            },
        )

        return self._project_manager.get_by_id(key["id"])

    @property
    def name(self) -> str:
        """Cherry Servers project module name."""
        return "cherryservers_project"

    @property
    def _arg_spec(self) -> dict:
        return {
            "state": {
                "choices": ["absent", "present"],
                "default": "present",
                "type": "str",
            },
            "id": {
                "type": "int",
            },
            "team_id": {
                "type": "int",
            },
            "name": {
                "type": "str",
            },
            "bgp": {
                "type": "bool",
                "default": False,
            },
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
            required_if=[
                ("state", "absent", ("id", "name"), True),
                ("state", "absent", ("id", "team_id"), True),
            ],
        )


def main():
    """Main function."""
    ProjectModule().run()


if __name__ == "__main__":
    main()
