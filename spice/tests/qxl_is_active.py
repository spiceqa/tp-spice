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

"""Examine Xorg log in guest-VM.

    - Verifying the qxl driver in Xorg logs.

"""

import logging
from avocado.core import exceptions
from virttest import utils_misc
from spice.lib import rv_ssn
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
    utils.reset_gui(test, test.name)
    test_cmd = "grep -i qxl %s" % cfg.qxl_log
    test.ssn.cmd(test_cmd)
