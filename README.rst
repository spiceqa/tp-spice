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
