"""
rv_fullscreen.py - remote-viewer full screen
                   Testing the remote-viewer --full-screen option
                   If successful, the resolution of the guest will
                   take the resolution of the client.

Requires: connected binaries remote-viewer, Xorg, gnome session

"""
import logging
from autotest.client.shared import error
from virttest.aexpect import ShellCmdError
from spice.tests.rv_session import *


#TODO: This can probably be removed, replaced by rv_session, utils_spice and the
# new fullscreen test
def run_fullscreen_setup(test, params, env):
    """
    Simple test for Remote Desktop connection
    Tests expects that Remote Desktop client (spice/vnc) will be executed
    from within a second guest so we won't be limited to Linux only clients

    The plan is to support primarily remote-viewer

    @param test: QEMU test object.
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """
    # Get necessary params
    logging.debug("Exporting guest display")
    guest_session.cmd("export DISPLAY=:0.0")

    # Get the min, current, and max resolution on the guest
    output = guest_session.cmd("xrandr | grep Screen")
    outputlist = output.split()

    minimum = "640x480"

    current_index = outputlist.index("current")
    current = outputlist[current_index + 1]
    current += outputlist[current_index + 2]
    # Remove trailing comma
    current += outputlist[current_index + 3].replace(",", "")

    maximum = "2560x1600"

    logging.info("Minimum: " + minimum + " Current: " + current +
                 " Maximum: " + maximum)
    if(current != minimum):
        resolution = minimum
    else:
        resolution = maximum

    # Changing the guest resolution
    guest_session.cmd("xrandr -s " + resolution)
    logging.info("The resolution on the guest has been changed from " +
                 current + " to: " + resolution)

    # Start vdagent daemon
    utils_spice.start_vdagent(guest_root_session, "linux", test_timeout)

    client_vm = env.get_vm(params["client_vm"])
    client_vm.verify_alive()
    client_session = client_vm.wait_for_login(
        timeout=int(params.get("login_timeout", 360)))

    client_session.close()
    guest_session.close()

#TODO: Delete this function if the new one works reasonably well; part of cleanup
def run_rv_fullscreen_old(test, params, env):
    """
    Tests the --full-screen option
    Positive test: full_screen param = yes, verify guest res = client res
    Negative test: full_screen param= no, verify guest res != client res

    @param test: QEMU test object.
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """
    # Get the parameters needed for the test
    full_screen = params.get("full_screen")
    guest_vm = env.get_vm(params["guest_vm"])
    client_vm = env.get_vm(params["client_vm"])

    guest_vm.verify_alive()
    guest_session = guest_vm.wait_for_login(
        timeout=int(params.get("login_timeout", 360)))

    client_vm.verify_alive()
    client_session = client_vm.wait_for_login(
        timeout=int(params.get("login_timeout", 360)))

    # Get the resolution of the client & guest
    logging.info("Getting the Resolution on the client")
    client_session.cmd("export DISPLAY=:0.0")

    try:
        guest_res_raw = vm_session.cmd_output("xrandr -d :0 | grep '*'")
        guest_res = guest_res_raw.split()[0]
    except ShellCmdError:
        raise error.TestFail("Could not get guest resolution, xrandr output:" +
                             " %s" % client_res_raw)
    except IndexError:
        raise error.TestFail("Could not get guest resolution, xrandr output:" +
                             " %s" % client_res_raw)

    logging.info("Getting the Resolution on the guest")
    guest_session.cmd("export DISPLAY=:0.0")

    try:
        guest_res_raw = vm_session.cmd_output("xrandr -d :0 | grep '*'")
        guest_res = guest_res_raw.split()[0]
    except ShellCmdError:
        raise error.TestFail("Could not get guest resolution, xrandr output:" +
                             " %s" % guest_res_raw)
    except IndexError:
        raise error.TestFail("Could not get guest resolution, xrandr output:" +
                             " %s" % guest_res_raw)

    logging.info("Here's the information I have: ")
    logging.info("\nClient Resolution: " + client_res)
    logging.info("\nGuest Resolution: " + guest_res)

    # Positive Test, verify the guest takes the resolution of the client
    if full_screen == "yes":
        if(client_res == guest_res):
            logging.info("PASS: Guest resolution is the same as the client")
        else:
            raise error.TestFail("Guest resolution differs from the client")
    # Negative Test, verify the resolutions are not equal
    elif full_screen == "no":
        if(client_res != guest_res):
            logging.info("PASS: Guest resolution differs from the client")
        else:
            raise error.TestFail("Guest resolution is the same as the client")
    else:
        raise error.TestFail("The test setup is incorrect.")

    client_session.close()
    guest_session.close()


# TODO: Might need extending for more than one display (later)
#      -- has more issues though, maybe allow more parameters (although a
# completely new test "resolution sync" could be more useful, eventually
#      -- Also, more displays will most likely need a change in config file
def run_rv_fullscreen(test, params, env):

    session = RvSession(params, env)
    session.clear_interface_all()

    session.set_client_resolution("1920x1080")
    guest_res = session.get_guest_resolution()

    if guest_res[0] == "1920x1080":
        session.set_guest_resolution("640x480")

    session.connect()
    try:
        session.is_connected()
    except:
        logging.info("FAIL")
        raise error.TestFail("Failed to establish connection")

    guest_res = session.get_guest_resolution()

    if guest_res[0] == "1920x1080":
        match = True
        logging.info("Resolution of guest matches the one of client")

    else:
        match = False
        logging.info("Resolutions of guest and client differ")

    full_screen = params.get("full_screen")
    fullscreen_prop = session.is_fullscreen_xprop()

    if full_screen == 'yes' and match and fullscreen_prop:
        logging.info("PASS: Window is fullscreen")
    elif not (full_screen or match): #negative, we don't want the resolutions to match
        logging.info("PASS: Not in fullscreen")
    else:
        logging.info("FAIL")
        raise error.TestFail("r-v either not in fullscreen when expected or yes when not")
