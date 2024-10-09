# Cherry Servers Ansible Collection

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/caliban0/cherryservers-ansible-collection/graph/badge.svg?token=WQ8P3OKBCZ)](https://codecov.io/gh/caliban0/cherryservers-ansible-collection)
[![galaxy](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fgalaxy.ansible.com%2Fapi%2Fv3%2Fplugin%2Fansible%2Fcontent%2Fpublished%2Fcollections%2Findex%2Fcherryservers%2Fcloud%2F&query=highest_version.version&label=galaxy)](https://galaxy.ansible.com/ui/repo/published/cherryservers/cloud/)

Cherry Servers Ansible collection for managing infrastructure and resources.

## Installation and Usage

### Requirements

- ansible-core >= 2.14
- python >= 3.9

### Installation

Use Ansible Galaxy CLI to install the collection:

```shell
ansible-galaxy collection install cherryservers.cloud
```

### Usage

Before using the collection, you need to generate an API token from
the [Cherry Servers client portal](https://portal.cherryservers.com/settings/api-keys).
You can supply the token with the `auth_token` attribute or by setting `CHERRY_AUTH_TOKEN` (or `CHERRY_AUTH_KEY`)
environment variables.

### Example playbook

```yaml
---
- name: Create a Cherry Servers server
  hosts: localhost
  tasks:
    - name: Create a server
      cloud.cherryservers.server:
        project_id: 216063
        region: "eu_nord_1"
        plan: "cloud_vps_1"
        auth_token: "my-auth-token-goes-here"
```

## Included content

### Modules

```text
server
server_info
floating_ip
floating_ip_info
sshkey
sshkey_info
storage
storage_info
```

### Inventory plugins

```cherryservers```

## Documentation

The full documentation can be found
on [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/cherryservers/cloud/docs/).
Documentation for separate modules and plugins can also be accessed with `ansible-doc`.

For example: `ansible-doc cherryservers.cloud.server` will display documentation for the `server` module.

## Development

The collection should be placed in the Ansible collection path, which is usually
`~/.ansible/collections/ansible_collections/<namespace>/collection`.
You can either clone the repository there directly, or, clone the repository anywhere, build with
`ansible-galaxy collection build` (from the collection directory)
and install with `ansible-galaxy collection install <path-to-collection-file>`.

For more information, refer to Ansible documentation
on [collection development](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html).

## Testing

Testing can be done with `ansible-test`. For example, to launch sanity tests, you can use:

```shell
ansible-test sanity --docker default -v
```

To perform integration tests, an `integration_config.yml` file must be created in the `tests/integration/` directory.
This file must declare `cherryservers_api_key`, `cherryservers_project_id` and, optionally,
`cherryservers_baremetal_server_id`(used for storage testing).

You can run the whole suite of integration tests with, for example:

```shell
ansible-test integration --docker fedora39 -vvv
```

You can also run integration tests for specific modules, for example:

```shell
ansible-test integration server --docker fedora39 -vvv
```

More information on Ansible collection testing can be
found [here](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_testing.html).

## Release notes

See the [changelog](CHANGELOG.md).

### Release process

1. Update `_VERSION` in `plugins/module_utils/_version.py`.
2. Update the human-readable `CHANGELOG.md`.
3. Update version in `galaxy.yml`.
4. If there are new modules or plugins, update the [Included content](#included-content) section of this document.
5. Tag the new version and push it.