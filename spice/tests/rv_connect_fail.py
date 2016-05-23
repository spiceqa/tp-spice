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

"""Connect with remote-viewer from client VM to guest VM.
"""

import logging
from avocado.core import exceptions
from spice.lib import rv_ssn
from spice.lib import stest
from spice.lib import utils


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

    Raises
    ------
    TestFail
        Test fails for expected behaviour.

    """
    test = stest.ClientGuestTest(vt_test, test_params, env)
    cfg = test.cfg
    test.cmd_c.reset_gui()
    test.cmd_g.reset_gui()
    ssn = test.open_ssn(test.name_c)
    try:
        rv_ssn.connect(test, ssn)
    except rv_ssn.RVSessionConnect as e:
        logger.info("Test failed as expected. Reason: %s", e)
        pass
    else:
        raise exceptions.TestFail(
            "RV connection was established when it was supposed to fail.")
