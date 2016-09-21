#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
#
# Copyright: Red Hat Inc. 2016
# Author: Andrei Stepanov <astepano@redhat.com>
#

import logging

from avocado.core import exceptions
from autotest.client.shared import error
from virttest import asset

from spice.lib import stest

from lib4x import driver
from lib4x import vms_base
from lib4x.user_portal import user_login

logger = logging.getLogger(__name__)

@error.context_aware
def run(vt_test, test_params, env):
    """Steps:

        - Download SeleniumHQ server, and copy it to a client.
        - Open ovirt portal.
        - Login as a user.
        - Switch to extended tab.
        - Connect with remote-viewer to selected VM.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    """
    test = stest.ClientTest(vt_test, test_params, env)
    ssn = test.open_ssn(test.name)
    test.cmd.run_selenium(ssn)
    test.cmd.firefox_auto_open_vv()
    client_vm_addr = test.vm.get_address()
    logger.info("VM addr: %s", client_vm_addr)
    test.assn.cmd("iptables -F")  # XXX
    drv = driver.DriverFactory(cfg.selenium_driver,
                               client_vm_addr,
                               cfg.selenium_port)
    drv.maximize_window()
    login_page = user_login.UserLoginPage(drv)
    home_page = login_page.login_user(username=cfg.ovirt_user,
                                      password=cfg.ovirt_password,
                                      domain=cfg.ovirt_profile,
                                      autoconnect=False)
    tab_controller = home_page.go_to_extended_tab()
    vm = tab_controller.get_vm(name)
    if not vm.is_up():
        tab_controller.run_vm_and_wait_until_up(name)
    console_options_dialog = vm.console_edit()
    console_options_dialog.select_spice()
    console.set_open_in_fullscreen(cfg.full_screen)
    console_options_dialog.submit_and_wait_to_disappear()
    vm.console()
    vms_base.GuestAgentIsNotResponsiveDlg.ok_ignore(drv)
    home_page.sign_out_user()
    out = ssn.read_nonblocking()
    logger.info("Selenium log: %s.", str(out))
