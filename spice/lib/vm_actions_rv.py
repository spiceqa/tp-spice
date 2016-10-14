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


"""Connect with remote-viewer from client VM to guest VM.

Client requires
---------------

    - remote-viewer

TODO
----

    - Update properties and add functionality to test others

    Other properties:

    - username
    - version
    - title
    - toggle-fullscreen (key combo)
    - release-cursor (key combo)
    - smartcard-insert
    - smartcard-remove
    - enable-smartcard
    - enable-usbredir
    - color-depth
    - disable-effects
    - usb-filter
    - secure-channels
    - delete-this-file (0,1)

"""

import os
import logging
import socket
import time
import aexpect
import ntpath
from virttest import utils_net
from spice.lib import utils
from spice.lib import act
from spice.lib import reg
from spice.lib import ios

logger = logging.getLogger(__name__)

WINDOW_TITLE = "'vm1 (1) - Remote Viewer'"

RV_WIN_NAME_AUTH = "Authentication required"
"""Expected window caption."""
RV_WIN_NAME = "Remote Viewer"
"""Expected window caption."""
RV_WM_CLASS = "remote-viewer"


class RVSessionError(Exception):
    """Exception for remote-viewer session. Root exception for the RV Sessiov.
    """
    def __init__(self, test, *args, **kwargs):
        super(RVSessionError, self).__init__(args, kwargs)
        if test.cfg.pause_on_fail or test.cfg.pause_on_end:
            # 1 hour
            seconds = 60 * 60 * 10
            logger.error("Test %s has failed. Do nothing for %s seconds.",
                         test.cfg.id, seconds)
            time.sleep(seconds)


class RVSessionNotImplemented(RVSessionError):
    """Used to show that this part of code is not implemented.
    """


class RVSessionConnect(RVSessionError):
    """Exception for remote-viewer session.
    """

@reg.add_action(req=[ios.ILinux])
def cp_rv_file(vmi, test):
    if cfg.rv_parameters_from != "file":
        return
    host_dir = os.path.expanduser('~')
    host_vv_file = os.path.join(host_dir, cfg.rv_file)
    utils.generate_vv_file(host_vv_file, test)
    client_dir = act.dst_dir(vmi)
    client_vv_file = os.path.join(client_dir, cfg.rv_file)
    act.info(vmi_c, "Copy from host: %s to %s", host_vv_file,
                client_vv_file)
    test.vm_c.copy_files_to(host_vv_file, client_vv_file)


@reg.add_action(req=[ios.ILinux])
def rv_url(vmi, test):
    host_ip = utils.get_host_ip(test)
    # Cacert subj is in format for create certificate(with '/'
    # delimiter) remote-viewer needs ',' delimiter. And also is needed
    # to remove first character (it's '/')
    host_subj = utils.get_host_subj(test)
    port = kvm_g.spice_port
    tls_port = kvm_g.spice_tls_port
    # If it's invalid implicit, a remote-viewer connection will be
    # attempted with the hostname, since ssl certs were generated with
    # the ip address.
    escape_char = test.cfg_c.shell_escape_char or '\\'
    if cfg.ssltype == "invalid_implicit_hs" or \
            "explicit" in cfg.ssltype:
        hostname = socket.gethostname()
        url = "spice://%s?tls-port=%s%s&port=%s" % (
            hostname, tls_port, escape_char, port)
    else:
        url = "spice://%s?tls-port=%s%s&port=%s" % (
            host_ip, tls_port, escape_char, port)
    if cfg.rv_parameters_from == "cmd":
        rv_cmd.append(url)
    # not ssl
    port = kvm_g.spice_port
    if cfg.rv_parameters_from == "menu":
        # Line to be sent through monitor once r-v is started without
        # spice url.
        url = "spice://%s?port=%s" % (host_ip, port)
    else:
        opt = "spice://%s?port=%s" % (host_ip, port)
        rv_cmd.append(opt)


@reg.add_action(req=[ios.ILinux])
def cacert_path(vmi, test):
    # CA cert file on the host.
    fpath = utils.cacert_path_host(test)
    fname = ntpath.basename(fpath)
    wdir = act.workdir(vmi)
    fpath_c = os.path.join(wdir, fname)
    return fpath_c


@reg.add_action(req=[ios.ILinux])
def cp_cacert(vmi, test):
    """Copy cacert file to client.

    """
    # Remove previous CA cert on the client.
    fpath = utils.cacert_path_host(test)
    fpath_c = act.cacert_path(vmi, test)
    cmd = utils.Cmd("rm", "-f", fpath_c)
    act.run(vmi_c, cmd)
    cmd = utils.Cmd("mkdir", "-p", wdir)
    act.run(vmi_c, cmd)
    vm_c.copy_files_to(fpath, fpath_c)
    return fpath_c


@reg.add_action(req=[ios.ILinux])
def rv_opts(vmi, test):
    """Command line parameters for RV.

    """
    rv_cmd = utils.Cmd()
    rv_cmd.append(cfg.rv_binary)
    if cfg.rv_debug:
        rv_cmd.append("--spice-debug")
    if cfg.full_screen:
        rv_cmd.append("--full-screen")
    if cfg.disable_audio:
        rv_cmd.append("--spice-disable-audio")
    if cfg.smartcard:
        rv_cmd.append("--spice-smartcard")
        if cfg.certdb:
            rv_cmd.append("--spice-smartcard-db")
            rv_cmd.append(cfg.certdb)
        if cfg.gencerts:
            rv_cmd.append("--spice-smartcard-certificates")
            rv_cmd.append(cfg.gencerts)
    if cfg.usb_redirection_add_device:
        logger.info("Auto USB redirect for devices class == 0x08.")
        opt = r'--spice-usbredir-redirect-on-connect="0x08,-1,-1,-1,1"'
        rv_cmd.append(opt)
    if utils.is_yes(test.kvm_g.spice_ssl):
        fpath = act.cacert_path(vmi, test)
        opt = "--spice-ca-file=%s" % fpath
        rv_cmd.append(opt)
        if cfg.spice_client_host_subject:
            opt = '--spice-host-subject=%s' % host_subj
            rv_cmd.append(opt)
    return rv_cmd

utils.info(vmi_c, "Final cmd for client is: %s", str(rv_cmd))

@reg.add_action(req=[ios.ILinux])
def rv_run(vmi, cmd, env={}):
    if cfg.rv_ld_library_path:
        cmd = utils.Cmd("export")
        cmd.append("LD_LIBRARY_PATH=%s" % cfg.rv_ld_library_path)
        act.run(vmi_c, cmd, ssn=ssn)
    if cfg.spice_proxy and cfg.rv_parameters_from != "file":
        cmd = utils.Cmd("export")
        cmd.append("SPICE_PROXY=%s" % cfg.spice_proxy)
        act.run(vmi_c, cmd, ssn=ssn)
    for key in env:
        cmd = utils.Cmd("export", "%s=%s" % (key, env[key]))
        act.run(vmi_c, cmd, ssn=ssn)
    if cfg.usb_redirection_add_device:
        # USB was created by qemu (root). This prevents right issue.
        # ..todo:: must be root session
        cmd = utils.Cmd("chown", cfg.username, cfg.file_path)
        act.run(vmi_c, cmd, ssn=ssn)
        if not act.check_usb_policy(test.vmi_c):
            act.add_usb_policy(test.vmi_c)
    try:
        pid = ssn.get_pid()
        logger.info("shell pid id: %s", pid)
        ssn.sendline(str(rv_cmd))
    except aexpect.ShellStatusError:
        logger.debug("Ignoring a status exception, will check connection"
                      "of remote-viewer later")


@reg.add_action(req=[ios.ILinux])
def rv_auth(vmi, cmd, env={}):
    """Client waits for user authentication if spice_password is set use qemu
    monitor password if set, else, if set, try normal password.

    Only for cmdline. File console.rv should have a password.

    """
    if cfg.ticket_send:
        # Wait for remote-viewer to launch.
        act.wait_for_win(vmi_c, RV_WIN_NAME_AUTH)
        act.str_input(vmi_c, cfg.ticket_send)

is_connected(test)

@reg.add_action(req=[ios.IWindows])
def rv_run(vmi, cmd, env={}):
    if cfg.spice_proxy and cfg.rv_parameters_from != "file":
        cmd = utils.Cmd("SET SPICE_PROXY=%s", cfg.spice_proxy)
        act.run(vmi_c, cmd, ssn=ssn)
    for key in env:
        cmd = utils.Cmd("SET %s=%s" % (key, env[key]))
        act.run(vmi_c, cmd, ssn=ssn)
    if utils.is_yes(test.kvm_g.spice_ssl):
    if cfg.usb_redirection_add_device:
        if not act.check_usb_policy(test.vmi_c):
            act.add_usb_policy(test.vmi_c)
    try:
        pid = ssn.get_pid()
        logger.info("shell pid id: %s", pid)
        ssn.sendline(str(rv_cmd))
    except aexpect.ShellStatusError:
        logger.debug("Ignoring a status exception, will check connection"
                      "of remote-viewer later")
    # Send command line through monitor since url was not provided
    if cfg.rv_parameters_from == "menu":
        act.str_input(test.vmi_c, url)
    # At this step remote-viewer application window must exist.  It can be any
    # remote-viewer window: main, pop-up, menu, etc.
    try:
        act.wait_for_win(vmi_c, RV_WM_CLASS, "WM_CLASS")
    except utils.SpiceUtilsError:
        raise RVSessionError(test)

def connect(test, ssn, env={}):
    """Establish connection between client and guest based on test
    parameters supplied at cartesian config.

    Notes
    -----
    There are three possible methods to connect from client to guest:

        * From cmdline + parameters
        * From cmdline + rv file
        * remote-viewer menu URL

    Parameters
    ----------
    test : SpiceTest
        Spice test object.
    ssn : xxx
        Session object, as a exec-layer to VM.
    env : dict
        Dictionary of env variables to passed before remote-viewer start.

    Returns
    -------
    None

    """
    cmd = act.rv_opts(vmi)
    if cfg.rv_parameters_from in ['cmd', 'menu']:
        url = act.rv_url(vmi, test)
    if cfg.rv_parameters_from == 'cmd':
        cmd.extend(url)
    if utils.is_yes(test.kvm_g.spice_ssl):
        act.cp_cacert(vmi)
    if cfg.rv_parameters_from == 'file':
        fpath = cp_rv_file(vmi, test)
        cmd.append(fpath)
    utils.set_ticket(test)
    act.rv_run(vmi, cmd)
    if cfg.rv_parameters_from in ['cmd', 'menu']:
        act.rv_auth(vmi)
    act.chk_rvcon(vmi)


def chk_rvcon(test):
    """Tests if connection is active.

    .. todo:: rewrte to test per session.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    Raises
    ------
    RVSessionConnect
        RV session is not establised. Or established in unexpected way.
    RVSessionError
        Something goes wrong.
    """
    cfg = test.cfg
    remote_ip = utils.get_host_ip(test)
    proxy_port = ""
    if cfg.spice_proxy:
        # ..todo:: add spice_proxy_port
        proxy_port = "3128"
        if "http" in cfg.spice_proxy:
            split = cfg.spice_proxy.split('//')[1].split(':')
        else:
            split = cfg.spice_proxy.split(':')
        remote_ip = split[0]
        if len(split) > 1:
            proxy_port = split[1]
        logger.info("Proxy port to inspect: %s", proxy_port)
    rv_binary = test.vm_c.params.get("rv_binary")
    rv_binary = os.path.basename(rv_binary)
    if test.vm_c.is_linux():
        cmd = '(netstat -pn 2>&1| grep "^tcp.*:.*%s.*ESTABLISHED.*%s.*")' % \
            (remote_ip, rv_binary)
    elif test.vm_c.is_win():
        # .. todo: finish it
        cmd = "netstat -n"
    try:
        # Wait all RV Spice links raise up.
        time.sleep(5)
        netstat_out = act.run(test.vmi_c, cmd)
    except aexpect.ShellCmdError as info:
        raise RVSessionError(test, info)
    proxy_port_count = 0
    if cfg.spice_proxy:
        proxy_port_count = netstat_out.count(proxy_port)
    test.vm_g.info("Active proxy ports %s: %s", proxy_port, proxy_port_count)
    port = test.kvm_g.spice_port
    tls_port = test.kvm_g.spice_tls_port
    port_count = netstat_out.count(port)
    test.vm_g.info("Active ports %s: %s", port, port_count)
    tls_port_count = 0
    if tls_port:
        tls_port_count = netstat_out.count(tls_port)
    test.vm_g.info("Active TLS ports %s: %s", tls_port, tls_port_count)
    opened_ports = port_count + tls_port_count + proxy_port_count
    if opened_ports < 4:
        raise RVSessionConnect(test,
                               "Total links per session is less then 4 (%s)." %
                               opened_ports)
    if cfg.spice_secure_channels:
        tls_port_expected = len(cfg.spice_secure_channels.split(','))
        if tls_port_count < tls_port_expected:
            msg = "Secure links per session is less then expected. %s (%s)" % (
                tls_port_count, tls_port_expected)
            raise RVSessionConnect(test, msg)
    for line in netstat_out.split('\n'):
        for p in port, tls_port, proxy_port:
            if p and p in line and "ESTABLISHED" not in line:
                raise RVSessionConnect(test, "Missing active link at port %s",
                                       p)
    output = test.vm_g.monitor.cmd("info spice")
    logger.info(output)
    # Check to see if ipv6 address is reported back from qemu monitor
    if cfg.spice_info == "ipv6":
        # Remove brackets from ipv6 host ip
        host_ip = utils.get_host_ip(test)
        if host_ip[1:len(host_ip) - 1] in output:
            logger.info(
                "Reported ipv6 address found in output from 'info spice'")
        else:
            raise RVSessionConnect("ipv6 address not found from qemu monitor"
                                   " command: 'info spice'")
    logger.debug("Connection checking pass")


def disconnect(test):
    """Terminates connection by killing remote-viewer.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    :return: None
    """
    act.kill_by_name(test.vmi_c, test.cfg.rv_binary)
