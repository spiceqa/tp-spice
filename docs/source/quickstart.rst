============
Quick start.
============

* Put here documentation.
* Check with: http://rst.ninjs.org/

Installation
============

::

        # yum install avocado avocado-plugins-vt
        $ avocado vt-bootstrap

Make guest VM image
-------------------

::

        # avocado run --vt-guest-os Linux.RHEL.7.devel --vt-extra-params 'url=http://download.eng.brq.redhat.com/rel-eng/$RHELVERSION/compose/Server/x86_64/os/' --show-job-log  -- unattended_install.url.http_ks.default_install


qcow2 VM guest image is then stored in ~/avocado/data/avocado-vt/images/

Beaker initialization
---------------------

1. Login to beaker
2. Go to user preferences -> SSH Public Keys and upload your id_rsa ssh public key, store your ssh private key to safe place and do not forget its  password
3. 

- job is run on beaker machine in /mnt/tests/spice/qe-tests/avocado-data directory

First look
==========

  **Directories**

  - ssh to beaker machine, then you'll find:

  +-----------------------+------------------------------------------+
  |  Avocado job run      |  /mnt/tests/spice/qe/tests/avocado-data  |
  +------------------------------------------------------------------+
  |  Avocado logs         |  /mnt/tests/spice/qe/tests/avocado-logs  |
  +------------------------------------------------------------------+
  |  Avocado git repo     |  /mnt/tests/spice/qe/tests/avocado       |
  +------------------------------------------------------------------+
  |  Avocado-vt git repo  |  /mnt/tests/spice/qe/tests/avocado-vt    |
  +-----------------------+------------------------------------------+

 - Avocado logs are also accessible also through beaker server (go to IP address of beaker server through your web browser)
