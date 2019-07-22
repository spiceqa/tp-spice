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

import os
import ntpath
import logging
import contextlib

from spice.lib import reg
from spice.lib import ios
from spice.lib import act
from spice.lib import utils

logger = logging.getLogger(__name__)


@reg.add_action(req=[ios.IOSystem])
@reg.add_action(req=[ios.IRhel, ios.IVersionMajor8])
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
        ssn = act.new_ssn(vmi, admin, dogtail_ssn=True)
    cmdline = str(cmd)
    kwargs = {}
    if timeout:
        kwargs['timeout'] = timeout
    out = ssn.cmd(cmdline, **kwargs)
    act.info(vmi, "cmd: %s, out: %s", cmdline, out)
    return out


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
    kwargs = {}
    if timeout:
        kwargs['timeout'] = timeout
    out = ssn.cmd(cmdline, **kwargs)
    act.info(vmi, "cmd: %s, out: %s", cmdline, out)
    return out


@reg.add_action(req=[ios.IOSystem])
def rstatus(vmi, cmd, ssn=None, admin=False, dogtail_ssn=False, timeout=None):
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
        ssn = act.new_ssn(vmi, admin, dogtail_ssn)
    cmdline = str(cmd)
    kwargs = {}
    if timeout:
        kwargs['timeout'] = timeout
    status, out = ssn.cmd_status_output(cmdline, **kwargs)
    act.info(vmi, "cmd: %s, status: %s, output: %s", cmdline, status, out)
    return (status, out)


@reg.add_action(req=[ios.IOSystem])
def new_admin_ssn(vmi):
    return act.new_ssn(vmi, admin=True)


@reg.add_action(req=[ios.IOSystem], name="new_ssn_context")
@contextlib.contextmanager
def new_ssn_context(vmi, admin=False, dogtail_ssn=False, name=""):
    ssn = act.new_ssn(vmi, admin, dogtail_ssn)
    try:
        yield ssn
    finally:
        out = ssn.read_nonblocking(internal_timeout=20)
        logger.info("'%s' session log:\n%s.", name, str(out))
        ssn.close()


@reg.add_action(req=[ios.IOSystem])
def new_ssn(vmi, admin=False, dogtail_ssn=False):
    if admin:
        username = vmi.cfg.rootuser
        password = vmi.cfg.rootpassword
        utils.debug(vmi, "Open a new session for: admin.")
    else:
        username = vmi.cfg.username
        password = vmi.cfg.password
        utils.debug(vmi, "Open a new session for: user.")
    ssn = vmi.vm.wait_for_login(username=username,
                                password=password,
                                timeout=int(vmi.cfg.login_timeout))
    if dogtail_ssn:
        dogtail_cmd = utils.Cmd("dogtail-run-headless-next", "--dont-start",
                                "--dont-kill", "/bin/bash")
        act.run(vmi, dogtail_cmd, ssn=ssn)
    act.export_vars(vmi, ssn)
    return ssn


@reg.add_action(req=[ios.IOSystem])
def info(vmi, string, *args, **kwargs):
    logger.info(vmi.vm_name + " : " + string, *args, **kwargs)


@reg.add_action(req=[ios.IOSystem])
def error(vmi, string, *args, **kwargs):
    logger.error(vmi.vm_name + " : " + string, *args, **kwargs)


@reg.add_action(req=[ios.ILinux])
def cp_file(vmi, src_fpath, dst_fpath=None, dst_dir=None, dst_fname=None):
    """Copy file from host system to VM's workdir.
    """
    if not dst_fpath:
        if not dst_dir:
            dst_dir = act.dst_dir(vmi)
        if not dst_fname:
            dst_fname = ntpath.basename(src_fpath)
        dst_fpath = os.path.join(dst_dir, dst_fname)
    vmi.vm.copy_files_to(src_fpath, dst_fpath)
    return dst_fpath
