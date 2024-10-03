# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


class ModuleDocFragment:  # pylint: disable=missing-class-docstring, too-few-public-methods
    DOCUMENTATION = r"""
    options:
      auth_token:
        description:
          - API authentication token for Cherry Servers public API.
          - Can be supplied via E(CHERRY_AUTH_TOKEN) and E(CHERRY_AUTH_KEY) environment variables.
        type: str

    requirements:
      - python >= 3.9

    seealso:
      - name: Cherry Servers API documentation
        description: Complete reference for Cherry Servers public API.
        link: https://api.cherryservers.com/doc/
      - name: Cherry Servers authentication token generation
        description: website link for generating API tokens.
        link: https://portal.cherryservers.com/settings/ssh-keys
    """
