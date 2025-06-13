=================================
Cherryservers.Cloud Release Notes
=================================

.. contents:: Topics

v2.0.0
======

Breaking Changes / Porting Guide
--------------------------------

- Drop support for Python 3.9. This is required to drop support for ansible-core 2.15, which is at EOF.
- Drop support for ansible-core 2.16. This drops support for Python 3.9 as well, since ansible-core 2.16 requires at least 3.10.

v1.1.0
======

Bugfixes
--------

- Increase default request timeout lengths, the previous ones would often cause unnecessary timeouts.
- On server reinstall, set SSH keys and images to their previous values, if they haven't been changed or are unprovided.
- Wait for server to become active, if ``state`` is set to active, on server reinstall.
- remove ddos_scrubbing option from the floating_ip module, since upstream API changes have made it unusable.
- test - Properly delete floating IP after using it for server integration tests.

v1.0.0
======

New Modules
-----------

- cherryservers.cloud.floating_ip - Create and manage floating IPs on Cherry Servers.
- cherryservers.cloud.floating_ip_info - Gather information about your Cherry Servers floating IPs.
- cherryservers.cloud.project - Create and manage projects on Cherry Servers.
- cherryservers.cloud.project_info - Gather information about your Cherry Servers projects.
- cherryservers.cloud.server - Create and manage servers on Cherry Servers.
- cherryservers.cloud.server_info - Gather information about your Cherry Servers servers.
- cherryservers.cloud.sshkey - Create and manage SSH keys on Cherry Servers.
- cherryservers.cloud.sshkey_info - Gather information about your Cherry Servers SSH keys.
- cherryservers.cloud.storage - Create and manage elastic block storage volumes on Cherry Servers.
- cherryservers.cloud.storage_info - Gather information about your Cherry Servers EBS volumes.
