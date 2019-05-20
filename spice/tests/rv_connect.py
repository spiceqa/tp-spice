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

from spice.lib import stest
from spice.lib import act


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
    act.x_active(test.vmi_c)
    act.x_active(test.vmi_g)
    with act.new_ssn_context(test.vmi_c, dogtail_ssn=test.vmi_c.vm.is_rhel8(),
                             name="Remote Viewer") as ssn:
        act.rv_connect(test.vmi_c, ssn)
        act.rv_chk_con(test.vmi_c)
