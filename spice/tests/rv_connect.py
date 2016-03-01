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

from avocado.core import exceptions
from spice.lib import rv_ssn
from spice.lib import stest
from spice.lib import utils


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
    utils.clear_interface(test, test.name_c)
    utils.clear_interface(test, test.name_c)
    reason = ""
    try:
        rv_ssn.connect(test)
    except rv_ssn.RVSessionConnect as excp:
        is_connected = False
        reason = str(excp)
    except rv_ssn.RVSessionError:
        raise exceptions.TestFail("Internal bug.")
    else:
        is_connected = True
    is_not_connected = not is_connected
    must_fail = utils.is_yes(cfg.must_fail)
    must_connect = not must_fail
    # Fail cases
    if is_not_connected and must_connect:
        raise exceptions.TestFail(reason)
        #raise exceptions.TestFail("Connection is not established.")
    if is_connected and must_fail:
        raise exceptions.TestFail("Remote viewer connection was established "
                                  "when it was supposed to be unsuccessful.")
    is_ssl = cfg.ssltype in (utils.SSL_TYPE_IMPLICIT_INVALID,
                             utils.SSL_TYPE_EXPLICIT_INVALID)
    if is_not_connected and must_fail and is_ssl:
        qemulog = test.vm_g.process.get_output()
        if utils.PTRN_QEMU_SSL_ACCEPT_FAILED not in qemulog:
            raise exceptions.TestFail(
                "Failed to find pattern `{0}` in qemu log.".format(
                    utils.PTRN_QEMU_SSL_ACCEPT_FAILED))
    # Test pass
    return
