#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: prebuilt_info

short_description: Information about available prebuilt server plans

version_added: "3.1.0"

description:
  - Information about available prebuilt server plans.
  - Prebuilt plans are plan variations that are available on-site, with no extra assembly.
  - VAT adjusted according to your billing settings.

options:
    team_id:
        description:
            - Cherry Servers team ID.
        required: true
        type: int
    plan:
        description:
            - Slug of the base plan.
        required: true
        type: str
    region:
        description:
            - Slug of the region.
        required: true
        type: str

extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get a plan variations for amd-epyc-9355
  cherryservers.cloud.prebuilt_info:
    team_id: 123456
    plan: "amd-epyc-9355"
    region: "LT-Siauliai"
  register: result
"""

RETURN = r"""
cherryservers_prebuilts:
  description: Prebuilt plan data.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Prebuilt plan ID.
      returned: always
      type: int
      sample: 7955
    stock_qty:
      description: Amount of stock for this prebuilt plan.
      returned: always
      type: int
      sample: 1
    specs:
      description: Plan machine hardware specification.
      returned: always
      type: dict
      contains:
        cpus:
          description: Machine CPU specification.
          returned: always
          type: dict
          contains:
            count:
              description: Amount of CPUs in this machine.
              returned: always
              type: int
              sample: 1
            name:
              description: CPU name.
              returned: always
              type: str
              sample: "E5-1650v4"
            cores:
              description: Amount of cores per CPU.
              returned: always
              type: int
              sample: 6
            frequency:
              description: Core frequency.
              returned: always
              type: float
              sample: 3.6
            unit:
              description: Core frequency unit.
              returned: always
              type: str
              sample: "GHz"
        memory:
          description: Machine memory specification.
          returned: always
          type: dict
          contains:
            count:
              description: Amount of memory modules.
              returned: always
              type: int
              sample: 1
            total:
              description: Total amount of memory.
              returned: always
              type: int
              sample: 64
            unit:
              description: Memory units.
              returned: always
              type: str
              sample: "GB"
            name:
              description: Memory module name.
              returned: always
              type: str
              sample: "64GB ECC REG DDR4"
        storage:
          description: Machine storage specification.
          returned: always
          type: list
          elements: dict
          contains:
            count:
              description: Amount of storage devices.
              returned: always
              type: int
              sample: 2
            name:
              description: Storage device name.
              returned: always
              type: str
              sample: "SSD 500GB"
            size:
              description: Storage device size.
              returned: always
              type: int
              sample: 500
            unit:
              description: Storage device size measurement unit.
              returned: always
              type: str
              sample: "GB"
            type:
              description: Storage device type.
              returned: always
              type: str
              sample: "SSD"
        nics:
          description: Machine NIC specification.
          returned: always
          type: dict
          contains:
            name:
              description: NIC name.
              returned: always
              type: str
              sample: "3Gbps"
    traffic:
        description: Plan monthly egress traffic limit.
        returned: always
        type: str
        sample: "30TB"
    pricing:
      description: Plan pricing specification.
      returned: always
      type: list
      elements: dict
      contains:
        unit:
          description: Billing cycle unit.
          returned: always
          type: str
          sample: "Monthly"
        price:
          description: Server price, for the relevant billing period.
          returned: always
          type: float
          sample: 228.69
        currency:
          description: Price currency.
          returned: always
          type: str
          sample: "EUR"
"""

from typing import List, Optional
from ansible.module_utils import basic as utils
from ..module_utils import info_module
from ..module_utils.resource_managers.prebuilt_manager import PrebuiltManager


class PrebuiltInfoModule(info_module.InfoModule):
    """Prebuilt plan info module.

    Retrieves data on available prebuilt variations of server plans.
    """

    def __init__(self):
        super().__init__()
        self._resource_manager = PrebuiltManager(self._module)

    def _filter(self, _resource: dict) -> bool:
        return True

    def _get_resource_list(self) -> List[dict]:
        params = self._module.params
        return self._resource_manager.list(
            params["team_id"], params["plan"], params["region"]
        )

    # Should never be called, as long as _resource_uniquely_identifiable always
    # returns False.
    def _get_single_resource(self) -> Optional[dict]:
        return None

    def _resource_uniquely_identifiable(self) -> bool:
        return False

    @property
    def name(self) -> str:
        """Prebuilt info module name."""
        return "cherryservers_prebuilts"

    @property
    def _arg_spec(self) -> dict:
        return {
            "team_id": {"type": "int", "required": True},
            "plan": {"type": "str", "required": True},
            "region": {"type": "str", "required": True},
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
        )


def main():
    """Main function."""
    PrebuiltInfoModule().run()


if __name__ == "__main__":
    main()
