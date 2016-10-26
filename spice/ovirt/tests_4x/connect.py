#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib4x import driver
from lib4x.user_portal import user_login
from lib4x import vms_base

# Howto run
# export PYTHONPATH="$PYTHONPATH:$PWD/../"
# $ ipython
# $ execfile("name.py")

hostname = "XXX"
port = "55555"
vm_name = "win7"

drv = driver.DriverFactory("Firefox", hostname, port)
drv.maximize_window()
login_page = user_login.UserLoginPage(drv)
home_page = login_page.login_user(username="auto",
                                  password="redhat",
                                  domain="spice.brq.redhat.com",
                                  autoconnect=False)
tab_controller = home_page.go_to_extended_tab()
vm = tab_controller.get_vm('win7')
vm.console()
vms_base.GuestAgentIsNotResponsiveDlg.ok_ignore(drv)
