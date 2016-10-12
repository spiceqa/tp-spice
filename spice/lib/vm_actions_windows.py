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

"""Action on VM with Windows.
"""

from spice.lib import reg
from spice.lib import ios
from spice.lib import act


@reg.add_action(req=[ios.IWindows])
def service_vdagent(vmi, action):
    """Start/Stop/... on the spice-vdagentd service.

    Parameters
    ----------
    action : str
        Action on vdagent-service: stop, start, restart, status, ...

        http://ss64.com/nt/net_service.html

        Know actions are: start / stop / pause / continue.

        .. todo:: Implement me. Not finished: status, restart.

    """
    cmd = ['net', action, "RHEV Spice Agent"]
    act.run_cmd(vmi, cmd)


@reg.add_action(req=[ios.IWindows])
def verify_virtio(vmi):
    """Verify Virtio-Serial linux driver is properly loaded.

    """
    cmd = [vmi.cfg.pnputil, '/e']
    output = act.run_cmd(vmi, cmd)
    installed = "System devices" in output
    act.info(vmi, "Virtio Serial driver is installed:", installed)
    return installed


@reg.add_action(req=[ios.IWindows])
def install_rv(vmi):
    """Install remote-viewer on a windows client.

    .. todo:: Add cfg.client_path_rv_dst = C:\virt-viewer

    """
    vm.copy_files_to(vmi.cfg.host_path, self.cfg.client_path_rv)
    cmd = ['start', '/wait', 'msiexec', '/i', vmi.cfg.client_path_rv]
    cmd.append('INSTALLDIR=%s' % vmi.cfg.client_path_rv_dst)
    act.run_cmd(vmi, cmd)


@reg.add_action(req=[ios.IWindows])
def install_usbclerk_win(vmi):
    """Install usbclerk on a windows client.

    ..todo:: host_path - fix

    """
    vm.copy_files_to(vmi.cfg.host_path, self.cfg.client_path_usbc)
    cmd = ["start", "/wait", "msiexec", "/i", vmi.cfg.client_path_usbc, "/qn"]
    act.run_cmd(vmi, cmd)


@reg.add_action(req=[ios.IWindows])
def reset_gui(vmi):
    """Kill remote-viewer.

    Raises
    ------
    SpiceUtilsError
        Fails to kill remote-viewer.

    """
    # .. todo:: check if remote-viewer is running before killing it.
    cmd = ["taskkill", "/F", "/IM", "remote-viewer.exe"]
    act.run_cmd(vmi, cmd)


@reg.add_action(req=[ios.IWindows])
def kill_by_name(vmi, app_name):
    """Kill selected app on selected VM.

    Parameters
    ----------
    app_name : str
        Name of the binary.

    """
    cmd = ["taskkill", "/F", "/IM"]
    cmd.append(app_name.split('\\')[-1])
    act.run_cmd(vmi, cmd)


@reg.add_action(req=[ios.IWindows])
def proc_is_active(vmi, pname):
    cmd = ['tasklist', '/FI']
    cmd.append("IMAGENAME eq %s.exe" % pname)
    output = act.run_cmd(vmi, cmd)
    if pname in output:
        res = True
    else:
        res = False
    return res
