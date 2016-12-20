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


"""Test.
"""

import driver
from user_portal import user_login

drv = driver.DriverFactory("Firefox", "astepano-ws", "4444")
drv.maximize_window()
name = "w7_32"
login_page = user_login.UserLoginPage(drv)
home_page = login_page.login_user(username="username", password="pass",
                                  domain="fqdn", autoconnect=False)
tab_controller = home_page.go_to_basic_tab()
# tab_controller.run_vm_and_wait_until_up(name, timeout=None)
# VMDetailsView
details = tab_controller.get_vm_details(name)
print "Name: %s" % details.name
print "Description: %s" % details.description
print "Os: %s" % details.os
print "Memory: %s" % details.memory
print "Cores: %s" % details.cores
print "Console: %s" % details.console

# VMInstance
vm = tab_controller.get_vm(name)
print "Name: %s" % vm.name
print "Status: %s" % vm.status
print "Is up: %s" % vm.is_up
print "Is down: %s" % vm.is_down
print "Is suspeded: %s" % vm.is_suspended
print "is booting: %s" % vm.is_booting

# EditConsoleOptions
console = details.console_edit()
print "FullScreen: %s" % console.fullscreen_is_checked
console.select_spice()
print "Spice console is selected: %s" % console.spice_is_selected
console.cancel()

from user_portal import extendedtab

tab_controller = home_page.go_to_extended_tab()
vm = tab_controller.get_vm(name)
print "Name: %s" % vm.name
print "Status: %s" % vm.status
print "Is up: %s" % vm.is_up
print "Is down: %s" % vm.is_down
print "Is suspeded: %s" % vm.is_suspended
print "is booting: %s" % vm.is_booting

menu_bar = extendedtab.VMsTabMenuBar(drv)
