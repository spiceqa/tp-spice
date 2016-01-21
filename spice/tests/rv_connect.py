#!/usr/bin/env python

"""Connect with remote-viewer from client VM to guest VM.

Client requires
---------------
    - remote-viewer

Guest requires
--------------
    - Xorg
    - netstat
"""

import logging
from avocado.core import exceptions
from spice.lib import rv_session
from spice.lib import conf

def run(test, params, env):
    """Simple tests for Remote Desktop connection. Tests expect that
    remote-viewer will be executed from guest VM. Thus we support clients
    running on different OSes.

    Parameters
    ----------
    test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    Raises
    ------
    TestFail
        Test fails for expected behaviour.

    """
    logging.info("Start test %s", test.name)
    cfg = conf.Params(params)
    session = rv_session.RvSession(params, env)
    session.clear_interface_all()
    session.connect()
    if session.is_connected():
        if cfg.test_type == conf.TEST_TYPE_NEGATIVE:
            raise exceptions.TestFail(
                "Remote viewer connection was established when it was"
                "supposed to be unsuccessful."
            )
    else:
        if cfg.test_type == conf.TEST_TYPE_NEGATIVE:
            logging.info("Remote viewer connection failed as expected")
            if cfg.ssltype in (conf.SSL_TYPE_IMPLICIT_INVALID,
                           conf.SSL_TYPE_EXPLICIT_INVALID):
                guest_vm = env.get_vm(cfg.guest_vm)
                qemulog = guest_vm.process.get_output()
                if conf.PTRN_QEMU_SSL_ACCEPT_FAILED not in qemulog:
                    raise exceptions.TestFail(
                        "Failed to find pattern `${0}` in qemu log."
                        .format(conf.PTRN_QEMU_SSL_ACCEPT_FAILED)
                    )
        else:
            raise exceptions.TestFail("Connection is not established.")
    # Test pass.
