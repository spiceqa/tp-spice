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

from spice.lib import reg
from spice.lib import ios
from spice.lib import act


@reg.add_action(req=[ios.IOSystem])
def run(vmi, cmd, ssn=None, admin=False, timeout=None):
    """
    Raises
    ------
        If the command's exit status is nonzero, raise an exception.
        See: /usr/lib/python2.7/site-packages/aexpect/client.py

    Returns
    -------
    str
        Command output.
    """
    if not ssn:
        ssn = act.new_ssn(vmi, admin)
    cmdline = str(cmd)
    kwargs = []
    if timeout:
        kwargs['timeout'] = timeout
    out = ssn.cmd(cmdline, **kwargs)
    act.info(vmi, "cmd: %s, out: %s", cmdline, out)
    return out


@reg.add_action(req=[ios.IOSystem])
def rstatus(vmi, cmd, ssn=None, admin=False, timeout=None):
    """
    Raises
    ------
        See: /usr/lib/python2.7/site-packages/aexpect/client.py

    Returns
    -------
    str
        Command output + exit status.
    """
    if not ssn:
        ssn = act.new_ssn(vmi, admin)
    cmdline = str(cmd)
    kwargs = []
    if timeout:
        kwargs['timeout'] = timeout
    status, out = ssn.cmd_status_output(cmdline)
    act.info(vmi, "cmd: %s, status: %s, output: %", cmdline, status, out)
    return (status, out)


@reg.add_action(req=[ios.IOSystem])
def new_admin_ssn(vmi):
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


@reg.add_action(req=[ios.IOSystem])
def info(vmi, string, *args, **kwargs):
    logger.info(vmi.vm_name + " : " + string, *args, **kwargs)


@reg.add_action(req=[ios.IOSystem])
def error(vmi, string, *args, **kwargs):
    logger.error(vmi.vm_name + " : " + string, *args, **kwargs)
