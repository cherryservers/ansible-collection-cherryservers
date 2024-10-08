# Cherry Servers Ansible Collection

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/caliban0/cherryservers-ansible-collection/graph/badge.svg?token=WQ8P3OKBCZ)](https://codecov.io/gh/caliban0/cherryservers-ansible-collection)

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
      local.cherryservers.server:
        project_id: 216063
        region: "eu_nord_1"
        plan: "cloud_vps_1"
        auth_token: "my-auth-token-goes-here"
```

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

More information on Ansible collection testing can be found [here](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_testing.html).

## Release notes
TBD