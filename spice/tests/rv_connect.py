"""
rv_connect.py - connect with remote-viewer to remote target

Requires: binaries remote-viewer, Xorg, netstat
          Use example kickstart RHEL-6-spice.ks

"""
import logging
import socket
from aexpect.exceptions import ShellStatusError
from aexpect.exceptions import ShellProcessTerminatedError
from spice.tests.utils_spice import *
from spice.tests.rv_session import *
from virttest import utils_net, remote, utils_misc
from autotest.client.shared import error


def run_rv_connect(test, params, env):
    """
    Simple test for Remote Desktop connection
    Tests expects that Remote Desktop client (spice/vnc) will be executed
    from within a second guest so we won't be limited to Linux only clients

    The plan is to support remote-viewer at first place

    @param test: QEMU test object.  @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """

    test_type = params.get("test_type")
    ssltype = params.get("ssltype", "")

    guest_vm = env.get_vm(params["guest_vm"])


    session = RvSession(params, env)
    session.clear_interface_all()
    session.connect()

    try:
        session.is_connected()
    except RVConnectError:
        if test_type == "negative":
            logging.info("remote-viewer connection failed as expected")
            if ssltype in ("invalid_implicit_hs", "invalid_explicit_hs"):
                # Check the qemu process output to verify what is expected
                qemulog = guest_vm.process.get_output()
                if "SSL_accept failed" in qemulog:
                    return
                else:
                    raise error.TestFail("SSL_accept failed not shown in qemu" +
                                         "process as expected.")
            is_rv_connected = False
        else:
            raise error.TestFail("remote-viewer connection failed")

    if test_type == "negative" and is_rv_connected:
        raise error.TestFail("remote-viewer connection was established when" +
                             " it was supposed to be unsuccessful")
