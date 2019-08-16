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

"""rv_gui.py - runs dogtail tests on the client.

Requirements for host machine
-----------------------------

    - rv_setup must be run to have dogtail be installed on the client.
    - rv_connect must be run to restart the gdm session.

This file doesn't make any decision about test success. The decision is made by
test running at VM.

Test is successful if all sub-tests running at VM are successful.

"""

import os
import logging
import traceback
from spice.lib import stest
from spice.lib import utils
from spice.lib import act


logger = logging.getLogger(__name__)


def run(vt_test, test_params, env):
    """GUI tests for remote-viewer.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    Raises
    ------
    TestFail
        Test fails for expected behaviour.

    """
    test = stest.ClientGuestTest(vt_test, test_params, env)
    cfg = test.cfg
    vmi_c = test.vmi_c
    vmi_g = test.vmi_g
    vm_c = test.vm_c
    # Screen lock is now disabled in kickstart file for source QCOW images of
    # SPICE-QE team (https://gitlab.cee.redhat.com/spiceqe/install-compose/ks).
    # act.lock_scr_off(vmi_c)
    act.turn_accessibility(vmi_c)
    act.x_active(vmi_c)
    act.x_active(vmi_g)
    if utils.vm_is_rhel8(vm_c):
        act.set_alt_python(vmi_c, "/usr/bin/python3")
    else:
        act.install_rpm(vmi_c, test.cfg_c.epel_rpm)
        act.install_rpm(vmi_c, test.cfg_c.dogtail_rpm)
        act.install_rpm(vmi_c, "xdotool")
    if utils.vm_is_rhel6(vm_c):
        # Activate accessibility for rhel6
        act.reset_gui(vmi_c)

    # Copy tests to client VM.
    # Some tests could require established RV session, some of them, don't.
    is_connected = False
    if cfg.make_rv_connect:
        ssn = act.new_ssn(vmi_c, dogtail_ssn=vmi_c.vm.is_rhel8())
        act.rv_connect(vmi_c, ssn)
        if not cfg.negative:
            act.rv_chk_con(vmi_c)
            is_connected = True
    logging.getLogger().setLevel(logging.DEBUG)
    tdir = act.cp2vm(vmi_c, cfg.client_tests)
    tpath = os.path.join(tdir, cfg.script)
    cmd = utils.Cmd('python', *tpath.split())
    try:
        status, _ = act.rstatus(vmi_c, cmd, dogtail_ssn=vmi_c.vm.is_rhel8())
    except Exception as e:
        a = traceback.format_exc()
        logger.info("Exception: %s: %s.", repr(e), a)
    if cfg.make_rv_connect:
        out = ssn.read_nonblocking()
        logger.info("RV log: %s.", str(out))
    if status:
        raise utils.SpiceTestFail(test, "Test failed.")
