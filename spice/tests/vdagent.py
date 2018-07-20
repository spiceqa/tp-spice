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


import logging

from spice.lib import act
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
    vmi = test.vmi
    act.x_active(vmi)

    active = act.service_vdagent(vmi, "status")

    if cfg.ttype == "start":
        if active:
            # spice-vdagentd.service must be masked before stopping, otherwise
            # is immediatelly started by spice-vdagentd.socket
            act.service_vdagent(vmi, "mask")
            act.service_vdagent(vmi, "stop")
            act.service_vdagent(vmi, "unmask")
            active = act.service_vdagent(vmi, "status")
        assert not active
        act.service_vdagent(vmi, "start")
        active = act.service_vdagent(vmi, "status")
        assert active
    elif cfg.ttype == "stop":
        if not active:
            act.service_vdagent(vmi, "start")
            active = act.service_vdagent(vmi, "status")
        assert active
        act.service_vdagent(vmi, "mask")
        act.service_vdagent(vmi, "stop")
        act.service_vdagent(vmi, "unmask")
        active = act.service_vdagent(vmi, "status")
        assert not active
    elif cfg.ttype == "restart_running":
        if not active:
            act.service_vdagent(vmi, "start")
            active = act.service_vdagent(vmi, "status")
        assert active
        act.service_vdagent(vmi, "restart")
        active = act.service_vdagent(vmi, "status")
        assert active
    elif cfg.ttype == "restart_stopped":
        if active:
            act.service_vdagent(vmi, "mask")
            act.service_vdagent(vmi, "stop")
            act.service_vdagent(vmi, "unmask")
            active = act.service_vdagent(vmi, "status")
        assert not active
        act.service_vdagent(vmi, "restart")
        active = act.service_vdagent(vmi, "status")
        assert active
    else:
        raise utils.SpiceTestFail(test, "Bad config.")
