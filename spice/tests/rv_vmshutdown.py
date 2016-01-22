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

"""
rv_vmshutdown.py - shutdown the guest and verify it is a clean exit.

Requires: connected binaries remote-viewer, Xorg, gnome session

"""

# noqa
# flake8: noqa
#pylint: skip-file

import logging
from aexpect import ShellCmdError
from virttest.virt_vm import VMDeadError
from autotest.client.shared import error
from virttest import utils_spice
from virttest import utils_misc
from virttest import utils_net

#TODO: needs rewrite

def run_rv_vmshutdown(test, params, env):
    """
    Tests clean exit after shutting down the VM.
    Covers two cases:
    (1)Shutdown from the command line of the guest.
    (2)Shutdown from the qemu monitor.

    Verify after the shutdown:
    (1)Verifying the guest is down
    (2)Verify the spice connection to the guest is no longer established
    (3)Verify the remote-viewer process is not running

    @param test: QEMU test object.
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """

    # Get the required variables
    rv_binary = params.get("rv_binary", "remote-viewer")
    host_ip = utils_net.get_host_ip_address(params)
    shutdownfrom = params.get("shutdownfrom")
    cmd_qemu_shutdown = params.get("cmd_qemu_shutdown")
    host_port = None

    guest_vm = env.get_vm(params["guest_vm"])
    cmd_cli_shutdown = guest_vm.params.get("shutdown_command")
    guest_vm.verify_alive()
    if guest_vm.params.get("os_type") == "linux":
        guest_session = guest_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)),
            username="root", password="123456")
    else:
        guest_session = guest_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)))

    client_vm = env.get_vm(params["client_vm"])
    client_vm.verify_alive()
    if client_vm.params.get("os_type") == "linux":
        client_session = client_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)),
            username="root", password="123456")
    else:
        client_session = client_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)))

    if guest_vm.get_spice_var("spice_ssl") == "yes":
        host_port = guest_vm.get_spice_var("spice_tls_port")
    else:
        host_port = guest_vm.get_spice_var("spice_port")

    # Determine if the test is to shutdown from cli or qemu monitor
    if shutdownfrom == "cmd":
        logging.info("Shutting down guest from command line:"
                     " %s\n" % cmd_cli_shutdown)
        output = guest_session.cmd(cmd_cli_shutdown)
        logging.debug("Guest is being shutdown: %s" % output)
    elif shutdownfrom == "qemu_monitor":
        logging.info("Shutting down guest from qemu monitor\n")
        output = guest_vm.monitor.cmd(cmd_qemu_shutdown)
        logging.debug("Output of %s: %s" % (cmd_qemu_shutdown, output))
    else:
        raise error.TestFail("shutdownfrom var not set, valid values are"
                             " cmd or qemu_monitor")

    # wait for the guest vm to be shutoff
    logging.info("Waiting for the guest VM to be shutoff")
    utils_misc.wait_for(guest_vm.is_dead, 90, 30, 1, "waiting...")
    logging.info("Guest VM is now shutoff")

    # Verify there was a clean exit by
    #(1)Verifying the guest is down
    #(2)Verify the spice connection to the guest is no longer established
    #(3)Verify the remote-viewer process is not running
    try:
        guest_vm.verify_alive()
        raise error.TestFail("Guest VM is still alive, shutdown failed.")
    except VMDeadError:
        logging.info("Guest VM is verified to be shutdown")

    try:
        utils_spice.rv_connected(
            client_vm, host_ip, host_port, rv_binary)
        raise error.TestFail("Remote-Viewer connection to guest"
                             "is still established.")
    except utils_spice.RVConnectError:
        logging.info("There is no remote-viewer connection as expected")
    else:
        raise error.TestFail("Unexpected error while trying to see if there"
                             " was no spice connection to the guest")

    # Verify the remote-viewer process is not running
    logging.info("Checking to see if remote-viewer process is still running on"
                 " client after VM has been shutdown")
    if client_vm.params.get("os_type") == "linux":
        try:
            pidoutput = str(client_session.cmd("pgrep remote-viewer"))
            raise error.TestFail("Remote-viewer is still running on the client.")
        except ShellCmdError:
            logging.info("Remote-viewer process is not running as expected.")
    elif client_vm.params.get("os_type") == "windows":
        output = client_session.cmd_output(
            'tasklist /FI "IMAGENAME eq remote-viewer.exe"')
        if "remote-viewer" in output:
            raise error.TestFail(
                "Remote-viewer is still running on the client.")
        else:
            logging.info(
                "Remote-viewer process is not running as expected.")
