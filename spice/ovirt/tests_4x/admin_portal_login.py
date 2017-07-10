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
from lib4x.admin_portal import admin_login

logger = logging.getLogger(__name__)


# pylint: disable=E0602
@error.context_aware
def run(vt_test, test_params, env):
    """Download SeleniumHQ server, and copy it to a client.

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
    vmi = test.vmi
    cfg = vmi.cfg
    with act.new_ssn_context(vmi, name='Selenium session') as ssn:
        act.run_selenium(vmi, ssn)
        vm_addr = test.vm.get_address()
        logger.info("VM addr: %s", vm_addr)
        act.turn_firewall(vmi, "no")
        port = vmi.vm.get_port(int(cfg.selenium_port))
        act.info(vmi, "Use port to connect to selenium: %s.", port)
        drv = driver.DriverFactory(cfg.selenium_driver,
                                   vm_addr,
                                   port)
        drv.maximize_window()
        login_page = admin_login.AdminLoginPage(drv)
        home_page = login_page.login_user(username=cfg.ovirt_admin_user,
                                          password=cfg.ovirt_admin_password,
                                          domain='internal')
        assert cfg.ovirt_vm_name
        if not vmi.vm.is_up:
            #TODO: tab_controller undefined
            tab_controller.run_vm_and_wait_until_up(cfg.ovirt_vm_name)
        home_page.sign_out()
