# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


class ModuleDocFragment:  # pylint: disable=missing-class-docstring, too-few-public-methods
    DOCUMENTATION = r"""
    options:
      api_key:
        description:
          - API key for Cherry Servers public API.
          - Can also be supplied via the E(CHERRY_API_KEY) environment variable.
          - The alias C(auth_token) is B(deprecated) and will be removed in C(v4.0.0),
            along with the environment variables E(CHERRY_AUTH_TOKEN) and E(CHERRY_AUTH_KEY).
        type: str
        aliases: [auth_token]
        required: true

    requirements:
      - python >= 3.11

    seealso:
      - name: Cherry Servers API documentation
        description: Complete reference for Cherry Servers public API.
        link: https://api.cherryservers.com/doc/
      - name: Cherry Servers API key generation
        description: Generate Cherry Servers API keys.
        link: https://portal.cherryservers.com/settings/api-keys
    """
