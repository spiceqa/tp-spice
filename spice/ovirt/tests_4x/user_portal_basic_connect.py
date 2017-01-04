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

from autotest.client.shared import error

from spice.lib import act
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
    test = stest.ClientGuestOvirtTest(vt_test, test_params, env)
    vmi_c = test.vmi_c
    cfg = test.cfg
    with act.new_ssn_context(vmi_c, name='Selenium session') as ssn:
        act.run_selenium(vmi_c, ssn)
        vm_addr = test.vm_c.get_address()
        logger.info("VM addr: %s", vm_addr)
        act.turn_firewall(vmi_c, "no")  # XXX
        port = test.vm_c.get_port(int(cfg.selenium_port))
        act.info(vmi_c, "Use port to connect to selenium: %s.", port)
        drv = driver.DriverFactory(cfg.selenium_driver,  # Browser name.
                                   vm_addr,
                                   port)
        drv.maximize_window()   # Maximize web-browser window.
        login_page = user_login.UserLoginPage(drv)
        home_page = login_page.login_user(username=cfg.ovirt_user,
                                          password=cfg.ovirt_password,
                                          domain=cfg.ovirt_profile,
                                          autoconnect=False)
        tab_controller = home_page.go_to_basic_tab()
        if cfg.ovirt_vm_name:
            vm = tab_controller.get_vm(cfg.ovirt_vm_name)
        elif cfg.ovirt_pool_name:
            vm = tab_controller.start_vm_from_pool(cfg.ovirt_pool_name)
            shutdown_vm = True
        if not vm.is_up:
            logger.info("Up VM: %s.", vm.name)
            tab_controller.run_vm(vm.name)
            tab_controller.wait_until_vm_starts_booting(vm.name)
        vm_details = vm.select()
        console_options_dialog = vm_details.console_edit()
        console_options_dialog.select_spice()
        console_options_dialog.set_open_in_fullscreen(cfg.full_screen)
        console_options_dialog.submit_and_wait_to_disappear(timeout=2)
        tab_controller.wait_until_vm_is_up(vm.name)
        vm_details.console()
        vms_base.GuestAgentIsNotResponsiveDlg.ok_ignore(drv)
        logging.info("remote-viewer is supposed now connected.")
        if shutdown_vm:
            tab_controller.shutdown_vm(vm.name)
        home_page.sign_out_user()
        drv.close()
        act.rv_chk_con(vmi_c)  # Check connection on client.
