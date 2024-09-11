#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: storage_info

short_description: Gather information about your Cherry Servers EBS volumes

version_added: "0.1.0"

description:
  - Gather information about your Cherry Servers elastic block storage volumes.
  - Returns volumes that match all your provided options in the given project.
  - Alternatively, you can gather information directly by volume ID.

options:
    state:
        description:
            - The state of the volume.
        choices: ['attached', 'detached']
        type: str
    id:
        description:
            - ID of the volume.
            - Required if O(project_id) is not provided.
        type: int
    description:
        description:
            - User configured description of the volume.
        type: str
    project_id:
        description:
            - ID of the project the volume belongs to.
            - Required if O(id) is not provided.
        type: int
    region:
        description:
            - Slug of the volume region.
        type: str
    target_server_id:
        description:
            - ID of the server that the volume is attached to.
        type: int

extends_documentation_fragment:
  - local.cherryservers.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get a storage volume by ID
  local.cherryservers.storage_info:
    auth_token: "{{ auth_token }}"
    id: 123456
  register: result

- name: Get all project storage volumes
  local.cherryservers.storage_info:
    auth_token: "{{ auth_token }}"
    project_id: 123456
  register: result

- name: Get all project storage volumes, that are detached and have test description
  local.cherryservers.storage_info:
    auth_token: "{{ auth_token }}"
    project_id: 123456
    state: "detached"
    description: "test"
  register: result
"""

RETURN = r"""
cherryservers_storages:
  description: EBS storage volume data.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: EBS volume ID.
      returned: always
      type: int
      sample: 123456
    region:
      description: Slug of the region that the EBS volume belongs to.
      returned: always
      type: str
      sample: "eu_nord_1"
    size:
      description: Size of the volume, in GB.
      returned: always
      type: int
      sample: 100
    description:
      description: User defined volume description.
      returned: if exists
      type: str
      sample: "my storage"
    target_server_id:
      description: ID of the server that the volume is attached to.
      returned: if exists
      type: int
      sample: 123456
    vlan_id:
      description: ID of the EBS volume VLAN.
      returned: if exists
      type: str
      sample: "1234"
    vlan_ip:
      description: IP address of the EBS volume VLAN.
      returned: if exists
      type: str
      sample: "10.168.143.200"
    initiator:
      description: EBS volume initiator.
      returned: if exists
      type: str
      sample: "iqn.2019-03.com.cherryservers:initiator-123456-123456"
    portal_ip:
      description: EBS volume portal/discovery IP address.
      returned: if exists
      type: str
      sample: "10.168.143.200"
    name:
      description: EBS volume name.
      returned: always
      type: str
      sample: "cs-volume-123456-123456"
    state:
      description: EBS volume state. Can be 'attached' or 'detached'.
      returned: always
      type: str
      sample: "detached"
"""

from ansible.module_utils import basic as utils
from ..module_utils import client
from ..module_utils import common
from ..module_utils import constants
from ..module_utils import normalizers
from ..module_utils import info_module_base


class StorageInfoModule(info_module_base.InfoModuleBase):
    """Info module implementation for Cherry Servers EBS volumes.

    For more information, see base class documentation.
    """

    @property
    def _name(self) -> str:
        return "cherryservers_storages"

    @property
    def _timeout(self) -> int:
        return constants.STORAGE_TIMEOUT

    @property
    def _get_by_id_url(self) -> str:
        return "storages/{id}"

    def _filter(self, resource: dict) -> bool:
        params = self.module.params
        if all(
            params[k] is None or params[k] == resource[k]
            for k in ["id", "description", "region", "target_server_id", "state"]
        ):
            return True
        return False

    def _normalize(self, raw_resource: dict) -> dict:
        return normalizers.normalize_storage(raw_resource)

    @property
    def _get_by_project_id_url(self) -> str:
        return "projects/{project_id}/storages"


def run_module():
    """Execute the ansible module."""
    module_args = get_module_args()

    module = utils.AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_one_of=[("project_id", "id")],
    )

    api_client = client.CherryServersClient(module)

    StorageInfoModule(api_client, module).run()


def get_module_args() -> dict:
    """Return a dictionary with the modules argument specification."""
    module_args = common.get_base_argument_spec()

    module_args.update(
        {
            "state": {
                "choices": ["attached", "detached"],
                "type": "str",
            },
            "region": {"type": "str"},
            "id": {"type": "int"},
            "description": {"type": "str"},
            "project_id": {"type": "int"},
            "target_server_id": {"type": "int"},
        }
    )

    return module_args


def main():
    """Main function."""
    run_module()


if __name__ == "__main__":
    main()
