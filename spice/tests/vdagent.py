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

"""Verify, vdagent status, starting, stopping, and restarting correctly.

"""


import os
import logging
import aexpect
from avocado.core import exceptions
from spice.lib import stest
from spice.lib import utils


logger = logging.getLogger(__name__)


def run(vt_test, test_params, env):
    """Tests for vdagent.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    """
    test = stest.GuestTest(vt_test, test_params, env)
    cfg = test.cfg
    test.cmd.x_active()

    active = test.cmd.service_vdagent("status")

    if cfg.ttype == "start":
        if active:
            test.cmd.service_vdagent("stop")
            active = test.cmd.service_vdagent("status")
        assert not active
        test.cmd.service_vdagent("start")
        active = test.cmd.service_vdagent("status")
        assert active
    elif cfg.ttype == "stop":
        if not active:
            test.cmd.service_vdagent("start")
            active = test.cmd.service_vdagent("status")
        assert active
        test.cmd.service_vdagent("stop")
        active = test.cmd.service_vdagent("status")
        assert not active
    elif cfg.ttype == "restart_running":
        if not active:
            test.cmd.service_vdagent("start")
            active = test.cmd.service_vdagent("status")
        assert active
        test.cmd.service_vdagent("restart")
        active = test.cmd.service_vdagent("status")
        assert active
    elif cfg.ttype == "restart_stopped":
        if active:
            test.cmd.service_vdagent("stop")
            active = test.cmd.service_vdagent("status")
        assert not active
        test.cmd.service_vdagent("restart")
        active = test.cmd.service_vdagent("status")
        assert active
    else:
        raise utils.SpiceTestFail(test, "Bad config.")
