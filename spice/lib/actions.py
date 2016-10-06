#!/usr/bin/python

import zope
from zope import interface
from zope.interface.interface import adapter_hooks
from zope.interface import adapter
from spice.lib import reg

registry = reg.registry

# Command(s)


def run_cmd(act, cmd, admin=False):
    ssn = act.open_ssn()
    cmdline = act.mk_cmd()
    return subprocess.list2cmdline(cmd)


@add_action(req=[ILinux])
def export_vars(act, ssn):
    """Export essentials variables per SSH session."""
    ssn.cmd("export DISPLAY=:0.0")


@add_action(req=[IOSystem])
def new_ssn(act, admin=False):
    if admin:
        username = act.cfg.rootuser
        password = act.cfg.rootpassword
        act.vm.info("Open a new session for: admin.")
    else:
        username = act.cfg.username
        password = act.cfg.password
        act.vm.info("Open a new session for: user.")
    ssn = act.vm.wait_for_login(username=username,
                                password=password,
                                timeout=int(act.cfg.login_timeout))
    act.export_vars()
    return ssn
