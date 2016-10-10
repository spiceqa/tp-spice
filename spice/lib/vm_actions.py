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
#
# Copyright: Red Hat Inc. 2016
# Author: Andrei Stepanov <astepano@redhat.com>
#

"""Action on VM with some OS.
"""

import zope
from zope import interface
from zope.interface.interface import adapter_hooks
from zope.interface import adapter
from spice.lib import reg
from spice.lib import ios
from spice.lib import act


def run_cmd(act, cmd, admin=False):
    ssn = act.open_ssn()
    cmdline = act.mk_cmd()
    return subprocess.list2cmdline(cmd)


@reg.add_action(req=[ios.ILinux])
def export_vars(vmi, ssn):
    """Export essentials variables per SSH session."""
    vmi.vm.info("Export vars for session.")
    ssn.cmd("export DISPLAY=:0.0")


@reg.add_action(req=[ios.IOSystem])
def new_admin_ssn(vmi, act):
    return act.new_ssn(vmi, admin=True)


@reg.add_action(req=[ios.IOSystem])
def new_ssn(vmi, admin=False):
    if admin:
        username = vmi.cfg.rootuser
        password = vmi.cfg.rootpassword
        vmi.vm.info("Open a new session for: admin.")
    else:
        username = vmi.cfg.username
        password = vmi.cfg.password
        vmi.vm.info("Open a new session for: user.")
    ssn = vmi.vm.wait_for_login(username=username,
                                password=password,
                                timeout=int(vmi.cfg.login_timeout))
    act.export_vars(vmi, ssn)
    return ssn
