=================================
Cherryservers.Cloud Release Notes
=================================

.. contents:: Topics

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
