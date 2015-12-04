=================================
Spice test provider for virt-test
=================================

This is the official [1] test provider for the following
subtest types:

* SPICE

Howto start
-----------
Before start, update **run.cfg** file and add something like this to the end:

    only RHEL.7.1.x86_64..role-guest, RHEL.6.7.i386..role-client

This is done automatically for Beaker task **spice-qe-tests**

General info
------------

This tests depends on another test provider: tp-qemu

This is tests provider from SPICE QE

http://virt-test.readthedocs.org/en/latest/basic/TestProviders.html

virtio-win
----------
Windows should be provided with virtio-drivers to use: virtio_blk, virtio_scsi,
virtio_net. You can find virtio-win package at brewweb.
    # rpm -qf /usr/share/virtio-win/virtio-win-1.7.4.iso
      virtio-win-1.7.4-1.el6_6.noarch

Vista drivers for Unattended install
http://www.scribd.com/doc/17471845/FireGeier-Unattended-Vista-Guide-2#scribd

# Windows
drvload vioscsi.inf
drvload viostor.inf
drvload BALLOON.INF
drvload NETKVM.INF
drvload VIORNG.INF
drvload VIOSER.INF

# 

pnputil -i -a .inf

# dism /image:d:\ /add-driver
/driver:e:\virtio\amd64\win2008\viostor.inf

# NETCFG -WINPE to install the WinPE network stack

================
Know dict values
================

#. **ssltype**

   * explicit_hs
   * implicit_hs
   * invalid_explicit_hs
   * invalid_implicit_hs

#. **test_type**

   * test_type

#. **rv_binary** - path to remote viewer

   * /usr/bin/remote-viewer (default)

#. **spice_secure_channels** - format is 'one, two, three'

   * main, inputs
