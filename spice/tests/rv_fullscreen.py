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


"""Testing the remote-viewer full-screen option. The resolution of the guest
will take the resolution of the client.
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

    """
    test = stest.ClientGuestTest(vt_test, test_params, env)
    cfg = test.cfg
    act.x_active(test.vmi_c)
    act.x_active(test.vmi_g)
    res_target = "1920x1080"
    res_reset = "640x480"
    act.set_resolution(test.vmi_c, res_target)
    act.set_resolution(test.vmi_g, res_reset)
    ssn = test.open_ssn(test.name_c)
    rv_ssn.connect(test, ssn)
    res_g = act.get_display_resolution(test.vmi_g)[0]
    res_c = act.get_display_resolution(test.vmi_c)[0]
    logger.info("Target: %s, client: %s, guest: %s.", res_target, res_c, res_g)
    err_info = "Guest res should have adjusted to client, but it hasn't."
    assert res_target == res_c == res_g, err_info
