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

"""Examine spice-vdagent logs during a remote-viewer session.

    - Verifying that the spice-vdagent daemon logs correctly on the guest.
    - Verifying that the spice-vdagent logs correctly copy-paste actions on the
      guest.

    Copies the clipboard script to the guest to test spice vdagent.

"""


import os
import logging
from spice.lib import rv_ssn  # pylint: disable=E0611
from spice.lib import stest

logger = logging.getLogger(__name__)


def run(vt_test, test_params, env):
    """Tests for Remote Desktop connection. Tests expect that remote-viewer
    will be executed from guest VM.

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
    cmd_g = test.cmd_g
    test.cmd_c.reset_gui()
    cmd_g.reset_gui()
    rv_ssn.connect(test)
    if cfg.spice_vdagent_stop_log:
        logger.info("Inspect logs for stop action.")
        if not cmd_g.vdagent_is_running():
            cmd_g.start_vdagent()
        cmd_g.stop_vdagent()
        cmd = "tail -n 3 %s | grep 'vdagentd quiting'" % cfg.vdagent_log
        test.vm_g.assn_g.cmd(cmd)
    if cfg.spice_vdagent_start_log:
        logger.info("Inspect logs for start action.")
        if cmd_g.vdagent_is_active():
            cmd_g.stop_vdagent()
        cmd_g.start_vdagent()
        cmd = "tail -n 2 %s | grep 'opening vdagent virtio channel'" % \
            cfg.vdagent_log
        test.vm_g.assn_g.cmd(cmd)
    if cfg.spice_vdagent_restart_log:
        cmd_g.restart_vdagent()
        cmd = "tail -n 2 %s | grep 'opening vdagent virtio channel'" % \
            cfg.vdagent_log
        test.vm_g.assn_g.cmd(cmd)
    if cfg.spice_vdagent_copypaste:
        # Script location: avocado-vt/shared/scripts/cb.py
        script_path = os.path.join(test.virtdir, "scripts", cfg.guest_script)
        test.vm_g.copy_files_to(script_path, cfg.dst_dir)
        cmd = ('echo "SPICE_VDAGENTD_EXTRA_ARGS=-dd > '
               '/etc/sysconfig/spice-vdagentd')
        test.vm_g.assn_g.cmd(cmd)
        cmd_g.restart_vdagent()
        script_call = os.path.join(cfg.dst_dir, cfg.guest_script)
        cmd = "%s %s %s %s" % (cfg.interpreter, script_call, cfg.script_params,
                               cfg.text_to_test)
        test.vm_g.assn_g.cmd(cmd)
        cmd = "tail -n 3 " + cfg.vdagent_log + " | grep 'clipboard grab'"
        test.vm_g.assn_g.cmd(cmd)
