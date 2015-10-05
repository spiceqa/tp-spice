"""
Common spice test utility functions.

"""
import os
import logging
import socket
import time
import sys
import subprocess
import re
#from autotest.client.shared import error
#from aexpect import ShellCmdError, ShellStatusError
#from virttest import utils_net, utils_misc

# TODO: Rework migration, add migration as a option of the session, but that can wait


class RVConnectError(Exception):

    """Exception raised in case that remote-viewer fails to connect"""
    pass

def _is_pid_alive(session, pid):
    """
    verify the process is still alive

    :param session:- established session
    :param pid: - process that is to be checked
    """

    try:
        session.cmd("ps -p %s" % pid)
    except ShellCmdError:
        return False

    return True

def load_kernel_module(session, module):
    try:
        session.cmd_status("modprobe %s" % module)
    except ShellCmdError:
        logging.info("Failed to load kernel module: %s" %s)
        return False

def wait_timeout(timeout=10):
    """
    time.sleep(timeout) + logging.debug(timeout)

    :param timeout: default timeout = 10
    """
    logging.debug("Waiting (timeout=%ss)", timeout)
    time.sleep(timeout)


def kill_app(vm_name, app_name, params, env):
    """
    Kill selected app on selected VM

    :params vm_name - VM name in parameters
    :params app_name - name of application
    """
    vm = env.get_vm(vm_name)

    vm.verify_alive()
    vm_session = vm.wait_for_login(
        timeout=int(params.get("login_timeout", 360)))

    logging.info("Try to kill %s", app_name)
    if vm.params.get("os_type") == "linux":
        try:
            output = vm_session.cmd_output("pkill %s" % app_name
                                    .split(os.path.sep)[-1])
        except:
            if output == 1:
                pass
            else:
                raise
    elif vm.params.get("os_type") == "windows":
        vm_session.cmd_output("taskkill /F /IM %s" % app_name
                        .split('\\')[-1])
    vm.verify_alive()
    vm_session.close()


def verify_established(client_vm, host, port, rv_binary,
                       tls_port = None, secure_channels = None):
    """
    Parses netstat output for established connection on host:port
    :param client_vm: vm.wait_for_login()
    :param host: host ip addr
    :param port: port for client to connect
    :param rv_binary:  remote-viewer binary
    :param tls_port: value of the secure port if doing an secure connection
    :param secure_channels: channels to secure if having a secure connection
    """
    rv_binary = rv_binary.split(os.path.sep)[-1]
    print "Verification in progress"

    client_session = client_vm.wait_for_login(timeout=60)
    tls_count = 0

    # !!! -n means do not resolve port names
    if ".exe" in rv_binary:
        cmd = "netstat -n"

    else:
        cmd = '(netstat -pn 2>&1| grep "^tcp.*:.*%s.*ESTABLISHED.*%s.*")' % \
            (host, rv_binary)
    netstat_out = client_session.cmd_output(cmd)
    logging.info("netstat output: %s", netstat_out)

    if tls_port:
        tls_count = netstat_out.count(tls_port)
    else:
        tls_port = port

    if (netstat_out.count(port)+tls_count) < 4:
        logging.error("Not enough channels were open")
        raise RVConnectError()
    if secure_channels:
        if tls_count < len(secure_channels.split(',')):
            logging.error("Not enough secure channels open")
            raise RVConnectError()
    for line in netstat_out.split('\n'):
        if ((port in line and "ESTABLISHED" not in line) or
            (tls_port in line and "ESTABLISHED" not in line)):
            logging.error("Failed to get established connection from netstat")
            raise RVConnectError()
    if "ESTABLISHED" not in netstat_out:
        logging.error("Failed to get established connection from netstat")
        raise RVConnectError()
    logging.info("%s connection to %s:%s successful.",
                     rv_binary, host, port)

    client_session.close()


def start_vdagent(guest_session, os_type, test_timeout):
    """
    Sending commands to start the spice-vdagentd service

    :param guest_session: ssh session of the VM
    :param os_type: os the command is to be run on (windows or linux)
    :param test_timeout: timeout time for the cmds
    """
    if os_type == "linux":
        cmd = "service spice-vdagentd start"
    elif os_type == "windows":
        cmd = 'net start "RHEV Spice Agent"'
    else:
        raise error.TestFail("Error: os_type passed to stop_vdagent is invalid")

    try:
        guest_session.cmd(cmd, print_func=logging.info,
                          timeout=test_timeout)
    except ShellStatusError:
        logging.debug("Status code of \"%s\" was not obtained, most likely"
                      "due to a problem with colored output" % cmd)
    except:
        logging.warn("Starting Vdagent May Not Have Started Properly")
        #raise error.TestFail("Guest Vdagent Daemon Start failed")

    logging.debug("------------ End of guest checking for Spice Vdagent"
                  " Daemon ------------")
    wait_timeout(3)


def restart_vdagent(guest_session, os_type, test_timeout):
    """
    Sending commands to restart the spice-vdagentd service
    :param guest_session: ssh session of the VM
    :param os_type: os the command is to be run on (windows or linux)
    :param test_timeout: timeout time for the cmds

    """
    if os_type == "linux":
        cmd = "service spice-vdagentd restart"
        try:
            guest_session.cmd(cmd, print_func=logging.info,
                              timeout=test_timeout)
        except ShellCmdError:
            raise error.TestFail("Couldn't restart spice vdagent process")
        except:
            raise error.TestFail("Guest Vdagent Daemon Check failed")

        logging.debug("------------ End of Spice Vdagent"
                      " Daemon  Restart ------------")
    elif os_type == "windows":
        try:
            try:
                guest_session.cmd('net stop "RHEV Spice Agent"',
                                  print_func=logging.info, timeout=test_timeout)
            except:
                logging.debug("Failed to stop the service, may have been because" +
                              " it was not running")
            guest_session.cmd('net start "RHEV Spice Agent"',
                              print_func=logging.info, timeout=test_timeout)
        except ShellCmdError:
            raise error.TestFail("Couldn't restart spice vdagent process")
        except:
            raise error.TestFail("Guest Vdagent Daemon Check failed")

        logging.debug("------------ End of Spice Vdagent"
                      " Daemon  Restart ------------")

    wait_timeout(3)


def stop_vdagent(guest_session, os_type, test_timeout):
    """
    Sending commands to stop the spice-vdagentd service

    :param guest_session: ssh session of the VM
    :param os_type: os the command is to be run on (windows or linux)
    :param test_timeout: timeout time for the cmds
    """
    if os_type == "linux":
        cmd = "service spice-vdagentd stop"
    elif os_type == "windows":
        cmd = 'net stop "RHEV Spice Agent"'
    else:
        raise error.TestFail("Error: os_type passed to stop_vdagent is invalid")


    try:
        guest_session.cmd(cmd, print_func=logging.info,
                     timeout=test_timeout)
    except ShellStatusError:
        logging.debug("Status code of \"%s\" was not obtained, most likely"
                      "due to a problem with colored output" % cmd)
    except ShellCmdError:
        raise error.TestFail("Couldn't turn off spice vdagent process")
    except:
        logging.warn("Starting Vdagent May Not Have Stopped Properly")
        #raise error.TestFail("Guest Vdagent Daemon Check failed")

    logging.debug("------------ End of guest checking for Spice Vdagent"
                  " Daemon ------------")

    wait_timeout(3)


def verify_vdagent(guest_session, os_type, test_timeout):
    """
    Verifying vdagent is installed on a VM

    :param guest_session: ssh session of the VM
    :param os_type: os the command is to be run on (windows or linux)
    :param test_timeout: timeout time for the cmds
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
            logging.debug("-----End of guest check to see if vdagent is running"
                          " ----")
        wait_timeout(3)
    else:
        raise error.TestFail("os_type passed to verify_vdagent is invalid")



def get_vdagent_status(vm_session, os_type, test_timeout):
    """
    Return the status of vdagent
    :param vm_session:  ssh session of the VM
    :param os_type: os the command is to be run on (windows or linux)
    :param test_timeout: timeout time for the cmd
    """
    output = ""

    if os_type == "linux":
        cmd = "service spice-vdagentd status"

        wait_timeout(3)
        try:
            output = vm_session.cmd(
                cmd, print_func=logging.info, timeout=test_timeout)
        except ShellCmdError:
            # getting the status of vdagent stopped returns 3, which results in a
            # ShellCmdError
            return("stopped")
        except:
            logging.info("Unexpected error:", sys.exc_info()[0])
            raise error.TestFail(
               "Failed attempting to get status of spice-vdagentd")
        wait_timeout(3)
        return(output)
    elif os_type == "windows":
        cmd = 'net start | FIND "Spice"'
        try:
            output = vm_session.cmd(
                cmd, print_func=logging.info, timeout=test_timeout)
        except ShellCmdError:
            return("stopped")
        except:
            logging.info("Unexpected error:", sys.exc_info()[0])
            raise error.TestFail(
               "Failed attempting to get status of spice-vdagentd")
        wait_timeout(3)
        return("running")



def verify_virtio(guest_session, os_type, test_timeout):
    """
    Verify Virtio linux driver is properly loaded.

    :param guest_session: ssh session of the VM
    :param os_type: os the command is to be run on (windows or linux)
    :param test_timeout: timeout time for the cmds
    """
    if os_type == "linux":
        #cmd = "lsmod | grep virtio_console"
        cmd = "ls /dev/virtio-ports/"
        try:
            guest_session.cmd(cmd, print_func=logging.info,
                              timeout=test_timeout)
        finally:
            logging.debug("------------ End of guest check of the Virtio-Serial"
                          " Driver------------")
        wait_timeout(3)
    elif os_type == "windows":
        cmd = 'C:\\Windows\\winsxs\\amd64_microsoft-windows-pnputil_31bf3856ad364e35_6.1.7600.16385_none_5958b438d6388d15\\PnPutil.exe /e'
        try:
            output = guest_session.cmd(cmd, print_func=logging.info,
                                       timeout=test_timeout)
            if "System devices" in output:
                logging.info("Virtio Serial driver is installed")
        finally:
            logging.debug("----------End of guest check of Virtio-Serial driver"
                          " ------------")
        wait_timeout(3)
    else:
        raise error.TestFail("os_type passed to verify_vdagent is invalid")


def install_rv_win(client, host_path, client_path='C:\\virt-viewer.msi'):
    """
    Install remote-viewer on a windows client

    :param client:      VM object
    :param host_path:   Location of installer on host
    :param client_path: Location of installer after copying
    """
    session = client.wait_for_login(
            timeout=int(client.params.get("login_timeout", 360)))
    client.copy_files_to(host_path, client_path)
    try:
        session.cmd_output('start /wait msiexec /i ' + client_path + ' INSTALLDIR="C:\\virt-viewer"')
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



def clear_interface(vm, login_timeout = 360, timeout = None):
    """
    Clears user interface of a vm without restart

    :param vm:      VM where cleaning is required
    :param login_timeout: timeout time for logging on
    :param timeout: wait time after clearing the interface

    """
    if vm.params.get("os_type") == "windows":
        clear_interface_windows(vm, timeout)
    else:
        clear_interface_linux(vm, login_timeout, timeout)

def clear_interface_linux(vm, login_timeout, timeout = None):
    """
    Clears user interface of a vm without restart

    @param vm:      VM where cleaning is required
    """
    logging.info("restarting X on: %s", vm.name)
    session = vm.wait_for_login(username = "root", password = "123456",
                timeout = login_timeout)

    output = session.cmd('cat /etc/redhat-release')
    isRHEL7 = "release 7." in output

    if isRHEL7:
        command = "gdm"
        pgrep_process = "'^gdm$'"
        if not timeout:
            timeout = 60
    else:
        command = "Xorg"
        pgrep_process = "Xorg"
        if not timeout:
            timeout = 15

    try:
        pid = session.cmd("pgrep %s" % pgrep_process)
        session.cmd("killall %s" % command)
        utils_misc.wait_for(lambda: _is_pid_alive(session, pid), 10, timeout, 0.2)
    except:
        pass

    try:
        session.cmd("ps -C %s" % command)
    except:
        raise error.TestFail("X/gdm not running")
        #logging.info("X or gdm is not running; might cause failures")
    time.sleep(timeout)

def clear_interface_windows(vm, timeout = None):
    session = vm.wait_for_login()
    try:
        session.cmd("taskkill /F /IM remote-viewer.exe")
    except:
        logging.info("Remote-viewer not running")
    if timeout:
        time.sleep(timeout)

def deploy_epel_repo(guest_session, params):
    """
    Deploy epel repository to RHEL VM If It's RHEL6 or 5.

    :param guest_session: - ssh session to guest VM
    :param params: env params
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
    logging.info("Seeting resolution to %s" % res)
    session.cmd("xrandr --output %s --mode %s " %(display, res))

def get_connected_displays(session):
    """ Returns list of video devices on a VM
    :param session: Active connection to the VM
    :return: List of active displays on the VM
    """
    raw = session.cmd_output("xrandr | grep \ connected")
    displays = [a.split()[0] for a in raw.split('n') if a is not '']
    return displays

#TODO: Maybe a dict instead of a list...?
def get_display_resolution(session):
    """ Returns list of resolutions on all displays of a VM
    :param session: Active connection to the VM
    :return: List of resolutions
    """
    raw = session.cmd_output("xrandr | grep \*")
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
        out = subprocess.check_output('xprop -id %s' %window, shell = True)
        for line in out.split('\n'):
            if ( 'NET_WM_WINDOW_TYPE' in line and
                 'ET_WM_WINDOW_TYPE_NORMAL' in line ):
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
            return filter(re.split('[\+\-\W]'))[1]

