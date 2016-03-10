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

"""rv_gui.py - runs dogtail tests on the client.

Requirements for host machine
-----------------------------

    - rv_setup must be run to have dogtail be installed on the client.
    - rv_connect must be run to restart the gdm session.
"""

import os
import logging
import aexpect
import glob
from virttest.virt_vm import VMDeadError
from autotest.client.shared import error
from virttest import utils_net
from spice.lib import rv_ssn
from spice.lib import stest
from spice.lib import utils


EXPECTED_RV_CORNERS_FS = [('+0','+0'),('-0','+0'),('-0','-0'),('+0','-0')]
WIN_TITLE = "'vm1 (1) - Remote Viewer'"


def run(vt_test, test_params, env):
    """GUI tests for remote-viewer.

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
    utils.clear_interface(test, test.name_c)
    utils.clear_interface(test, test.name_g)
    cfg = test.cfg
    ssn_c = test.ssn_c

    tests = cfg.rv_gui_test_list.split()
    ssn_c.cmd("cd %s" % cfg.test_script_tgt)
    rv_res_orig = utils.get_geom(test, test.name_c, WIN_TITLE)
    errors = 0
    for i in tests:
        logging.info("Test: " + i)

        # Prepare for test.
        if "zoom" in i or "autoresize" in i:
            res_g = utils.get_res(test, test.name_g)
            rv_res = utils.get_geom(test, test.name_c, WIN_TITLE)
        if "screenshot" in i:
            screenshot_exp_file = os.path.join(cfg.screenshot_dir,
                                               cfg.screenshot_expected_name)
            cmd = 'test -f %s' % screenshot_exp_file
            if ssn_c.cmd_status(cmd) == 0:
                logging.info('Remove %s on client.' % screenshot_exp_file)
                cmd = 'rm -f %s' % screenshot_exp_file
                ssn_c.cmd(cmd)


        # Verification of the printscreen test prior to the test being run.
        if "printscreen" in i:
            if test.vm_c.is_rhel7():
                pics = glob.glob('/home/test/Pictures/Screen*')
                output = guest_session.cmd('rm -vf')
                logging.info("Screenshots removed: " + output)

        # Adding parameters to the test
        test_path = "./unittests/%s_rv.py" % i
        cmdline = test_path
        if (i == "connect"):
            host_ip = utils_net.get_host_ip_address(test_params)
            host_port = test.vm_g.get_spice_var("spice_port")
            cmdline += " 'spice://%s:%s'" % (host_ip, host_port)
            if cfg.spice_password:
                cmdline += " %s > /dev/null 2>&1" % cfg.spice_password

        logging.info("cmdline for client: %s", cmdline)
        try:
            out = ssn_c.cmd(cmdline)
            logging.info(out)
        except aexpect.ShellCmdError:
            logging.error("Status %s: FAIL", i)
            errors += 1
        else:
            logging.info("Status %s: PASS", i)

        # XXX What we are wait for?
        utils_spice.wait_timeout(5)

        # Verification after test run.
        if "zoom" in i:
            res_g2 = utils.get_res(test, test.name_g)
            rv_res2 = utils.get_geom(test, test.name_c, WIN_TITLE)
            # Check to see that the resolution doesn't change
            logstr = "Checking that the guest's resolution doesn't change."
            res_eq(res_g, res_g2)
            if "zoomin" in i:
                if not res_gt(rv_res, rv_res2):
                    logging.error("RV window was not increased.")
            if "zoomout" in i:
                if not res_gt(rv_res2, rv_res)
                    logging.error("RV window was not decreased.")
            if "zoomnorm" in i:
                if not res_eq(rv_res2, rv_res_orig):
                    logging.error("RV window is not the same as it was"
                                  "originally when rv was started.")
        if "quit" in i or "close" in i:
            # Verify for quit tests that remote viewer is not running on client
            status, out = ssn_c.cmd_status_output("pgrep remote-viewer")
            if status == 0:
                logging.error("remote-viewer is still running: %s", out)
        if "screenshot" in i:
            # Verify the screenshot was created and clean up.
            try:
                ssn_c.cmd('[ -e ' + screenshot_exp_file + ' ]')
                ssn_c.cmd('rm ' + screenshot_exp_file)
                print cfg.screenshot_expected_name + " was created as expected"
            except aexpect.ShellCmdError:
                raise error.TestFail("Screenshot " + screenshot_exp_file + \
                                     " was not created")
        if i == "fullscreen" or i == "fullscreen_shortcut":
            # Verify that client's res = guests's res
            res_g = utils.get_res(test, test.name_g)
            res_c = utils.get_res(test, test.name_c)
            rv_geometry = utils.get_geom(test, test.name_c, WIN_TITLE)
            rv_corners = utils.get_corners(test, test.name_c, WIN_TITLE)
            if(res_c == res_g):
                logging.info("PASS: Guest resolution is the same as the client")
                # Verification #2, client's res = rv's geometry
                if(res_c == rv_geometry):
                    logging.info("PASS client's res = geometry of rv window")
                else:
                    raise error.TestFail("Client resolution: " + res_c +
                                         " differs from the rv's geometry: " +
                                         rv_geometry)
            else:
                raise error.TestFail("Guest resolution: " + res_g +
                                     "differs from the client: " + res_c)
            # Verification #3, verify the rv window is at the top corner
            if rv_corners in EXPECTED_RV_CORNERS_FS:
                logging.info("PASS: rv window is at the top corner: " +
                             rv_corners)
            else:
                raise error.TestFail("rv window is not at the top corner " +
                                     "as expected, it is at: " + rv_corners)
        # Verify rv window < client's res
        if i == "leave_fullscreen" or i == "leave_fullscreen_shortcut":
            rv_corners = utils.get_corners(test, test.name_c, WIN_TITLE)
            if(rv_corners not in EXPECTED_RV_CORNERS_FS):
                logging.info("PASS: rv window is not at top corner: " + \
                             rv_corners)
            else:
                raise error.TestFail("rv window, leaving full screen failed.")

        if "printscreen" in i:
            if test.vm_c.is_rhel7():
                output = guest_session.cmd('ls -al /home/test/Pictures | grep Screen*')
                logging.info("Screenshot Taken Found: " + output)
            else:
                output = guest_root_session.cmd("ps aux | grep gnome-screenshot")
                index = 1
                found = 0
                plist = output.splitlines()
                for line in plist:
                    print str(index) + " " + line
                    index += 1
                    list2 = line.split()
                    #get gnome-screenshot info
                    gss_pid = str(list2[1])
                    gss_process_name = str(list2[10])
                    #Verify gnome-screenshot is running and kill it
                    if gss_process_name == "gnome-screenshot":
                        found = 1
                        guest_root_session.cmd("kill " + gss_pid)
                        break
                    else:
                        continue
                if not (found):
                    raise error.TestFail("gnome-screenshot is not running.")

        # Verify the shutdown dialog is present
        if "ctrl_alt_del" in i:
            #looking for a blank named dialog will not work for RHEL 7
            #Will need to find a better solution to verify
            #the shutdown dialog has come up
            if isRHEL7:
                #wait 80 seconds for the VM to completely shutdown
                utils_spice.wait_timeout(90)
                try:
                    guest_vm.verify_alive()
                    raise error.TestFail("Guest VM is still alive, shutdown failed.")
                except VMDeadError:
                    logging.info("Guest VM is verified to be shutdown")
            else:
                guest_session.cmd("xwininfo -name ''")

        # If autoresize_on is run, change window geometry
        if i == "autoresize_on" or i == "autoresize_off":
            logging.info("Attempting to change the window size of rv to:" + \
                         str(cfg.changex) + "x" + str(cfg.changey))
            #wmctrl_cmd = "wmctrl -r 'spice://%s?port=%s (1) - Remote Viewer'" \
            #       % (host_ip, host_port)
            wmctrl_cmd = "wmctrl -r %s" % WIN_TITLE
            wmctrl_cmd += " -e 0,0,0," + str(cfg.changex) + "," + str(cfg.changey)
            output = client_session.cmd(wmctrl_cmd)
            logging.info("Original res: " + res_g)
            logging.info("Original geometry: " + rv_res)

            #Wait for the rv window to change and guest to adjust resolution
            utils_spice.wait_timeout(2)

            res_g2 = utils.get_res(test, test.name_g)
            rv_res2 = utils.get_geom(test, test.name_c, WIN_TITLE)
            logging.info("After test res: " + res_g2)
            logging.info("After test geometry: " + rv_res2)

            #Get the required information
            width2 = int(res_g2.split('x')[0])
            rvwidth2 = int(rv_res2.split('x')[0])

            #The second split of - is a workaround because the xwinfo sometimes
            #prints out dashes after the resolution for some reason.
            height2 = int(res_g2.split('x')[1].split('-')[0])
            rvheight2 = int(rv_res2.split('x')[1].split('-')[0])

            # width and height that was specified is changed w/alotted limit
            percentchange(cfg.accept_pct, cfg.changey, rvheight2, "Height parameter:")
            percentchange(cfg.accept_pct, cfg.changex, rvwidth2, "Width parameter:")

            if i == "autoresize_on":
                #resolution is changed, attempted to match the window
                logging.info("Checking resolution is changed, attempted"
                             " to match the window, when autoresize is on")
                percentchange(cfg.accept_pct, rvheight2, height2, "Height param:")
                percentchange(cfg.accept_pct, rvwidth2, width2, "Width param:")
            if i == "autoresize_off":
                #resolutions did not change
                logging.info("Checking the resolution does not change"
                             ", when autoresize is off")
                logstr = "Checking that the guest's resolution doesn't change"
                res_eq(res_g, res_g2)

        # Verify a connection is established
        if i == "connect":
            try:
                utils_spice.rv_connected(client_vm, host_ip, host_port,
                                         cfg.rv_binary)
            except utils_spice.SpiceUtilsError:
                raise error.TestFail("remote-viewer connection failed")
    if errors:
        raise error.TestFail("%d GUI tests failed, see log for more details" %
                             errors)
