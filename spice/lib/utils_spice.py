"""
Common spice test utility functions.

"""
import os
import logging
import time
import sys
import subprocess
import re
import aexpect
from avocado.core import exceptions
from virttest import qemu_vm
from spice.lib import conf


def is_win(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_type") == "windows":
        return True
    return False


def is_linux(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_type") == "linux":
        return True
    return False


def extend_vm():
    """Extend qemu.VM(virt_vm.BaseVM) with useful methods.
    """
    qemu_vm.VM.is_linux = is_linux
    qemu_vm.VM.is_win = is_win

# TODO: Rework migration, add migration as a option of the session, but that
# can wait


class RVConnectError(Exception):
    """Exception raised in case that remote-viewer fails to connect"""
    pass


def check_usb_policy(virtm, params):
    """
    Check USB policy in polkit file.
    returns status of grep command. If pattern is found 0 is returned. 0 in
    python is False so negative of grep is returned
    """
    logging.info("Checking USB policy")
    file_name = ("/usr/share/polkit-1/actions/org.spice-space."
                 "lowlevelusbaccess.policy")
    cmd = "grep \"<allow_any>yes\" " + file_name
    timeout = int(params.get("login_timeout", 360))
    client_root_session = virtm.wait_for_login(timeout=timeout,
                                               username=conf.USERNAME,
                                               password=conf.PASSWORD)
    usb_policy = client_root_session.cmd_status(cmd)
    logging.info("Policy %s", usb_policy)
    if usb_policy:
        return False
    else:
        return True


def add_usb_policy(virtm):
    """
    Add USB policy to policykit file
    """
    logging.info("Adding USB policy")
    remote_file_path = ("/usr/share/polkit-1/actions/org.spice-space."
                        "lowlevelusbaccess.policy")
    file_to_upload = "deps/org.spice-space.lowlevelusbaccess.policy"
    file_to_upload_path = os.path.join("deps", file_to_upload)
    logging.debug("Sending %s", file_to_upload_path)
    virtm.copy_files_to(file_to_upload_path,
                        remote_file_path,
                        username=conf.USERNAME,
                        password=conf.PASSWORD)


def _is_pid_alive(session, pid):
    """
    verify the process is still alive

    @param session:- established ssh session
    @param pid: - process that is to be checked
    """

    try:
        session.cmd("ps -p %s" % pid)
    except aexpect.ShellCmdError:
        return False

    return True


def str_input(client_vm, ticket):
    """
    sends spice_password trough vm.send_key()
    @param client_session - vm() object
    @param ticket - use params.get("spice_password")
    """
    logging.info("Passing ticket '%s' to the remote-viewer.", ticket)
    char_mapping = {":": "shift-semicolon",
                    ",": "comma",
                    ".": "dot",
                    "/": "slash",
                    "?": "shift-slash",
                    "=": "equal"}
    for character in ticket:
        if character in char_mapping:
            character = char_mapping[character]
        client_vm.send_key(character)

    client_vm.send_key("kp_enter")  # send enter


def print_rv_version(client_session, rv_binary):
    """
    prints remote-viewer and spice-gtk version available inside client_session
    @param client_session - vm.wait_for_login()
    @param rv_binary - remote-viewer binary
    """
    logging.info("remote-viewer version: %s",
                 client_session.cmd(rv_binary + " -V"))
    logging.info("spice-gtk version: %s",
                 client_session.cmd(rv_binary + " --spice-gtk-version"))


def start_vdagent(guest_session, os_type, test_timeout):
    """
    Sending commands to start the spice-vdagentd service

    @param guest_session: ssh session of the VM
    @param os_type: os the command is to be run on (windows or linux)
    @param test_timeout: timeout time for the cmds
    """
    if os_type == "linux":
        cmd = "service spice-vdagentd start"
    elif os_type == "windows":
        cmd = 'net start "RHEV Spice Agent"'
    else:
        raise exceptions.TestFail(
            "Error: os_type passed to stop_vdagent is invalid")
    try:
        guest_session.cmd(cmd, print_func=logging.info,
                          timeout=test_timeout)
    except aexpect.ShellStatusError:
        logging.debug("Status code of \"%s\" was not obtained, most likely"
                      "due to a problem with colored output", cmd)
    except:
        logging.warn("Starting Vdagent May Not Have Started Properly")
        # raise error.TestFail("Guest Vdagent Daemon Start failed")

    logging.debug("------------ End of guest checking for Spice Vdagent"
                  " Daemon ------------")
    wait_timeout(3)


def restart_vdagent(guest_session, os_type, test_timeout):
    """
    Sending commands to restart the spice-vdagentd service
    @param guest_session: ssh session of the VM
    @param os_type: os the command is to be run on (windows or linux)
    @param test_timeout: timeout time for the cmds

    """
    if os_type == "linux":
        cmd = "service spice-vdagentd restart"
        try:
            guest_session.cmd(cmd, print_func=logging.info,
                              timeout=test_timeout)
        except aexpect.ShellCmdError:
            raise exceptions.TestFail("Couldn't restart spice vdagent process")
        except:
            raise exceptions.TestFail("Guest Vdagent Daemon Check failed")

        logging.debug("------------ End of Spice Vdagent"
                      " Daemon  Restart ------------")
    elif os_type == "windows":
        try:
            try:
                guest_session.cmd('net stop "RHEV Spice Agent"',
                                  print_func=logging.info,
                                  timeout=test_timeout)
            except:
                logging.debug("Failed to stop the service, may have been "
                              "because it was not running")
            guest_session.cmd('net start "RHEV Spice Agent"',
                              print_func=logging.info, timeout=test_timeout)
        except aexpect.ShellCmdError:
            raise exceptions.TestFail("Couldn't restart spice vdagent process")
        except:
            raise exceptions.TestFail("Guest Vdagent Daemon Check failed")

        logging.debug("------------ End of Spice Vdagent"
                      " Daemon  Restart ------------")

    wait_timeout(3)


def stop_vdagent(guest_session, os_type, test_timeout):
    """
    Sending commands to stop the spice-vdagentd service

    @param guest_session: ssh session of the VM
    @param os_type: os the command is to be run on (windows or linux)
    @param test_timeout: timeout time for the cmds
    """
    if os_type == "linux":
        cmd = "service spice-vdagentd stop"
    elif os_type == "windows":
        cmd = 'net stop "RHEV Spice Agent"'
    else:
        raise exceptions.TestFail(
            "Error: os_type passed to stop_vdagent is invalid")
    try:
        guest_session.cmd(cmd, print_func=logging.info,
                          timeout=test_timeout)
    except aexpect.ShellStatusError:
        logging.debug("Status code of \"%s\" was not obtained, most likely"
                      "due to a problem with colored output", cmd)
    except aexpect.ShellCmdError:
        raise exceptions.TestFail("Couldn't turn off spice vdagent process")
    except:
        logging.warn("Starting Vdagent May Not Have Stopped Properly")
        # raise error.TestFail("Guest Vdagent Daemon Check failed")

    logging.debug("------------ End of guest checking for Spice Vdagent"
                  " Daemon ------------")
    wait_timeout(3)


def verify_vdagent(guest_session, os_type, test_timeout):
    """
    Verifying vdagent is installed on a VM

    @param guest_session: ssh session of the VM
    @param os_type: os the command is to be run on (windows or linux)
    @param test_timeout: timeout time for the cmds
    """
    if os_type == "linux":
        cmd = "rpm -qa | grep spice-vdagent"

        try:
            guest_session.cmd(cmd, print_func=logging.info,
                              timeout=test_timeout)
        finally:
            logging.debug("---- End of guest check to see if vdagent package"
                          " is available ----")
        wait_timeout(3)
    elif os_type == "windows":
        cmd = 'net start | FIND "Spice"'
        try:
            output = guest_session.cmd(cmd, print_func=logging.info,
                                       timeout=test_timeout)
            if "Spice" in output:
                logging.info("Guest vdagent is running")
        finally:
            logging.debug("End of guest check to see if vdagent is running")
        wait_timeout(3)
    else:
        raise exceptions.TestFail(
            "os_type passed to verify_vdagent is invalid")


def get_vdagent_status(vm_session, os_type, test_timeout):
    """
    Return the status of vdagent
    @param vm_session:  ssh session of the VM
    @param os_type: os the command is to be run on (windows or linux)
    @param test_timeout: timeout time for the cmd
    """
    output = ""

    if os_type == "linux":
        cmd = "service spice-vdagentd status"

        wait_timeout(3)
        try:
            output = vm_session.cmd(
                cmd, print_func=logging.info, timeout=test_timeout)
        except aexpect.ShellCmdError:
            # getting the status of vdagent stopped returns 3, which results in
            # a aexpect.ShellCmdError
            return "stopped"
        except:
            logging.info("Unexpected error: %s", sys.exc_info()[0])
            raise exceptions.TestFail(
                "Failed attempting to get status of spice-vdagentd")
        wait_timeout(3)
        return output
    elif os_type == "windows":
        cmd = 'net start | FIND "Spice"'
        try:
            output = vm_session.cmd(
                cmd, print_func=logging.info, timeout=test_timeout)
        except aexpect.ShellCmdError:
            return "stopped"
        except:
            logging.info("Unexpected error: %s", sys.exc_info()[0])
            raise exceptions.TestFail(
                "Failed attempting to get status of spice-vdagentd")
        wait_timeout(3)
        return "running"


def verify_virtio(guest_session, os_type, test_timeout):
    """
    Verify Virtio linux driver is properly loaded.

    @param guest_session: ssh session of the VM
    @param os_type: os the command is to be run on (windows or linux)
    @param test_timeout: timeout time for the cmds
    """
    if os_type == "linux":
        # cmd = "lsmod | grep virtio_console"
        cmd = "ls /dev/virtio-ports/"
        try:
            guest_session.cmd(cmd, print_func=logging.info,
                              timeout=test_timeout)
        finally:
            logging.debug("End of guest check of the Virtio-Serial Driver")
        wait_timeout(3)
    elif os_type == "windows":
        cmd = (r"C:\Windows\winsxs\amd64_microsoft-windows-pnputil_31bf3856ad364e35_6.1.7600.16385_none_5958b438d6388d15\PnPutil.exe /e")
        try:
            output = guest_session.cmd(cmd, print_func=logging.info,
                                       timeout=test_timeout)
            if "System devices" in output:
                logging.info("Virtio Serial driver is installed")
        finally:
            logging.debug("End of guest check of Virtio-Serial driver")
        wait_timeout(3)
    else:
        raise exceptions.TestFail(
            "os_type passed to verify_vdagent is invalid")


def install_rv_win(client, host_path, client_path='C:\\virt-viewer.msi'):
    """
    Install remote-viewer on a windows client

    @param client:      VM object
    @param host_path:   Location of installer on host
    @param client_path: Location of installer after copying
    """
    session = client.wait_for_login(
        timeout=int(client.params.get("login_timeout", 360)))
    client.copy_files_to(host_path, client_path)
    try:
        session.cmd_output('start /wait msiexec /i ' +
                           client_path +
                           ' INSTALLDIR="C:\\virt-viewer"')
    except:
        pass


def install_usbclerk_win(client, host_path, client_path="C:\\usbclerk.msi"):
    """
    Install remote-viewer on a windows client

    @param client:      VM object
    @param host_path:   Location of installer on host
    @param client_path: Location of installer after copying
    """
    session = client.wait_for_login(
        timeout=int(client.params.get("login_timeout", 360)))
    client.copy_files_to(host_path, client_path)
    try:
        session.cmd_output("start /wait msiexec /i " + client_path + " /qn")
    except:
        pass


def clear_interface(virtm, login_timeout=360, timeout=None):
    """
    Clears user interface of a vm without restart

    @param vm:      VM where cleaning is required
    @param login_timeout: timeout time for logging on
    @param timeout: wait time after clearing the interface

    """
    if virtm.params.get("os_type") == "windows":
        clear_interface_windows(virtm, timeout)
    else:
        clear_interface_linux(virtm, login_timeout, timeout)


def clear_interface_linux(virtm, login_timeout, timeout=None):
    """Clears user interface of a virtm without restart.

    Parameters
    ----------
    virtm : virttest.qemu_vm.VM
        VM where cleaning is required.
    login_timeout : int
        Seconds. Timeout to establish ssh connection to vm.
    timeout : Optional[int]
        Seconds. Whait until process gets be killed.
    """
    os_variant = virtm.params.get("os_variant")
    if os_variant == "rhel7":
        command = "gdm"
        pgrep_process = "'^gdm$'"
        if not timeout:
            timeout = 60
    else:
        command = "Xorg"
        pgrep_process = "Xorg"
        if not timeout:
            timeout = 15
    session = virtm.wait_for_login(username=conf.USERNAME,
                                   password=conf.PASSWORD,
                                   timeout=login_timeout)
    try:
        logging.info("Restarting X on: %s", virtm.name)
        pid = session.cmd("pgrep %s" % pgrep_process)
        session.cmd("killall %s" % command)
        utils_misc.wait_for(lambda: _is_pid_alive(session, pid),
                            10, timeout, 0.2)
    except:
        pass
    try:
        session.cmd("ps -C %s" % command)
    except:
        raise exceptions.TestFail("X/gdm not running")
    time.sleep(timeout)


def clear_interface_windows(virtm, timeout=None):
    """Kill remote-viewer.
    """
    session = virtm.wait_for_login()
    try:
        session.cmd("taskkill /F /IM remote-viewer.exe")
    except:
        logging.info("Remote-viewer not running")
    if timeout:
        time.sleep(timeout)


def deploy_epel_repo(guest_session, params):
    """
    Deploy epel repository to RHEL VM If It's RHEL6 or 5.

    @param guest_session: - ssh session to guest VM
    @param params: env params
    """

    # Check existence of epel repository
    cmd = ("if [ ! -f /etc/yum.repos.d/epel.repo ]; then echo"
           " \"NeedsInstall\"; fi")
    output = guest_session.cmd(cmd, timeout=10)
    # Install epel repository If needed
    if "NeedsInstall" in output:
        arch = guest_session.cmd("arch")
        if "i686" in arch:
            arch = "i386"
        else:
            arch = arch[:-1]
        if "release 5" in guest_session.cmd("cat /etc/redhat-release"):
            cmd = ("yum -y localinstall http://download.fedoraproject.org/"
                   "pub/epel/5/%s/epel-release-5-4.noarch.rpm 2>&1" % arch)
            logging.info("Installing epel repository to %s",
                         params.get("guest_vm"))
            guest_session.cmd(cmd, print_func=logging.info, timeout=90)
        elif "release 6" in guest_session.cmd("cat /etc/redhat-release"):
            cmd = ("yum -y localinstall http://download.fedoraproject.org/"
                   "pub/epel/6/%s/epel-release-6-8.noarch.rpm 2>&1" % arch)
            logging.info("Installing epel repository to %s",
                         params.get("guest_vm"))
            guest_session.cmd(cmd, print_func=logging.info, timeout=90)
        else:
            raise Exception("Unsupported RHEL guest")


def set_resolution(session, res, display='qxl-0'):
    """Sets resolution of qxl device on a VM

    :param session: Active session (connection) to the VM
    :param res: Target resolution WidthxSize
    :param display: Which device, default qxl-0
    :return:
    """
    logging.info("Seeting resolution to %s", res)
    session.cmd("xrandr --output %s --mode %s " % (display, res))


def get_connected_displays(session):
    """Returns list of video devices on a VM
    :param session: Active connection to the VM
    :return: List of active displays on the VM
    """
    raw = session.cmd_output(
        "xrandr | grep -E '[[:space:]]connected[[:space:]]'")
    displays = [a.split()[0] for a in raw.split('n') if a is not '']
    return displays


# TODO: Maybe a dict instead of a list...?
def get_display_resolution(session):
    """Returns list of resolutions on all displays of a VM
    :param session: Active connection to the VM
    :return: List of resolutions
    """
    raw = session.cmd_output("xrandr | grep '*'")
    res = [a.split()[0] for a in raw.split('\n') if a is not '']
    return res


def get_open_window_ids(session, filter):
    """ Get X server window ids of active windows matching filter

    :param session: Active connection to a VM
    :param filter: String; name of binary/title
    :return: List of active windows matching filter
    """
    if not filter:
        logging.error("Filter can't be None/''")
        return
    xwininfo = session.cmd_output("xwininfo -tree -root")
    ids = [a.split()[0] for a in xwininfo.split('\n') if filter in a]
    windows = []
    for window in ids:
        out = subprocess.check_output('xprop -id %s' % window, shell=True)
        for line in out.split('\n'):
            if ('NET_WM_WINDOW_TYPE' in line and
                    'ET_WM_WINDOW_TYPE_NORMAL' in line):
                windows.append(window)
    return windows


def get_window_props(session, id):
    """ Get full properties of a window with speficied ID

    :param session: Active connection to a VM
    :param id: X server id of a window
    :return: Returns output of xprop -id
    """
    return session.cmd_output("xprop -id %s" % id)


def get_wininfo(session, id):
    """ Get xwininfo for windows of a specified ID
    :param session: Active connection to a VM
    :param id: ID of the window
    :return: Output xwininfo -id %id on the session
    """
    return session.cmd_output("xwininfo -id %s" % id)


def get_window_geometry(session, id):
    """ Get resolution of a window

    :param session: Active connection to a VM
    :param id: ID of the window of interest
    :return: WidthxHeight of the selected window
    """
    xwininfo = get_wininfo(session, id)
    for line in xwininfo:
        if '-geometry' in line:
            return filter(re.split(r'[\+\-\W]'))[1]


# TODO: REMOVE THIS ONE!!! (just a tmp method to test locally)
def temp_windows(filter):
    xwininfo = subprocess.check_output("xwininfo -tree -root", shell=True)
    # for line in xwininfo.split('\n'):
    #    if filter in line:
    if not filter:
        logging.error("Filter can't be None/''")
        return
    ids = [a.split()[0] for a in xwininfo.split('\n') if filter in a]
    windows = []
    for window in ids:
        out = subprocess.check_output('xprop -id %s' % window, shell=True)
        for line in out.split('\n'):
            if ('NET_WM_WINDOW_TYPE' in line and
                    'ET_WM_WINDOW_TYPE_NORMAL' in line):
                windows.append(window)
    return windows


def wait_timeout(timeout=10):
    """
    time.sleep(timeout) + logging.debug(timeout)

    Parameters
    ----------
    timeout : int
        Suspend execution of the current thread for the given number of
        seconds.
    """
    logging.debug("Waiting (timeout=%s secs)", timeout)
    time.sleep(timeout)
