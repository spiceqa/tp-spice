"""
rv_connect.py - connect with remote-viewer to remote target

Requires: binaries remote-viewer, Xorg, netstat
          Use example kickstart RHEL-6-spice.ks
"""

import logging
from avocado.core import exceptions
from spice.lib import rv_session

def run(test, params, env):
    """
    Simple test for Remote Desktop connection
    Tests expects that Remote Desktop client (spice/vnc) will be executed
    from within a second guest so we won't be limited to Linux only clients

    The plan is to support remote-viewer at first place

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
