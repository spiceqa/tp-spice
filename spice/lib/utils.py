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

"""Common spice test utility functions.

.. todo:: Rework migration, add migration as a option of the session, but
that can wait.

"""
import logging
import os
import re
import sys
import time
import tempfile
import subprocess
from distutils import util
import aexpect
from virttest import qemu_vm
from virttest import remote
from virttest import utils_misc
from virttest.staging import service
from avocado.core import exceptions


SSL_TYPE_IMPLICIT = "implicit_hs"
"""SSL type - implicit host name."""
SSL_TYPE_EXPLICIT = "explicit_hs"
"""SSL type - explicit host name."""
SSL_TYPE_IMPLICIT_INVALID = "invalid_implicit_hs"
"""SSL type - invalid implicit host name."""
SSL_TYPE_EXPLICIT_INVALID = "invalid_explicit_hs"
"""SSL type - invalid explicit host name."""
PTRN_QEMU_SSL_ACCEPT_FAILED = "SSL_accept failed"
"""Pattern for qemu log - failed to accept SSL."""
USB_POLICY_FILE = \
    "/usr/share/polkit-1/actions/org.spice-space.lowlevelusbaccess.policy"
"""USB policy file. Location on client."""
DEPS_DIR = "deps"
"""Dir with useful files."""
USB_POLICY_FILE_SRC = os.path.join(DEPS_DIR,
                                   "org.spice-space.lowlevelusbaccess.policy")
"""USB policy file source."""

VV_DISTR_PATH = r'C:\virt-viewer.msi'
USBCLERK_DISTR_PATH = r'C:\usbclerk.msi'
"""Path to virt-viewer distribution."""
# ..todo:: add to configs: host_path. client_path + rename to more obvious.
DISPLAY = "qxl-0"


def vm_is_win(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_type") == "windows":
        return True
    return False


def vm_is_linux(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_type") == "linux":
        return True
    return False


def vm_is_rhel7(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_variant") == "rhel7":
        return True
    return False


def vm_is_rhel6(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_variant") == "rhel6":
        return True
    return False


def vm_info(self, string, *args, **kwargs):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    logging.info(self.name + " : " + string, *args, **kwargs)


def vm_error(self, string, *args, **kwargs):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    logging.error(self.name + " : " + string, *args, **kwargs)


def extend_api_vm():
    """Extend qemu.VM(virt_vm.BaseVM) with useful methods.
    """
    qemu_vm.VM.is_linux = vm_is_linux
    qemu_vm.VM.is_win = vm_is_win
    qemu_vm.VM.is_rhel7 = vm_is_rhel7
    qemu_vm.VM.is_rhel6 = vm_is_rhel6
    qemu_vm.VM.info = vm_info
    qemu_vm.VM.error = vm_error


def vm_ssn(test, vm_name):
    """Usability function. Get objects VM and its session.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Returns
    -------
    tupe
        VM object and its session.

    """
    vm = test.vms[vm_name]
    ssn = test.sessions[vm_name]
    return (vm, ssn)


def vm_assn(test, vm_name):
    """Usability function. Get objects VM and its admin session.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Returns
    -------
    tupe
        VM object and its admin session.

    """
    vm = test.vms[vm_name]
    ssn = test.sessions_admin[vm_name]
    return (vm, ssn)


def vm_ssn_cfg(test, vm_name):
    """Usability function. Get objects VM, session, test config.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Returns
    -------
    tupe
        VM object, session, test config.

    """
    vm = test.vms[vm_name]
    ssn = test.sessions[vm_name]
    cfg = test.cfg
    return (vm, ssn, cfg)


def vm_assn_cfg(test, vm_name):
    """Usability function. Get objects VM, admin session, test config.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Returns
    -------
    tupe
        VM object, admin session, test config.

    """
    vm = test.vms[vm_name]
    ssn = test.sessions_admin[vm_name]
    cfg = test.cfg
    return (vm, ssn, cfg)


class SpiceUtilsError(Exception):
    """Exception raised in case the lib API fails."""


class SpiceTestFail(exceptions.TestFail):
    """Unknow VM type."""

    def __init__(self, test, *args, **kwargs):
        super(Exception, self).__init__(args, kwargs)
        if is_yes(test.cfg.pause_on_fail) or is_yes(test.cfg.pause_on_end):
            # 1 hour
            seconds = 60 * 60 * 10
            logging.error("Test %s has failed. Do nothing for %s seconds.",
                          test.cfg.id, seconds)
            time.sleep(seconds)


def finish_test(test):
    """Could be located at the end of the tests."""
    if is_yes(test.cfg.pause_on_end):
        # 1 hour
        seconds = 60 * 60
        logging.info("Test %s is finished. Do nothing for %s seconds.",
                      test.cfg.id, seconds)
        time.sleep(seconds)


class SpiceUtilsUnknownVmType(SpiceUtilsError):
    """Unknow VM type."""

    def __init__(self, vm_name, *args, **kwargs):
        super(SpiceUtilsUnknownVmType, self).__init__(args, kwargs)
        self.vm_name = vm_name

    def __str__(self):
        return "Unkon VM type: %s" % self.vm_name


class SpiceUtilsBadVmType(SpiceUtilsError):
    """Bad VM type."""
    def __init__(self, vm_name, *args, **kwargs):
        super(SpiceUtilsBadVmType, self).__init__(args, kwargs)
        self.vm_name = vm_name

    def __str__(self):
        return "Bad and unexpected VM type: %s." % self.vm_name


# ..todo:: or aexpect.xxx ???
class SpiceUtilsCmdRun(SpiceUtilsError):
    """Fail to run cmd on VM."""
    def __init__(self, vm_name, cmd, output, *args, **kwargs):
        super(SpiceUtilsCmdRun, self).__init__(args, kwargs)
        self.cmd = cmd
        self.output = output
        self.vm_name = vm_name

    def __str__(self):
        return "Command: {0} failed at: {1} with output: {2}".format(
            self.cmd, self.vm_name, self.output)


def check_usb_policy(test, vm_name):
    """Check USB policy in polkit file.

    Returns
    -------
    bool
        Status of grep command. If pattern is found 0 is returned. 0 in python
        is False so negative of grep is returned.
    """
    logging.info("Checking USB policy on %s", vm_name)
    vm = test.vms[vm_name]
    if not vm.is_linux():
        raise SpiceUtilsBadVmType(vm_name)
    cmd = "grep \"<allow_any>yes\" " + USB_POLICY_FILE
    session = test.sessions[vm_name]
    try:
        cmd_status = session.cmd_status(cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
    logging.info("USB policy at vm %s is %s.", vm_name, cmd_status)
    # Non 0 exit code is False. Success exec e.g. 0 - is True
    return not cmd_status


def add_usb_policy(test, vm_name):
    """Add USB policy to policykit file.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Raises
    ------
    SpiceUtilsBadVmType
        Bad VM type.

    """
    cfg = test.cfg
    vm = test.vms[vm_name]
    logging.debug("Sending %s to %s", USB_POLICY_FILE_SRC, vm_name)
    vm.copy_files_to(USB_POLICY_FILE_SRC,
                     USB_POLICY_FILE,
                     username=cfg.username,
                     password=cfg.password)


def _is_pid_alive(test, vm_name, pid):
    """Verify the process is still alive.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    pid : str
        Process that is to be checked.

    """
    vm, ssn = vm_ssn(test, vm_name)
    if not vm.is_linux():
        raise SpiceUtilsBadVmType(vm_name)
    try:
        ssn.cmd("ps -p %s" % pid)
    except aexpect.ShellCmdError:
        # Raised if the exit status is nonzero.
        return False
    except aexpect.ShellError, details:
        logging.info("Can't get current win name: %s", details)
        raise SpiceUtilsError("Can't get %s PID info at %s" % (
            pid, vm_name))
    return True


# ..todo:: change function name.
def str_input(test, vm_name, string):
    """Sends string trough vm.send_key(). The string could be spice_password.

    Notes
    -----
    After string will be send Enter.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    string : str
        Arbitrary string to be send to VM as keyboard events.

    """
    logging.info("Passing string '%s' as kbd events to the %s.", string,
                 vm_name)
    char_mapping = {":": "shift-semicolon",
                    ",": "comma",
                    ".": "dot",
                    "/": "slash",
                    "?": "shift-slash",
                    "=": "equal"}
    vm = test.vms[vm_name]
    for character in string:
        if character in char_mapping:
            character = char_mapping[character]
        vm.send_key(character)
    # Enter
    vm.send_key("kp_enter")


def print_rv_version(test, vm_name):
    """Prints remote-viewer and spice-gtk version available inside.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    rv_binary : str
        remote-viewer binary.

        if cfg.rv_ld_library_path:
            xxcmd = "LD_LIBRARY_PATH=/usr/local/lib %s" % cfg.rv_binary
        else:
            xxcmd = cfg.rv_binary
        try:
    """
    _, ssn, cfg = vm_ssn_cfg(test, vm_name)
    try:
        rv_ver = ssn.cmd(cfg.rv_binary + " -V")
        spice_gtk_ver = ssn.cmd(cfg.rv_binary + " --spice-gtk-version")
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
    logging.info("%s: remote-viewer version: %s", vm_name, rv_ver)
    logging.info("%s: spice-gtk version: %s", vm_name, spice_gtk_ver)

    #    except aexpect.ShellStatusError as ShellProcessTerminatedError:
    #        # Sometimes It fails with Status error, ingore it and continue.
    #        # It's not that important to have printed versions in the log.
    #        logging.debug(
    #            "Ignoring a Status Exception that occurs from calling print"
    #            "versions of remote-viewer or spice-gtk"
    #        )


def start_vdagent(test, vm_name):
    """Sending start the spice-vdagentd service.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn, cfg = vm_ssn_cfg(test, vm_name)
    if vm.is_linux():
        cmd = r"service spice-vdagentd start"
    elif vm.is_win():
        cmd = r'net start "RHEV Spice Agent"'
    else:
        raise SpiceUtilsUnknownVmType(vm_name)
    try:
        ssn.cmd(cmd, print_func=logging.info, timeout=cfg.test_timeout)
    except aexpect.ShellStatusError:
        logging.debug('Status code of "%s" was not obtained, most likely'
                      "due to a problem with colored output", cmd)
    except aexpect.ShellCmdError, e:
        logging.warn("Starting Vdagent May Not Have Started Properly")
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)


def restart_vdagent(test, vm_name):
    """Restart the spice-vdagentd service on VM.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn, cfg = vm_ssn_cfg(test, vm_name)
    if vm.is_linux():
        cmd = r"service spice-vdagentd restart"
        try:
            ssn.cmd(cmd, print_func=logging.info, timeout=cfg.test_timeout)
        except aexpect.ShellCmdError:
            raise SpiceUtilsError("Couldn't restart spice vdagent process")
        except:
            raise SpiceUtilsError("Guest Vdagent Daemon Check failed")
        logging.debug("End of Spice Vdagent Daemon  Restart.")
    elif vm.is_win():
        try:
            try:
                cmd = 'net stop "RHEV Spice Agent"'
                ssn.cmd(cmd, print_func=logging.info)
            except aexpect.ShellCmdError:
                logging.debug("Failed to stop the service, may have been "
                              "because it was not running")
            cmd = 'net start "RHEV Spice Agent"'
            ssn.cmd(cmd, print_func=logging.info, timeout=cfg.test_timeout)
        except aexpect.ShellCmdError:
            raise SpiceUtilsError("Couldn't restart spice vdagent process")
        except:
            raise SpiceUtilsError("Guest Vdagent Daemon Check failed")
        logging.debug("End of Spice Vdagent Daemon  Restart.")


def stop_vdagent(test, vm_name):
    """Sending commands to stop the spice-vdagentd service.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn, cfg = vm_ssn_cfg(test, vm_name)
    if vm.is_linux():
        cmd = r"service spice-vdagentd stop"
    elif vm.is_win():
        cmd = r'net stop "RHEV Spice Agent"'
    else:
        raise SpiceUtilsUnknownVmType(vm_name)
    try:
        ssn.cmd(cmd, print_func=logging.info, timeout=cfg.test_timeout)
    except aexpect.ShellStatusError:
        logging.debug('Status code of "%s" was not obtained, most likely'
                      "due to a problem with colored output", cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)


def verify_vdagent(test, vm_name):
    """Verifying vdagent is installed on a VM.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn = vm_ssn(test, vm_name)
    if vm.is_linux():
        cmd = r"rpm -qa | grep spice-vdagent"
        try:
            ssn.cmd(cmd, print_func=logging.info)
        finally:
            logging.debug("End of guest check to see if vdagent package"
                          " is available.")
    elif vm.is_win():
        cmd = r'net start | FIND "Spice"'
        try:
            output = ssn.cmd(cmd, print_func=logging.info)
            if "Spice" in output:
                logging.info("Guest vdagent is running")
        finally:
            logging.debug("End of guest check to see if vdagent is running")
    else:
        raise SpiceUtilsError("os_type passed to verify_vdagent is invalid")


def get_vdagent_status(test, vm_name):
    """Return the status of vdagent.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn = vm_ssn(test, vm_name)
    output = ""
    if vm.is_linux():
        cmd = "service spice-vdagentd status"
        try:
            output = ssn.cmd(cmd, print_func=logging.info)
        except aexpect.ShellCmdError:
            # getting the status of vdagent stopped returns 3, which results in
            # a aexpect.ShellCmdError
            return "stopped"
        except:
            logging.info("Unexpected error: %s", sys.exc_info()[0])
            raise SpiceUtilsError(
                "Failed attempting to get status of spice-vdagentd")
        return output
    elif vm.is_win():
        cmd = 'net start | FIND "Spice"'
        try:
            output = ssn.cmd(cmd, print_func=logging.info)
        except aexpect.ShellCmdError:
            return "stopped"
        except:
            logging.info("Unexpected error: %s", sys.exc_info()[0])
            raise SpiceUtilsError(
                "Failed attempting to get status of spice-vdagentd")
        return "running"


def verify_virtio(test, vm_name):
    """Verify Virtio linux driver is properly loaded.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn, cfg = vm_ssn_cfg(test, vm_name)
    if vm.is_linux():
        # cmd = "lsmod | grep virtio_console"
        cmd = "ls /dev/virtio-ports/"
        try:
            ssn.cmd(cmd, print_func=logging.info)
        finally:
            logging.debug("End of guest check of the Virtio-Serial Driver")
    elif vm.is_win():
        cmd = (cfg.pnputil + " /e")
        try:
            output = ssn.cmd(cmd, print_func=logging.info)
            if "System devices" in output:
                logging.info("Virtio Serial driver is installed")
        finally:
            logging.debug("End of guest check of Virtio-Serial driver")
    else:
        raise SpiceUtilsError("os_type passed to verify_vdagent is invalid")


def install_rv_win(test, vm_name):
    """Install remote-viewer on a windows client.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn, cfg = vm_ssn_cfg(test, vm_name)
    if not vm.is_win():
        raise SpiceUtilsBadVmType(vm_name)
    vm.copy_files_to(cfg.host_path, cfg.client_path_rv)
    cmd = 'start /wait msiexec /i ' + \
        cfg.client_path_rv + \
        r' INSTALLDIR="C:\virt-viewer"'
    try:
        ssn.cmd_output(cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)


def install_usbclerk_win(test, vm_name):
    """Install usbclerk on a windows client.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn, cfg = vm_ssn_cfg(test, vm_name)
    if not vm.is_win():
        raise SpiceUtilsBadVmType(vm_name)
    # ..todo:: host_path - fix
    vm.copy_files_to(cfg.host_path, cfg.client_path_usbc)
    try:
        cmd = "start /wait msiexec /i " + cfg.client_path_usbc + " /qn"
        ssn.cmd_output(cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)


def clear_interface(test, vm_name):
    """Clears user GUI interface of a vm without restart.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Raises
    ------
    SpiceUtilsUnknownVmType
        Unknow VM type.

    """
    vm = test.vms[vm_name]
    if vm.is_win():
        clear_interface_windows(test, vm_name)
    elif vm.is_linux():
        restart_session_linux(test, vm_name)
    else:
        raise SpiceUtilsUnknownVmType


def install_rpm(test, vm_name, rpm):
    """Install RPM package on a VM.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    rpm : str
        Path to RPM to be installed. It could be path to .rpm file, or RPM
        name.
    """
    vm, ssn = vm_assn(test, vm_name)
    if not vm.is_linux():
        raise SpiceUtilsBadVmType(vm_name)
    vm.info("Install RPM : %s.", rpm)
    pkg = rpm
    if rpm.endswith('.rpm'):
        pkg = rpm[:-4]
    try:
        cmd = 'rpm -q %s' % pkg
        status = ssn.cmd_status(cmd)
        if status == 0:
            vm.info("RPM %s is already installed.", pkg)
            return
        ssn.cmd("yum -y install %s" % rpm, timeout=500)
    except aexpect.ShellCmdError as e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)


def restart_session_linux(test, vm_name):
    """Restart graphical session at VM.

    Notes
    -----
        To accomplish this change SystemD/SystemV runlevels from graphical mode
        to multiuser mode, and back.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Raises
    ------
    SpiceUtilsError
        Fails to restart Graphical session.

    """
    logging.info("Begin: restart graphical session at VM: %s", vm_name)
    vm, ssn = vm_assn(test, vm_name)
    runner = remote.RemoteRunner(session=ssn)
    srv_mng = service.Factory.create_service(run=runner.run)
    srv_mng.set_target("multi-user.target")  # pylint: disable=no-member
    xsession_flag_cmd = r"ss -x src '*X11-unix*' | grep -q -s 'X11'"

    def is_x(active):
        """Looks up if X is "active"."""
        r = runner.run(xsession_flag_cmd, ignore_status=True)
        return not r.exit_status == active

    if not utils_misc.wait_for(lambda: is_x(False), 300, first=30, step=30):
        raise SpiceUtilsError("Can't switch to runlevel 3 at: %s" % vm_name)
    logging.info("Check: no more active X session at VM: %s", vm_name)
    srv_mng.set_target("graphical.target")  # pylint: disable=no-member
    if not utils_misc.wait_for(lambda: is_x(True), 300, first=30, step=30):
        raise SpiceUtilsError("Can't switch to runlevel 5 at: %s" % vm_name)
    logging.info("Done: restart graphical session at VM: %s", vm_name)
    """Export essentials variables per SSH session."""
    if vm.is_linux():
        vm, ssn = vm_ssn(test, vm_name)
        ssn.cmd("export DISPLAY=:0.0")
        var_list = ['DBUS_SESSION_BUS_ADDRESS']
        for var_name in var_list:
            val = get_x_var(test, vm_name, var_name)
            if val:
                logging.info("%s export %s == %s", vm_name, var_name, var_val)
                cmd = r"export %s='%s'" % (var_name, var_val)
                ssn.cmd(cmd)




def wait_for_win(test, vm_name, pattern, prop="_NET_WM_NAME"):
    """Wait until active window has "pattern" in window name.

    ..todo:: Write same function for MS Windows.

    Info
    ----
    http://superuser.com/questions/382616/detecting-currently-active-window

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    pattern : str
        Pattern for window name.

    Raises
    ------
    SpiceUtilsError
        Timeout and no window was found.

    """
    ssn = test.sessions[vm_name]
    cmd = r"xprop -notype -id " \
        r"$(xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2) "
    cmd += prop

    def is_active():
        """Test if window is active."""
        try:
            output = ssn.cmd(cmd)
        except aexpect.ShellError as e:
            raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
        logging.info("Current win name: %s", output)
        return pattern in output

    if not utils_misc.wait_for(is_active, 300, first=30, step=30):
        raise SpiceUtilsError("Can't find active window with name %s at: %s" %
                              (pattern, vm_name))


def clear_interface_windows(test, vm_name):
    """Kill remote-viewer.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Raises
    ------
    SpiceUtilsError
        Fails to kill remote-viewer.

    """
    ssn = test.sessions[vm_name]
    # .. todo:: check if remote-viewer is running before killing it.
    cmd = r"taskkill /F /IM remote-viewer.exe"
    try:
        ssn.cmd(cmd)
    except aexpect.ShellError, details:
        logging.info("Remote-viewer has not been killed: %s", details)


def deploy_epel_repo(test, vm_name):
    """Deploy epel repository to RHEL VM.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    # Check existence of epel repository
    _, ssn, cfg = vm_ssn_cfg(test, vm_name)
    cmd = ("if [ ! -f /etc/yum.repos.d/epel.repo ]; then echo"
           " \"NeedsInstall\"; fi")
    output = ssn.cmd(cmd, timeout=10)
    # Install epel repository If needed
    if "NeedsInstall" in output:
        arch = ssn.cmd("arch")
        if "i686" in arch:
            arch = "i386"
        else:
            arch = arch[:-1]
        if "release 5" in ssn.cmd("cat /etc/redhat-release"):
            cmd = ("yum -y localinstall http://download.fedoraproject.org/"
                   "pub/epel/5/%s/epel-release-5-4.noarch.rpm 2>&1" % arch)
            logging.info("Installing epel repository to %s", cfg.guest_vm)
            ssn.cmd(cmd, print_func=logging.info, timeout=90)
        elif "release 6" in ssn.cmd("cat /etc/redhat-release"):
            cmd = ("yum -y localinstall http://download.fedoraproject.org/"
                   "pub/epel/6/%s/epel-release-6-8.noarch.rpm 2>&1" % arch)
            logging.info("Installing epel repository to %s", cfg.guest_vm)
            ssn.cmd(cmd, print_func=logging.info, timeout=90)
        else:
            raise Exception("Unsupported RHEL guest")


def set_resolution(test, vm_name, res, display):
    """Sets resolution of qxl device on a VM.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    res : str
        Resolution.
    display : str
        Target display.

    """
    _, ssn = vm_ssn(test, vm_name)
    logging.info("Seeting resolution to %s on %s", res, vm_name)
    cmd = "xrandr --output %s --mode %s " % (display, res)
    try:
        ssn.cmd(cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)


def get_connected_displays(test, vm_name):
    """Get list of video devices on a VM.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Return
    ------
        List of active displays on the VM.

    """
    _, ssn = vm_ssn(test, vm_name)
    cmd = "xrandr | grep -E '[[:space:]]connected[[:space:]]'"
    try:
        raw = ssn.cmd_output(cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
    displays = [a.split()[0] for a in raw.split('n') if a is not '']
    return displays


def get_display_resolution(test, vm_name):
    """Returns list of resolutions on all displays of a VM.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Return
    ------
        List of resolutions.
    """
    _, ssn = vm_ssn(test, vm_name)
    cmd = "xrandr | grep '*'"
    try:
        raw = ssn.cmd_output(cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
    res = [a.split()[0] for a in raw.split('\n') if a is not '']
    return res


def get_open_window_ids(test, vm_name, fltr):
    """Get X server window ids of active windows matching filter.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    fltr: str.
        Name of binary/title.

    Return
    ------
        List of active windows matching filter.

    """
    _, ssn = vm_ssn(test, vm_name)
    if not fltr:
        logging.error("Bad filter.")
        return
    xwininfo = ssn.cmd_output("xwininfo -tree -root")
    ids = [a.split()[0] for a in xwininfo.split('\n') if fltr in a]
    windows = []
    for window in ids:
        out = subprocess.check_output('xprop -id %s' % window, shell=True)
        for line in out.split('\n'):
            if ('NET_WM_WINDOW_TYPE' in line and
                    'ET_WM_WINDOW_TYPE_NORMAL' in line):
                windows.append(window)
    return windows


def get_window_props(test, vm_name, win_id):
    """Get full properties of a window with speficied ID.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    win_id : str
        X server id of a window.

    Return
    ------
        Returns output of xprop -id.

    """
    vm, ssn = vm_ssn(test, vm_name)
    if not vm.is_linux():
        raise SpiceUtilsBadVmType(vm_name)
    cmd = "xprop -id %s" % win_id
    try:
        raw = ssn.cmd_output(cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
    return raw


def get_wininfo(test, vm_name, win_id):
    """Get xwininfo for windows of a specified ID.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    win_id : str
        X server id of a window.

    Return
    ------
        Output xwininfo -id %id on the session.

    """
    vm, ssn = vm_ssn(test, vm_name)
    if not vm.is_linux():
        raise SpiceUtilsBadVmType(vm_name)
    cmd = "xwininfo -id %s" % win_id
    try:
        raw = ssn.cmd_output(cmd)
    except aexpect.ShellCmdError, e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
    return raw


def get_window_geometry(test, vm_name, win_id):
    """Get resolution of a window.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    win_id : str
        ID of the window of interest.

    Return
    ------
        WidthxHeight of the selected window.

    """
    xwininfo = get_wininfo(test, vm_name, win_id)
    for line in xwininfo:
        if '-geometry' in line:
            return re.split(r'[\+\-\W]', line)[1]  # ..todo: review


# ..todo:: rename function name.
def kill_by_name(test, vm_name, app_name):
    """Kill selected app on selected VM.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    app_name : str
        Name of the binary.

    """
    vm, ssn = vm_ssn(test, vm_name)
    if vm.is_linux():
        try:
            cmd = "pkill %s" % app_name.split(os.path.sep)[-1]
            output = ssn.cmd_output(cmd)
        except aexpect.ShellCmdError:
            if output == 1:
                pass
            else:
                raise SpiceUtilsError("Cannot kill it.")
    elif vm.is_win():
        ssn.cmd_output("taskkill /F /IM %s" % app_name.split('\\')[-1])


def is_yes(string):
    """Wrapper around util.strtobool.

    Parameters
    ----------
    string : str
        String to check.

    Note
    ----
    https://docs.python.org/2/distutils/apiref.html#distutils.util.strtobool
    True values are y, yes, t, true, on and 1; false values are n, no, f,
    false, off and 0. Raises ValueError if val is anything else.
    """
    if not string:
        return False
    return util.strtobool(string)


def is_fullscreen_xprop(test, vm_name, win_name, window=0):
    """Tests if remote-viewer windows is fullscreen based on xprop.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.
    win_name : str
        Window name.
    window : int
        Which window is tested (0-3).

    Returns
    -------
    Returns True if fullscreen property is set.

    """
    win_id = get_open_window_ids(test, vm_name, win_name)[window]
    props = get_window_props(test, vm_name, win_id)
    for prop in props.split('\n'):
        if ('_NET_WM_STATE(ATOM)' in prop and
                '_NET_WM_STATE_FULLSCREEN ' in prop):
            return True


def window_resolution(test, vm_name, win_name, window=0):
    """ ..todo:: write me
    """
    win_id = get_open_window_ids(test, vm_name, win_name)[window]
    return get_window_geometry(test, vm_name, win_id)


def get_res(test, vm_name):
    """Gets the resolution of a VM

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Return
    ------

    """
    vm, ssn = vm_ssn(test, vm_name)
    if not vm.is_linux():
        raise SpiceUtilsBadVmType(vm_name)
    try:
        guest_res_raw = ssn.cmd_output("xrandr -d :0 2> /dev/null | grep '*'")
        guest_res = guest_res_raw.split()[0]
    except aexpect.ShellCmdError as e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
    except IndexError:
        raise SpiceUtilsError("Can't get resolution.")
    return guest_res

# ..todo:: implement
# def get_fullscreen_windows(test):
#    cfg = test.cfg
#    windows = self.get_windows_ids()

def get_corners(test, vm_name, win_title):
    """Gets the coordinates of the 4 corners of the window.

    Info
    ----
    http://www.x.org/archive/X11R6.8.0/doc/X.7.html#sect6

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Return
    ------
    list
        Corners in format: [('+470', '+187'), ('-232', '+187'),
                            ('-232', '-13'), ('+470', '-13')]

    """
    _, ssn = vm_ssn(test, vm_name)
    rv_xinfo_cmd = "xwininfo -name %s" % win_title
    rv_xinfo_cmd += " | grep Corners"
    try:
        # Expected format:   Corners:  +470+187  -232+187  -232-13  +470-13
        raw_out = client_session.cmd(rv_xinfo_cmd)
        line = raw_out.strip()
    except aexpect.ShellCmdError as e:
        raise RVSessionError(str(e))
    except IndexError:
        raise RVSessionError("Could not get the geometry for %s", win_title)
    corners = [tuple(re.findall("[+-]\d+",i)) for i in line.split()[1:]]
    return corners


def get_geom(test, vm_name, win_title):
    """Gets the geometry of the rv_window.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Returns
    -------
    tuple
        Geometry of RV window. (x,y)

    """
    xinfo_cmd = "xwininfo -name %s" % win_title
    xinfo_cmd += " | grep geometry"
    _, ssn = vm_ssn(test, vm_name)
    try:
        # Expected '  -geometry 898x700+470-13'
        res_raw = ssn.cmd(rv_xinfo_cmd)
        res = re.findall('\d+x\d+', res_raw)[0]
    except aexpect.ShellCmdError as e:
        raise RVSessionError(str(e))
    except IndexError:
        raise RVSessionError("Could not get the geometry of the window %s.",
                             win_title)
    logging.debug("Window %s has geometry: %s", win_title, res)
    return str2res(rv_res)


def str2res(res):
    """Convert resolution in str for: XXXxYYY to tuple.

    Parameters
    ----------
    res : str
        Resolution.

    Returns
    -------
    tuple
        Resolution.

    """
    width = int(res.split('x')[0])
    # The second split of - is a workaround because the xwinfo sometimes
    # prints out dashes after the resolution for some reason.
    height = int(res.split('x')[1].split('-')[0])
    return (width, height)


def res_gt(res1, res2):
    """Test res2 > res1

    Parameters
    ----------
    res1: tuple
        resolution
    res2: tuple
        resolution

    Returns
    -------
    bool
        res1 > res2

    """
    return h2 > h1 and w2 > w1


def res_eq(res1, res2):
    """Test res1 == res2

    Parameters
    ----------
    res1: tuple
        resolution
    res2: tuple
        resolution

    Returns
    -------
    bool
        res1 == res2

    """
    return res1 == res2


def is_eq(val, tgt, err_limit):
    """Test if val is equal to tgt in allowable limits.

    Parameters
    ----------
    val :
        Value to check.
    tgt :
        Specimen.
    err_limit :
        Acceptable percent change of x2 from x1.

    init: original integer value
    post: integer that must be within an acceptable percent of x1

    """
    if not isinstance(tgt, int):
        tgt = int(tgt)
    if not isinstance(post, int):
        val = int(val)
    if not isinstance(err_limit, int):
        err_limit = int(err_limit)
    sub = tgt * err_limit / 100
    bottom = tgt - sub
    up = tgt + sub
    ret =  bottom <= val and val <= up
    logging.info("Stating %d <= %d <= %d is %s.", bottom, val, up, str(ret))
    return ret


def get_x_var(test, vm_name, var_name):
    """Gets the env variable value by its name from X session.

    Info
    ----
    It is no straight way to get variable value from X session. If you try to
    read var value from SSH session it could be different from X session var or
    absent. The strategy used in this function is:

        1. Run terminal. Terminal will be disconnected from SSH session. The
        parent of the terminal will be X manager. Terminal inherits variables
        from X manager.  Dump variables to file.
        2. Read the file for interested variable.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    Returns
    -------
    str
        Env variable value.

    """
    _, ssn = vm_ssn(test, vm_name)
    terminal = 'gnome-terminal'
    dump_file = tempfile.mktemp()
    dump_env_cmd = """'sh -c "export -p > %s"'""" % dump_file
    cmd1 = terminal + " -e " + dump_env_cmd
    cmd2 = r'cat "%s"' % dump_file
    pattern = "\s%s=.+" % var_name
    try:
        ssn.cmd(cmd1)
        env = ssn.cmd(cmd2)
        ret = re.findall(pattern, env)
        if ret:
            ret = ret[0]
            ret = ret.strip()
            ret = ret.split('=', 1)[1]
        else:
            ret = ""
    except aexpect.ShellCmdError as e:
        raise SpiceUtilsCmdRun(vm_name, e.cmd, e.output)
    logging.debug("%s has %s = %s", var_name, ret)
    return ret


def turn_accessibility(test, vm_name, on=True):
    """Turn accessibility on vm.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    vm_name : str
        VM name.

    """
    vm, ssn = vm_ssn(test, vm_name)
    if not vm.is_linux():
        raise SpiceUtilsBadVmType(vm_name)
    if on:
        val = 'true'
    else:
        val = 'false'
    if vm.is_rhel6():
        # gconftool-2 --get "/desktop/gnome/interface/accessibility"
        # temporarily (for a single session) enable Accessibility:
        # GNOME_ACCESSIBILITY=1
        # session.cmd("gconftool-2 --shutdown")
        cmd = "gconftool-2 --set /desktop/gnome/interface/accessibility --type bool %s" % val
        ssn.cmd(cmd)
    elif vm.is_rhel7():
        cmd = "gsettings set org.gnome.desktop.interface toolkit-accessibility %s" % val
        ssn.cmd(cmd)
