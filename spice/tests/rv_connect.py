#!/usr/bin/env python

"""
rv_connect.py - connect with remote-viewer from client VM to guest VM

Requires
--------
    - remote-viewer
    - Xorg
    - netstat
"""

import logging
from avocado.core import exceptions
from spice.lib import rv_session

def run(test, params, env):
    """
    Simple tests for Remote Desktop connection. Tests expect that remote-viewer
    will be executed from guest VM. Thus we support clients running on
    different OSes.

    Parameters
    ----------
    test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    """

    logging.info("Start test %s", test.name)

    # test_type - known variants:
    # * negative
    test_type = params.get("test_type")

    # ssltype - known variants:
    # * explicit_hs
    # * implicit_hs
    # * invalid_explicit_hs
    # * invalid_implicit_hs
    ssltype = params.get("ssltype", "")

    # Gets guest vm object
    guest_vm = env.get_vm(params["guest_vm"])

    session = rv_session.RvSession(params, env)
    session.clear_interface_all()
    session.connect()

    try:
        session.is_connected()
    except rv_session.RVConnectError:
        if test_type == "negative":
            logging.info("remote-viewer connection failed as expected")
            if ssltype in ("invalid_implicit_hs", "invalid_explicit_hs"):
                # Check the qemu process output to verify what is expected
                qemulog = guest_vm.process.get_output()
                if "SSL_accept failed" in qemulog:
                    return
                else:
                    raise exceptions.TestFail(
                        "SSL_accept failed not shown in qemu process as"
                        "expected."
                    )
            is_rv_connected = False
        else:
            raise exceptions.TestFail("remote-viewer connection failed")

    if test_type == "negative" and is_rv_connected:
        raise exceptions.TestFail(
            "remote-viewer connection was established when it was supposed to"
            "be unsuccessful"
        )
