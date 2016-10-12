#!/usr/bin/env python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.

"""rv_vmshutdown.py - shutdown the guest and verify it is a clean exit.

"""


import os
import logging
import aexpect
from avocado.core import exceptions
from spice.lib import rv_ssn
from spice.lib import stest
from spice.lib import utils
from spice.lib import deco


logger = logging.getLogger(__name__)


def run(vt_test, test_params, env):
    """Run remote-viewer at client VM.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    Notes
    -----
    Tests clean exit after shutting down the VM. Covers two cases:

        * Shutdown from the command line of the guest.
        * Shutdown from the qemu monitor.

    Verify after the shutdown:

        * Verifying the guest is down.
        * Verify the spice connection to the guest is no longer established.
        * Verify the remote-viewer process is not running.

    """
    test = stest.ClientGuestTest(vt_test, test_params, env)
    cfg = test.cfg
    act.x_active(test.vmi_c)
    act.x_active(test.vmi_g)
    ssn = test.open_ssn(test.name_c)
    rv_ssn.connect(test, ssn)
    if test.cfg.shutdown_cmdline:
        test.vm_g.info("Shutting down from command line.")
        try:
            test.assn_g.cmd_output(test.cfg_g.shutdown_command)
        except aexpect.ShellProcessTerminatedError:
            pass
    elif test.cfg.shutdown_qemu:
        test.vm_g.info("Shutting down from qemu monitor.")
        test.vm_g.monitor.cmd(test.cfg.cmd_qemu_shutdown)
    else:
        raise utils.SpiceTestFail(test, "Bad config.")
    # Test: guest VM is dead.
    @deco.retry(8, exceptions=(AssertionError,))
    def is_dead():
        assert test.vm_g.is_dead(), "VM is alive."
    is_dead()
    test.vm_g.info("VM is dead.")
    # Test: no network connection.
    try:
        rv_ssn.is_connected(test)
    except rv_ssn.RVSessionConnect:
        pass
    else:
        raise utils.SpiceTestFail(test, "RV still connected.")
    # Test: no RV proccess on client.
    if act.proc_is_active(test.vmi_c, 'remote-viewer'):
        raise utils.SpiceTestFail(test, "RV is still running on the client.")
