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

"""Examine Xorg log in guest for qxl presence.

"""

import logging
from avocado.core import exceptions
from virttest import utils_misc
from spice.lib import act
from spice.lib import stest
from spice.lib import utils

logger = logging.getLogger(__name__)


def run(vt_test, test_params, env):
    """Inspects Xorg logs for QLX presence.

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
        Test fails for some reason.

    """
    test = stest.GuestTest(vt_test, test_params, env)
    cfg = test.cfg
    act.x_active(test.vmi)
    cmd = utils.Cmd("grep", "-i", "qxl", cfg.qxl_log)
    exit_code, output = act.rstatus(test.vmi, cmd)
    assert exit_code == 0
    act.info(test.vmi, "Mention about qxl: %s." % output)
