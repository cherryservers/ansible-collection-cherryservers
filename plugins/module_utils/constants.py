# Copyright: (c) 2024, Cherry Servers UAB <info@cherryservers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

SSH_TIMEOUT = 10
IP_TIMEOUT = 30

# Module parameter and resource key sequence orders must match.

SSH_MODULE_PARAM_KEYS = ("id", "fingerprint", "label", "public_key")
SSH_RESOURCE_KEYS = ("id", "fingerprint", "label", "key")

SSH_MODULE_PARAM_IDENTIFYING_KEYS = ("id", "fingerprint", "label", "public_key")
SSH_RESOURCE_IDENTIFYING_KEYS = ("id", "fingerprint", "label", "key")
SSH_IDENTIFYING_KEYS = (
    SSH_RESOURCE_IDENTIFYING_KEYS,
    SSH_MODULE_PARAM_IDENTIFYING_KEYS,
)
