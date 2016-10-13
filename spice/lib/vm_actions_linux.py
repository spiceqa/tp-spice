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

"""Action on VM with some Linux.
"""

import os
import re
import aexpect
import time
import subprocess

from virttest import asset
from virttest import remote
from virttest.staging import service

from spice.lib import utils
from spice.lib import deco
from spice.lib import reg
from spice.lib import ios
from spice.lib import act


USB_POLICY_FILE = \
    "/usr/share/polkit-1/actions/org.spice-space.lowlevelusbaccess.policy"
"""USB policy file. Location on client."""
USB_POLICY_FILE_SRC = os.path.join(utils.DEPS_DIR,
                                   "org.spice-space.lowlevelusbaccess.policy")
"""USB policy file source."""


@reg.add_action(req=[ios.ILinux])
def export_vars(vmi, ssn):
    """Export essentials variables per SSH session."""
    utils.debug(vmi, "Export vars for session.")
    ssn.cmd("export DISPLAY=:0.0")


@reg.add_action(req=[ios.ILinux])
def service_vdagent(vmi, action):
    """Start/Stop/... on the spice-vdagentd service.

    Parameters
    ----------
    action : str
        Action on vdagent-service: stop, start, restart, status, ...

    Info
    ----
    See: avocado-vt/virttest/staging/service.py for COMMANDS

    """
    ssn = act.new_admin_ssn(vmi)
    runner = remote.RemoteRunner(session=ssn)
    vdagentd = service.Factory.create_specific_service("spice-vdagentd",
                                                       run=runner.run)
    func = getattr(vdagentd, action)
    utils.info(vmi, "spice-vdagent: %s", action)
    return func()


@reg.add_action(req=[ios.ILinux])
def workdir(vmi):
    wdir = vmi.cfg.wdir or "~/tp-spice"
    cmd = ["mkdir", "-p", wdir]
    act.run(vmi, cmd)
    return wdir


@reg.add_action(req=[ios.ILinux])
def dst_dir(vmi):
    dst_dir = vmi.cfg_vm.dst_dir
    cmd1 = utils.Cmd("getent", "passwd", vmi.cfg.username)
    cmd2 = utils.Cmd("cut", "-d:", "-f6")
    cmd = utils.combine(cmd1, "|", cmd2)
    if not dst_dir:
        out = act.run(vmi, cmd)
        dst_dir = out.rstrip('\r\n')
        vmi.cfg.dst_dir = dst_dir
    return dst_dir
#    cmd = 'test -e %s' % dst_dir
#    if vmi.ssn.cmd_status(cmd) != 0:
#        cmd = 'mkdir -p "%s"' % dst_dir
#        vmi.ssn.cmd(cmd)


@reg.add_action(req=[ios.ILinux])
def verify_vdagent(vmi):
    """Verifying vdagent is installed on a VM.

    """
    cmd1 = utils.Cmd("rpm", "-qa")
    cmd2 = utils.Cmd("grep", "spice-vdagentd")
    cmd = utils.combine(cmd1, "|", cmd2)
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux])
def check_usb_policy(vmi):
    """Check USB policy in polkit file.

    Returns
    -------
    bool
        Status of grep command. If pattern is found 0 is returned. 0 in python
        is False so negative of grep is returned.

        .. todo: Move USB_POLICY_FILE to cfg.

    """
    cmd = utils.Cmd('grep', '<allow_any>yes', USB_POLICY_FILE)  # TODO
    status, _ = act.rstatus(vmi, cmd)
    utils.info(vmi, "USB policy is: %s.", status)
    return not status


@reg.add_action(req=[ios.ILinux])
def add_usb_policy(vmi):
    """Add USB policy to policykit file.

    .. todo:: USB_POLICY_FILE_SRC, USB_POLICY_FILE to cfg

    """
    utils.info(vmi, "Sending: %s.", USB_POLICY_FILE_SRC)
    vmi.vm.copy_files_to(USB_POLICY_FILE_SRC, USB_POLICY_FILE)


@reg.add_action(req=[ios.ILinux], name="x_active")
@deco.retry(8, exceptions=(aexpect.ShellCmdError,))
def x_active(vmi):
    """Test if X session is active. Do nothing is X active. Othrerwise
    throw exception.
    """
    cmd = utils.Cmd("gnome-terminal", "-e", "/bin/true")
    act.run(vmi, cmd)
    utils.info(vmi, "X session is present.")


@reg.add_action(req=[ios.ILinux])
def _is_pid_alive(vmi, pid):
    """Verify the process is still alive.

    Parameters
    ----------
    pid : str
        Process that is to be checked.

    """
    cmd = utils.Cmd("ps", "-p", pid)
    status, _ = act.run_cmd_status(vmi, cmd)
    return not status


# ..todo:: change function name.
@reg.add_action(req=[ios.ILinux])
def str_input(vmi, string):
    """Sends string trough vm.send_key(). The string could be spice_password.

    Notes
    -----
    After string will be send Enter.

    Parameters
    ----------
    string : str
        Arbitrary string to be send to VM as keyboard events.

    """
    utils.info(vmi, "Passing string '%s' as kbd events.", string)
    char_mapping = {":": "shift-semicolon",
                    ",": "comma",
                    ".": "dot",
                    "/": "slash",
                    "_": "shift-minus",
                    "?": "shift-slash",
                    " ": "spc",
                    "=": "equal"}
    for character in string:
        if character in char_mapping:
            character = char_mapping[character]
        vmi.vm.send_key(character)
    # Enter
    vmi.vm.send_key("kp_enter")


@reg.add_action(req=[ios.ILinux])
def print_rv_version(vmi):
    """Prints remote-viewer and spice-gtk version available inside.

    Parameters
    ----------
    rv_binary : str
        remote-viewer binary.

        if cfg.rv_ld_library_path:
            xxcmd = "LD_LIBRARY_PATH=/usr/local/lib %s" % cfg.rv_binary
        else:
            xxcmd = cfg.rv_binary
        try:
    """
    cmd = utils.Cmd(vmi.cfg.rv_binary, "-V")
    rv_ver = act.run(vmi, cmd)
    cmd = utils.Cmd(vmi.cfg.rv_binary, "--spice-gtk-version")
    spice_gtk_ver = act.run(vmi, cmd)
    utils.info(vmi, "remote-viewer version: %s", rv_ver)
    utils.info(vmi, "spice-gtk version: %s", spice_gtk_ver)


@reg.add_action(req=[ios.ILinux])
def verify_virtio(vmi):
    """Verify Virtio-Serial linux driver is properly loaded.

    """
    cmd = ["lsmod", "|", "grep", "virtio_console"]
    cmd = ["ls", "/dev/virtio-ports/"]
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux], name="x_turn_off")
@deco.retry(8, exceptions=(AssertionError,))
def x_turn_off(vmi):
    ssn = act.new_admin_ssn(vmi)
    runner = remote.RemoteRunner(session=ssn)
    srv_mng = service.Factory.create_service(run=runner.run)
    srv_mng.set_target("multi-user.target")  # pylint: disable=no-member
    cmd1 = utils.Cmd("ss", "-x", "src", "*X11-unix*")
    cmd2 = utils.Cmd("grep", "-q", "-s", "X11")
    cmd = utils.combine(cmd1, "|", cmd2)
    status, _ = act.rstatus(vmi, cmd)
    assert status != 0, "X is: on. But it should not."
    utils.info(vmi, "X is: off.")


@reg.add_action(req=[ios.ILinux], name="x_turn_on")
@deco.retry(8, exceptions=(AssertionError,))
def x_turn_on(vmi):
    ssn = act.new_admin_ssn(vmi)
    runner = remote.RemoteRunner(session=ssn)
    srv_mng = service.Factory.create_service(run=runner.run)
    srv_mng.set_target("graphical.target")  # pylint: disable=no-member
    cmd1 = utils.Cmd("ss", "-x", "src", "*X11-unix*")
    cmd2 = utils.Cmd("grep", "-q", "-s", "X11")
    cmd = utils.combine(cmd1, "|", cmd2)
    status, _ = act.rstatus(vmi, cmd)
    assert status == 0, "X is: off. But it should not."  # TODO
    utils.info(vmi, "X is: on.")


@reg.add_action(req=[ios.ILinux])
def reset_gui(vmi):
    """Clears user GUI interface of a vm without restart.

    Restart graphical session at VM.

    Notes
    -----
        To accomplish this change SystemD/SystemV runlevels from graphical mode
        to multiuser mode, and back.


    Raises
    ------
    SpiceUtilsError
        Fails to restart Graphical session.

    """
    act.x_turn_off(vmi)
    act.x_turn_on(vmi)
    act.x_active(vmi)


@reg.add_action(req=[ios.ILinux])
def export_x2ssh(vmi, var_name, fallback=None, ssn=None):
    """Take value from X session and export it to ssh session. Useful to
    export variables such as 'DBUS_SESSION_BUS_ADDRESS', 'AT_SPI_BUS'.

    Parameters
    ----------
    var : str
        Variable name.
    fallback : Optional[str]
        If value is absent in X session, then use this value.

    """
    var_val = act.get_x_var(vmi, var_name)
    if not var_val:
        var_val = fallback
    if not ssn:
        ssn = act.new_ssn(vmi)
    if var_val:
        utils.info(vmi, "Export %s == %s", var_name, var_val)
        cmd = utils.Cmd("export", "%s=%s" % (var_name, var_val))
        act.run(vmi, cmd, ssn=ssn)
    else:
        utils.info(vmi, "Do not export %s var.", var_name)


@reg.add_action(req=[ios.ILinux])
def install_rpm(vmi, rpm):
    """Install RPM package on a VM.

    Parameters
    ----------
    rpm : str
        Path to RPM to be installed. It could be path to .rpm file, or RPM
        name or URL.

    """
    utils.info(vmi, "Install RPM : %s.", rpm)
    pkg = rpm
    if rpm.endswith('.rpm'):
        pkg = os.path.split(rpm)[1]
        pkg = pkg[:-4]
    cmd = ["rpm", "-q", "pkg"]
    status, _ = act.scmd(vmi, cmd)
    if status == 0:
        utils.info(vmi, "RPM %s is already installed.", pkg)
        return
    if utils.url_regex.match(rpm):
        utils.info(vmi, "Download RPM: %s.", rpm)
        cmd = ["curl", "-s", "-O", rpm]
        act.cmd(cmd, admin=True, timeout=500)
        rpm = os.path.split(rpm)[1]
    act.cmd("yes | yum -y install %s" % rpm, admin=True, timeout=500)


@reg.add_action(req=[ios.ILinux], name="wait_for_prog")
@deco.retry(8, exceptions=(aexpect.ShellCmdError,))
def wait_for_prog(vmi, program):
    cmd = ["pgrep", program]
    out = act.run(vmi, cmd)
    pids = out.split()
    utils.info(vmi, "Found active %s with pids: %s.", program, str(pids))
    return pids


@reg.add_action(req=[ios.ILinux])
def proc_is_active(vmi, pname):
    try:
        cmd = utils.Cmd("pgrep", "pname")
        act.run(vmi, cmd)
        res = True
    except aexpect.ShellCmdError:
        res = False
    return res


@reg.add_action(req=[ios.ILinux])
def wait_for_win(vmi, pattern, prop="_NET_WM_NAME"):
    """Wait until active window has "pattern" in window name.

    ..todo:: Write same function for MS Windows.

    Info
    ----
    http://superuser.com/questions/382616/detecting-currently-active-window

    Parameters
    ----------
    pattern : str
        Pattern for window name.

    Raises
    ------
    SpiceUtilsError
        Timeout and no window was found.

    """
    cmd1 = utils.Cmd("xprop", "-root", "32x", r"\t$0", "_NET_ACTIVE_WINDOW")
    cmd2 = utils.Cmd("cut", "-f", "2")
    cmd = utils.combine(cmd1, "|", cmd2)
    win_id = act.run(vmi, cmd)
    cmd = utils.Cmd("xprop", "-notype", "-id", win_id, prop)

    @deco.retry(8, exceptions=(utils.SpiceUtilsError, aexpect.ShellCmdError,
                               aexpect.ShellTimeoutError))
    def is_active():
        utils.info(vmi, "Test if window is active: %s", pattern)
        output = act.run(vmi, cmd)
        utils.info(vmi, "Current win name: %s", output)
        if pattern not in output:
            msg = "Can't find active window with pattern %s." % pattern
            raise utils.SpiceUtilsError(msg)  # TODO
        utils.info(vmi, "Found active window: %s.", pattern)

    is_active()


# TODO rewrite me
@reg.add_action(req=[ios.ILinux])
def deploy_epel_repo(vmi):
    """Deploy epel repository to RHEL VM.

    """
    # Check existence of epel repository
    cmd = utils.Cmd("test", "-f", "/etc/yum.repos.d/epel.repo")
    status, _ = act.rstatus(cmd)
    if status:
        arch = vmi.ssn.cmd("arch")
        if "i686" in arch:
            arch = "i386"
        else:
            arch = arch[:-1]
        if "release 5" in vmi.ssn.cmd("cat /etc/redhat-release"):
            cmd = ("yum -y localinstall http://download.fedoraproject.org/"
                   "pub/epel/5/%s/epel-release-5-4.noarch.rpm 2>&1" % arch)
            utils.info(vmi, "Installing EPEL repository.")
            vmi.ssn.cmd(cmd)
        elif "release 6" in vmi.ssn.cmd("cat /etc/redhat-release"):
            cmd = ("yum -y localinstall http://download.fedoraproject.org/"
                   "pub/epel/6/%s/epel-release-6-8.noarch.rpm 2>&1" % arch)
            utils.info(vmi, "Installing EPEL repository.")
            vmi.ssn.cmd(cmd)
        else:
            raise Exception("Unsupported RHEL guest")


@reg.add_action(req=[ios.ILinux])
def set_resolution(vmi, res, display="qxl-0"):
    """Sets resolution of qxl device on a VM.

    Parameters
    ----------
    res : str
        Resolution.
    display : str
        Target display.

    """
    utils.info(vmi, "Seeting resolution to %s.", res)
    cmd = utils.Cmd("xrandr", "--output", display, "--mode", res)
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux])
def get_connected_displays(vmi):
    """Get list of video devices on a VM.

    Return
    ------
        List of active displays on the VM.

    """
    cmd1 = utils.Cmd("xrandr")
    cmd2 = utils.Cmd("grep", "-E", "[[:space:]]connected[[:space:]]")
    cmd = utils.combine(cmd1, "|", cmd2)
    raw = act.run(vmi, cmd)
    displays = [a.split()[0] for a in raw.split('n') if a is not '']
    return displays


@reg.add_action(req=[ios.ILinux])
def get_display_resolution(vmi):
    """Returns list of resolutions on all displays of a VM.

    Return
    ------
        List of resolutions.

    """
    cmd1 = utils.Cmd("xrandr")
    cmd2 = utils.Cmd("grep", "*")
    cmd = utils.combine(cmd1, "|", cmd2)
    raw = act.run(vmi, cmd)
    res = [a.split()[0] for a in raw.split('\n') if a is not '']
    return res


@reg.add_action(req=[ios.ILinux])
def get_open_window_ids(vmi, fltr):
    """Get X server window ids of active windows matching filter.

    Parameters
    ----------
    fltr: str.
        Name of binary/title.

    Return
    ------
        List of active windows matching filter.

    """
    cmd = utils.Cmd("xwininfo", "-tree", "-root")
    xwininfo = act.run(vmi, cmd)
    ids = [a.split()[0] for a in xwininfo.split('\n') if fltr in a]
    windows = []
    for window in ids:
        # ..todo:: What ? It will be localy
        out = subprocess.check_output('xprop -id %s' % window, shell=True)
        for line in out.split('\n'):
            if ('NET_WM_WINDOW_TYPE' in line and
                    'ET_WM_WINDOW_TYPE_NORMAL' in line):
                windows.append(window)
    return windows


@reg.add_action(req=[ios.ILinux])
def get_window_props(vmi, win_id):
    """Get full properties of a window with speficied ID.

    Parameters
    ----------
    win_id : str
        X server id of a window.

    Return
    ------
        Returns output of xprop -id.

    """
    cmd = utils.Cmd("xprop", "-id", win_id)
    raw = act.run(vmi, cmd)
    return raw


@reg.add_action(req=[ios.ILinux])
def get_wininfo(vmi, win_id):
    """Get xwininfo for windows of a specified ID.

    Return
    ------
        Output xwininfo -id %id on the session.

    """
    cmd = utils.Cmd("xwininfo", "-id", win_id)
    raw = act.run(vmi, cmd)
    return raw


@reg.add_action(req=[ios.ILinux])
def get_window_geometry(vmi, win_id):
    """Get resolution of a window.

    Parameters
    ----------
    win_id : str
        ID of the window of interest.

    Return
    ------
        WidthxHeight of the selected window.

    """
    xwininfo = act.get_wininfo(vmi, win_id)
    for line in xwininfo:
        if '-geometry' in line:
            return re.split(r'[\+\-\W]', line)[1]  # ..todo: review


@reg.add_action(req=[ios.ILinux])
def kill_by_name(vmi, app_name):
    """Kill selected app on selected VM.

    Parameters
    ----------
    app_name : str
        Name of the binary.
    XXX
    """
    cmd = utils.Cmd("pkill", app_name.split(os.path.sep)[-1])
    try:
        output = act.run(vmi, cmd)
    except aexpect.ShellCmdError:
        if output == 1:
            pass
        else:
            raise utils.SpiceUtilsError("Cannot kill it.")  # TODO


@reg.add_action(req=[ios.ILinux])
def is_fullscreen_xprop(vmi, win_name, window=0):
    """Tests if remote-viewer windows is fullscreen based on xprop.

    Parameters
    ----------
    win_name : str
        Window name.
    window : int
        Which window is tested (0-3).

    Returns
    -------
    Returns True if fullscreen property is set.

    """
    win_id = act.get_open_window_ids(vmi, win_name)[window]
    props = act.get_window_props(vmi, win_id)
    for prop in props.split('\n'):
        if ('_NET_WM_STATE(ATOM)' in prop and
                '_NET_WM_STATE_FULLSCREEN ' in prop):
            return True


@reg.add_action(req=[ios.ILinux])
def window_resolution(vmi, win_name, window=0):
    """ ..todo:: write me
    """
    win_id = act.get_open_window_ids(vmi, win_name)[window]
    return act.get_window_geometry(vmi, win_id)


@reg.add_action(req=[ios.ILinux])
def get_res(vmi):
    """Gets the resolution of a VM

    ..todo:: ? MONITOR # ?

    Return
    ------

    """
    cmd1 = utils.Cmd("xrandr", "-d", ":0")
    cmd1.append_raw("2>/dev/null")
    cmd2 = utils.Cmd("grep", "*")
    cmd = utils.combine(cmd1, "|", cmd2)
    guest_res_raw = act.run(vmi, cmd)
    guest_res = guest_res_raw.split()[0]
    return guest_res

# ..todo:: implement
# def get_fullscreen_windows(test):
#    cfg = test.cfg
#    windows = vmi.get_windows_ids()


@reg.add_action(req=[ios.ILinux])
def get_corners(vmi, win_title):
    """Gets the coordinates of the 4 corners of the window.

    Info
    ----
    http://www.x.org/archive/X11R6.8.0/doc/X.7.html#sect6

    Parameters
    ----------
    win_title : str
        XXX.

    Return
    ------
    list
        Corners in format: [('+470', '+187'), ('-232', '+187'),
                            ('-232', '-13'), ('+470', '-13')]

    """
    rv_xinfo_cmd = "xwininfo -name %s" % win_title
    rv_xinfo_cmd += " | grep Corners"
    cmd1 = utils.Cmd("xwininfo", "-name", win_title)
    cmd2 = utils.Cmd("grep", "Corners")
    cmd = utils.combine(cmd1, "|", cmd2)
    # Expected format:   Corners:  +470+187  -232+187  -232-13  +470-13
    raw_out = act.run(vmi, cmd)
    line = raw_out.strip()
    corners = [tuple(re.findall("[+-]\d+", i)) for i in line.split()[1:]]
    return corners


@reg.add_action(req=[ios.ILinux])
def get_geom(vmi, win_title):
    """Gets the geometry of the rv_window.

    Parameters
    ----------
    win_title : str
        XXX.

    Returns
    -------
    tuple
        Geometry of RV window. (x,y)

    """
    xinfo_cmd = "xwininfo -name %s" % win_title
    cmd = utils.Cmd("xwininfo", "-name", win_title)
    cmd1 = utils.Cmd("grep", "geometry")
    xinfo_cmd += " | grep geometry"
    # Expected '  -geometry 898x700+470-13'
    out = act.run(vmi, cmd)
    res = re.findall('\d+x\d+', out)[0]
    utils.info(vmi, "Window %s has geometry: %s", win_title, res)
    return utils.str2res(res)


@reg.add_action(req=[ios.ILinux])
def get_x_var(vmi, var_name):
    """Gets the env variable value by its name from X session.

    Info
    ----
    It is no straight way to get variable value from X session. If you try to
    read var value from SSH session it could be different from X session var or
    absent. The strategy used in this function is:

        1. Find nautilus process.
        2. Read its /proc/$PID/environ

    Parameters
    ----------
    var_name : str
        Spice test object.

    Returns
    -------
    str
        Env variable value.

    """
    pattern = "(?<=(?:^{0}=|(?<=\n){0}=))[^\n]+".format(var_name)
    pids = act.wait_for_prog(vmi, "nautilus")
    ret = ""
    for pid in pids:
        cmd1 = utils.Cmd("cat", "/proc/%s/environ" % pid)
        cmd2 = utils.Cmd("xargs", "-n", "1", "-0", "echo")
        cmd = utils.combine(cmd1, "|", cmd2)
        out = act.run(vmi, cmd)
        val = re.findall(pattern, out)
        if val:
            ret = val[0]
    utils.info(vmi, "export %s=%s", var_name, ret)
    return ret


@reg.add_action(req=[ios.ILinux])
def cp_deps(vmi, src, dst_dir=None):
    provider_dir = asset.get_test_provider_subdirs(backend="spice")[0]
    src_path = os.path.join(provider_dir, "deps", src)
    dst_dir = vmi.dst_dir()
    utils.info(vmi, "Copy from deps: %s to %s", src_path, dst_dir)
    vmi.vm.copy_files_to(src_path, dst_dir)


@reg.add_action(req=[ios.ILinux])
def cp2vm(vmi, src, dst_dir=None, dst_name=None):
    if not dst_dir:
        dst_dir = vmi.dst_dir()
    provider_dir = asset.get_test_provider_subdirs(backend="spice")[0]
    src = os.path.normpath(src)
    src_path = os.path.join(provider_dir, src)
    if not dst_name:
        dst_name = src
    dst_path = os.path.join(dst_dir, dst_name)
    utils.info(vmi, "Copy: %s to %s", src_path, dst_path)
    vmi.vm.copy_files_to(src_path, dst_dir)
    return dst_path


@reg.add_action(req=[ios.ILinux])
def chk_deps(vmi, fname, dst_dir=None):
    if not dst_dir:
        dst_dir = vmi.dst_dir()
    dst_path = os.path.join(dst_dir, fname)
    cmd = utils.Cmd("test", "-e", dst_path)
    status, _ = act.rstatus(cmd)
    if status != 0:
        vmi.cp_deps(fname, dst_path)
    return dst_path


@reg.add_action(req=[ios.ILinux])
def img2cb(vmi, img):
    """Use the clipboard script to copy an image into the clipboard.
    """
    script = vmi.cfg_vm.helper
    dst_script = vmi.chk_deps(script)
    cmd = utils.Cmd(dst_script, "--img2cb", img)
    utils.info(vmi, "Put image %s in clipboard.", img)
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux])
def cb2img(vmi, img):
    """

    Parameters
    ----------
    img : str
        Where to save img.

    """
    script = vmi.cfg_vm.helper
    dst_script = vmi.chk_deps(script)
    cmd = utils.Cmd(dst_script, "--cb2img", img)
    utils.info(vmi, "Dump clipboard to image %s.", img)
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux])
def text2cb(vmi, text):
    """Use the clipboard script to copy an image into the clipboard.
    """
    script = vmi.cfg_vm.helper
    dst_script = vmi.chk_deps(vmi.cfg.helper)
    params = "--txt2cb"
    cmd = utils.Cmd(dst_script, "--txt2cb", text)
    utils.info(vmi, "Put in clipboard: %s", text)
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux])
def cb2text(vmi):
    script = vmi.cfg_vm.helper
    dst_script = vmi.chk_deps(vmi.cfg.helper)
    cmd = utils.Cmd(dst_script, "--cb2stdout")
    text = act.run(vmi, cmd)
    utils.info(vmi, "Get from clipboard: %s", text)
    return text


@reg.add_action(req=[ios.ILinux])
def clear_cb(vmi):
    """Use the script to clear clipboard.
    """
    script = vmi.cfg_vm.helper
    dst_script = vmi.chk_deps(script)
    cmd = utils.Cmd(dst_script, "--clear")
    utils.info(vmi, "Clear clipboard.")
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux])
def gen_text2cb(vmi, kbytes):
    script = vmi.cfg_vm.helper
    dst_script = vmi.chk_deps(vmi.cfg.helper)
    size = int(kbytes)
    cmd = utils.Cmd(dst_script, "--kbytes2cb", size)
    utils.info(vmi, "Put %s kbytes of text to clipboard.", kbytes)
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux])
def cb2file(vmi, fname):
    script = vmi.cfg_vm.helper
    dst_script = vmi.chk_deps(vmi.cfg.helper)
    cmd = utils.Cmd(dst_script, "--cb2txtf", fname)
    utils.info(vmi, "Dump clipboard to file.", fname)
    act.run(vmi, cmd, timeout=300)


@reg.add_action(req=[ios.ILinux])
def md5sum(vmi, fpath):
    cmd = utils.Cmd("md5sum", fpath)
    out = act.run(vmi, cmd, timeout=300)
    md5_sum = re.findall(r'\w+', out)[0]
    utils.info(vmi, "MD5 %s: %s.", fpath, md5_sum)
    return md5_sum


@reg.add_action(req=[ios.ILinux])
def klogger_start(vmi):
    ssn = act.new_ssn(vmi)
    cmd = utils.Cmd("xev", "-event", "keyboard", "-name", "klogger")
    utils.info(vmi, "Start key logger. Do not forget to turn it off.")
    ssn.sendline(cmd)
    act.wait_for_win('klogger', 'WM_NAME')
    return ssn


@reg.add_action(req=[ios.ILinux])
def klogger_stop(vmi, ssn):
    # Send ctrl+c (SIGINT) through ssh session.
    time.sleep(1)
    ssn.send("\003")
    output = ssn.read_up_to_prompt()
    a = re.findall(
        'KeyPress.*\n.*\n.* keycode (\d*) \(keysym ([0-9A-Fa-fx]*)', output)
    keys = map(lambda keycode, keysym: (int(keycode), int(keysym, base=16)),
               a)
    utils.info(vmi, "Read keys: %s" % keys)
    # Return list of pressed: (keycode, keysym)
    return keys


@reg.add_action(req=[ios.IRhel, ios.IVersionMajor7])
def turn_accessibility(vmi, on=True):
    """Turn accessibility on vm.

    Parameters
    ----------
    on : str
        Spice test object.

    """
    if utils.is_yes(on):
        val = 'true'
    else:
        val = 'false'
    cmd = utils.Cmd("gsettings", "set",
                    "org.gnome.desktop.interface toolkit-accessibility", val)
    act.run(vmi, cmd)


@reg.add_action(req=[ios.IRhel, ios.IVersionMajor7])
def lock_scr_off(vmi):
    utils.info(vmi, "Disable lock screen.")
    cmd = utils.Cmd("gsettings", "set", "org.gnome.desktop.session",
                    "idle-delay", "0")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gsettings", "set", "org.gnome.desktop.lockdown"
                    "disable-lock-screen", "true")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gsettings", "set", "org.gnome.desktop.screensaver"
                    "lock-delay", "3600")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gsettings", "set", "org.gnome.desktop.screensaver"
                    "lock-enabled", "false")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gsettings", "set", "org.gnome.desktop.screensaver"
                    "idle-activation-enabled", "false")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gsettings", "set"
                    "org.gnome.settings-daemon.plugins.power"
                    "active", "false")
    act.run(vmi, cmd)


@reg.add_action(req=[ios.IRhel, ios.IVersionMajor6])
def turn_accessibility(vmi, on=True):
    """Turn accessibility on vm.

    Parameters
    ----------
    on : str
        Spice test object.

    """
    if utils.is_yes(on):
        val = 'true'
    else:
        val = 'false'
    # gconftool-2 --get "/desktop/gnome/interface/accessibility"
    # temporarily (for a single session) enable Accessibility:
    # GNOME_ACCESSIBILITY=1
    # session.cmd("gconftool-2 --shutdown")
    utils.info(vmi, "Turning accessibility: %s.", val)
    cmd = utils.Cmd("gconftool-2", "--set",
                    "/desktop/gnome/interface/accessibility",
                    "--type", "bool", val)
    act.run(vmi, cmd)


@reg.add_action(req=[ios.IRhel, ios.IVersionMajor6])
def export_dbus(vmi, ssn=None):
    if not ssn:
        ssn = vmi.ssn
    utils.info(vmi, "Export DBUS info.")
    cmd = "cat /var/lib/dbus/machine-id"
    machine_id = ssn.cmd(cmd).rstrip('\r\n')
    cmd = '. /home/test/.dbus/session-bus/%s-0' % machine_id
    ssn.cmd(cmd)
    cmd = ('export DBUS_SESSION_BUS_ADDRESS DBUS_SESSION_BUS_PID'
           'DBUS_SESSION_BUS_WINDOWID')
    ssn.cmd(cmd)


@reg.add_action(req=[ios.IRhel, ios.IVersionMajor6])
def lock_scr_off(vmi):
    utils.info(vmi, "Disable lock screen.")
    # https://wiki.archlinux.org/index.php/Display_Power_Management_Signaling
    # Disable DPMS and prevent screen from blanking
    cmd = utils.Cmd("xset", "s", "off", "-dpms")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gconftool-2", "--set",
                    "/apps/gnome-screensaver/idle_activation_enabled",
                    "--type", "bool", "false")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gconftool-2", "--set",
                    "/apps/gnome-power-manager/ac_sleep_display",
                    "--type", "int", "0")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gconftool-2", "--set",
                    "/apps/gnome-power-manager/timeout/sleep_display_ac",
                    "--type", "int", "0")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gconftool-2", "--set",
                    "/apps/gnome-screensaver/lock_enabled",
                    "--type", "boolean", "false")
    act.run(vmi, cmd)
    cmd = utils.Cmd("gconftool-2", "--set",
                    "/desktop/gnome/session/idle_delay",
                    "--type", "int", "0")
    act.run(vmi, cmd)


@reg.add_action(req=[ios.ILinux])
def run_selenium(vmi, ssn):
    """Some general info.
    There are ways to define Firefox options globaly:

        * /usr/lib64/firefox/defaults/preferences/<anyname>.js
        * /etc/firefox/pref/<anyname>.js

    Format is:

        user_pref("some.key", "somevalue");
        pref("some.key", "somevalue");

    All values are defined at:

        about:config?filter=color

    Also user can define values for specific profile:

        http://kb.mozillazine.org/Profile_folder_-_Firefox#Linux

    For curent profile go to: about:support and press "Open Directory"

    Selenium understands next options:

        -Dwebdriver.firefox.profile=my-profile
        -Dwebdriver.firefox.bin=/path/to/firefox
        -trustAllSSLcertificates

    Also it is possible to specify Firefox profile in selenium python
    bindings:

        FirefoxProfile p = new FirefoxProfile(new File("D:\\profile2"));
        p.updateUserPrefs(new File("D:\\t.js"));

    To create a new profile call:

        firefox -CreateProfile <profile name>

    """
    selenium = download_asset("selenium", section=vmi.cfg_vm.selenium_ver)
    fname = os.path.basename(selenium)
    dst_fname = os.path.join(vmi.workdir(), fname)
    vmi.vm.copy_files_to(selenium, dst_fname)
    defs = utils.Cmd()
    opts = utils.Cmd()
    opts.append("-port")
    opts.append(vmi.cfg.selenium_port)
    opts.append("-trustAllSSLcertificates")
    if vmi.cfg.selenium_driver == 'Firefox':
        profile = vmi.cfg.firefox_profile
        if profile:
            cmd = utils.Cmd("firefox", "-CreateProfile", profile)
            output = ssn.cmd(cmd)
            output = re.findall(r'\'[^\']*\'', output)[1]
            output = output.replace("'", '')
            output = os.path.dirname(output)
            vmi.firefox_profile_dir = output
            utils.info(vmi, "Created a new FF profile at: %s", output)
            defs.append("-Dwebdriver.firefox.profile=%s" % profile)
    defs = " ".join(defs)
    opts = " ".join(opts)
    cmd = "java {} -jar {} {}".format(defs, dst_fname, opts)
    utils.info(vmi, "selenium cmd: %s", cmd)
    ssn.sendline(cmd)


@reg.add_action(req=[ios.ILinux])
def firefox_auto_open_vv(vmi):
    """Automatically open remote-viewer for proposed .vv file.

    See content type at:

        ~/.mozilla/firefox/<profile_name>/mimeTypes.rdf
        application/x-virt-viewer
    """
    pdir = vmi.firefox_profile_dir
    if not pdir:
        vmi.vm.error("Firefox profile dir is not defined")
        return
    user_js = os.path.join(pdir, "user.js")
    opts = []
    opts.append("browser.helperApps.neverAsk.saveToDisk")
    opts.append("browser.helperApps.neverAsk.openFile")
    for o in opts:
        utils.info(vmi, "Remove old value %s from Firefox profile: %s", o,
                 user_js)
        cmd = ["sed", "-i", "-e", "/%s/d" % o, user_js]
        act.run(vmi, cmd)
    line = ('pref("browser.helperApps.neverAsk.openFile",'
            '"application/x-virt-viewer");')
    cmd1 = utils.Cmd("echo", line)
    cmd2 = utils.Cmd(user_js)
    cmd = utils.combine(cmd1, ">>", cmd2)
    utils.info(vmi, "Add new line %s to Firefox profile: %s", line, user_js)
    act.run(vmi, cmd)
