* Put here documentation.
* Check with: http://rst.ninjs.org/

############
Installation
############

You can manually  install avocado on your local machine, or you can exploit Beaker stable system and workflow-tomorrow parameter

**************************
Local machine installation
**************************

To run tests provided by tp-spice you must first install avocado, avocado-vt and all its dependencies (`Avocado installation <http://avocado-framework.readthedocs.io/en/latest/GetStartedGuide.html#installing-avocado>`_).

 1. Enable repository

::

        # cat  << EOF > /etc/yum.repos.d/avocado.repo
        [avocado]
        name=Avocado
        baseurl=https://repos-avocadoproject.rhcloud.com/static/epel-$releasever-noarch/
        skip_if_unavailable=True
        gpgkey=https://repos-avocadoproject.rhcloud.com/static/crosa_redhat_com.gpg
        gpgcheck=1
        enabled=1
        enabled_metadata=1

        [avocado-lts]
        name=Avocado LTS (Long Term Stability)
        baseurl=https://repos-avocadoproject.rhcloud.com/static/lts/epel-$releasever-noarch/
        skip_if_unavailable=True
        gpgkey=https://repos-avocadoproject.rhcloud.com/static/crosa_redhat_com.gpg
        gpgcheck=1
        enabled=0
        enabled_metadata=1
        EOF



::

        # yum install avocado avocado-plugins-vt

then the program must be bootstrapped - e.g. initialized. Configuration files are created in this stage and test providers are cloned from github repositories.
::

        # avocado vt-bootstrap
        # avocado vt-bootstrap --vt-type spice

By this command avocado performs these steps:

#. Checks mandatory programs and headers

#.  Checks the recommended programs

#. Updates all test providers from github

#. Create and verify directories

#. Generates config files

#. Verifies and possibly downloads guest image

   * downloads JeOS, which is minimalistic Fedora distribution

#. Checks for kvm modules

You can then check if everything is all right by running:
::

   # avocado list --vt-type spice

which should list all avocado spice tests (including avocado list


Make guest VM image
===================

To perform VM tests it is necessary to have some OS distribution installed on data image. The following example shows installation of RHEL developed version.
::

    # avocado run --vt-guest-os Linux.RHEL.7.devel --vt-extra-params 'url=http://download.eng.brq.redhat.com/rel-eng/$RHELVERSION/compose/Server/x86_64/os/' --show-job-log  -- unattended_install.url.http_ks.default_install

qcow2 VM guest image is then stored in ~/avocado/data/avocado-vt/images/

2. On Beaker stable system

 * Go to http://jenkins.spice.brq.redhat.com/

 * Select `Custom test run` and then `Build with Parameters` from left column menu.

 * Fill in form and while selecting use-install radio-button option

 * If desired, copy newly created qcow2 image to our nfs server (10.43.73.3:/nfs/iso/avocado/templates/) and make symlink of guest VM image.

*****************************
Beaker initialization and run
*****************************

#. Login to Beaker (http://beaker.engineering.redhat.com/).

#. Configure your Beaker account to work with `Jenkins` (http://jenkins.spice.brq.redhat.com/).

   * Go to User preferences -> SSH Public Keys and upload your id_rsa ssh public key, store your ssh private key to safe place and do not forget its password

   * Add `auto/jenkins.spice.brq.redhat.com` to Submission delegates in User preferences

   * To receive email for auto/jenkins.spice.brq.redhat.com subscribe yourself at: `spice-qe-auto`. Admin interface for mail list is: admin for spice-qe-auto (password is well know, starts with: fo0m4n.....)

Start a job
===========

#. Go to Jenkins: http://jenkins.spice.brq.redhat.com/ and login.

#. Select custom test run and Build with Parameters in the left column menu.

#. Fill in form

   * Qcow2 images are stored on 10.34.73.3 server in the path nfs/iso/avocado/templates/. You can choose from them or create your own image by following `Make guest VM image`_ 

   * If image of desired guest/client VM already exists, choose `use-template` from radio-button menu. Then run ``# avocado run --vt-type  spice -- use-template`` on beaker machine.

#. On selected Beaker system will be installed choosen OS, you can SSH and run desired test cases

Remark in the case of host bridge usage:
----------------------------------------

 * If you want to connect by remote-viewer to the client VM or guest VM using bridge virbr0, you must create new route table:
   ::

    # cat /etc/iproute2/rt_tables << EOF
    $any_number my
    EOF
    # ip r add default via 10.34.72.254 table my
    # ip rule add from $virbr0:inet table my

  , where ``$virbr0:inet`` is variable for virtual bridge IP address and ``$any_number`` stands for any unused number you like

First look
==========

Directories
-----------
* ssh to beaker machine, then you'll find:

  +-----------------------+------------------------------------------+
  |  Avocado job run      |  /mnt/tests/spice/qe/tests/avocado-data  |
  +-----------------------+------------------------------------------+
  |  Avocado logs         |  /mnt/tests/spice/qe/tests/avocado-logs  |
  +-----------------------+------------------------------------------+
  |  Avocado git repo     |  /mnt/tests/spice/qe/tests/avocado       |
  +-----------------------+------------------------------------------+
  |  Avocado-vt git repo  |  /mnt/tests/spice/qe/tests/avocado-vt    |
  +-----------------------+------------------------------------------+

* Avocado logs are also accessible through beaker server (go to IP address of beaker server through your web browser)

TP-Spice related directories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Directory /mnt/tests/spice/qe-tests/avocado-data/avocado-vt/backends/spice/ and its subdirectories are create by ``avocado vt-bootstrap --vt-type spice`` command
