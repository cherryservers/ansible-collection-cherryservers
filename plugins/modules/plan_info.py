#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type  # __metaclass__ is an exception to standard naming style, so pylint: disable=invalid-name.

DOCUMENTATION = r"""
---
module: plan_info

short_description: Information about available server plans

version_added: "3.1.0"

description:
  - Information about available server plans.
  - VAT adjusted according to your billing settings.

options:
    team_id:
        description:
            - Cherry Servers team ID.
        required: true
        type: int

extends_documentation_fragment:
  - cherryservers.cloud.cherryservers

author:
    - Martynas Deveikis (@caliban0)
"""

EXAMPLES = r"""
- name: Get plans
  cherryservers.cloud.plan_info:
    auth_token: "{{ auth_token }}"
    team_id: 123456
  register: result
"""

RETURN = r"""
cherryservers_plans:
  description: Plan data.
  returned: always
  type: list
  elements: dict
  contains:
    slug:
      description: Plan identifying reference slug.
      returned: always
      type: str
      sample: "e3-1240v3"
    type:
      description:
        - Indicates whether the plan is bare-metal or uses some kind of virtualization.
      returned: always
      type: str
      sample: "arm-vds"
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
    available_regions:
      description: Plan regional availability data.
      returned: always
      type: list
      elements: dict
      contains:
        slug:
          description: Region slug, used to identify and reference it.
          returned: always
          type: str
          sample: "JP-Tokyo"
        location:
          description: Region data center location.
          returned: always
          type: str
          sample: "Japan, Tokyo"
        stock_qty:
          description: The amount of servers in stock.
          returned: always
          type: int
          sample: 0
        spot_qty:
          description: The amount of servers in the spot market.
          returned: always
          type: int
          sample: 0
    operating_systems:
      description: The operating systems supported on this machine.
      returned: always
      type: list
      elements: str
      sample:
        - rockylinux_10_64bit
        - ubuntu_26_04_64bit
"""

from typing import List, Optional
from ansible.module_utils import basic as utils
from ..module_utils import info_module
from ..module_utils.resource_managers.plan_manager import PlanManager


class PlanInfoModule(info_module.InfoModule):
    """Server plan info info module.

    Retrieves data on available of server plans.
    """

    def __init__(self):
        super().__init__()
        self._resource_manager = PlanManager(self._module)

    def _filter(self, _resource: dict) -> bool:
        return True

    def _get_resource_list(self) -> List[dict]:
        params = self._module.params
        return self._resource_manager.list(params["team_id"])

    # Should never be called, as long as _resource_uniquely_identifiable always
    # returns False.
    def _get_single_resource(self) -> Optional[dict]:
        return None

    def _resource_uniquely_identifiable(self) -> bool:
        return False

    @property
    def name(self) -> str:
        """Plan info module name."""
        return "cherryservers_plans"

    @property
    def _arg_spec(self) -> dict:
        return {
            "team_id": {"type": "int", "required": True},
        }

    def _get_ansible_module(self, arg_spec: dict) -> utils.AnsibleModule:
        return utils.AnsibleModule(
            argument_spec=arg_spec,
            supports_check_mode=True,
        )


def main():
    """Main function."""
    PlanInfoModule().run()


if __name__ == "__main__":
    main()
