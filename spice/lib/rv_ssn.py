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
from virttest import utils_net
from spice.lib import utils
from spice.lib import act

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


def get_cacert_path_host(test):
    """cacert file path on host system.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    """
    path = None
    if utils.is_yes(test.kvm_g.spice_ssl):
        path = "%s/%s" % (test.cfg.spice_x509_prefix,
                          test.cfg.spice_x509_cacert_file)
    logger.info("CA cert file on host: %s", path)
    return path


def get_host_subj(test):
    """Host subject.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    """
    subj = None
    if utils.is_yes(test.kvm_g.spice_ssl):
        if test.cfg.ssltype == "invalid_explicit_hs":
            subj = "Invalid Explicit HS"
        else:
            # Has form: /C=CZ/L=BRNO/O=SPICE/CN=.
            subj = test.kvm_g.spice_x509_server_subj
            subj = subj.replace('/', ',')[1:]
            subj += utils.get_host_ip(test)
    return subj


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
    cfg = test.cfg
    vm_c = test.vm_c
    vm_g = test.vm_g
    kvm_g = test.kvm_g
    vmi_c = test.vmi_c
    # Check correct invocation.
    if test.cfg_g.display == "vnc":
        raise RVSessionError(test, "remote-viewer vnc not implemeted")
    elif test.cfg_g.display != "spice":
        raise RVSessionError(test, "Unsupported display value")
    # Print remove-viewer version on client
    if vm_c.is_linux():
        if cfg.rv_ld_library_path:
            cmd = utils.Cmd("export")
            cmd.append("LD_LIBRARY_PATH=%s" % cfg.rv_ld_library_path)
            act.run(vmi_c, cmd, ssn=ssn)
    if cfg.spice_proxy and cfg.rv_parameters_from != "file":
        if vm_c.is_linux():
            cmd = utils.Cmd("export", "SPICE_PROXY=%s" % cfg.spice_proxy)
            act.run(vmi_c, cmd, ssn=ssn)
        elif vm_c.is_win():
            cmd = utils.Cmd("SET SPICE_PROXY=%s", cfg.spice_proxy)
            act.run(vmi_c, cmd, ssn=ssn)
    for key in env:
        if vm_c.is_linux():
            cmd = utils.Cmd("export", "%s=%s" % (key, env[key]))
            act.run(vmi_c, cmd, ssn=ssn)
        elif vm_c.is_win():
            cmd = utils.Cmd("SET %s=%s" % (key, env[key]))
            act.run(vmi_c, cmd, ssn=ssn)
    act.print_rv_version(test.vmi_c)
    # Set the password of the VM using the qemu-monitor.
    if cfg.ticket_set:
        logging.info("Guest qemu monitor: set_password spice %s",
                     cfg.ticket_set)
        cmd = "set_password spice %s" % cfg.ticket_set
        vm_g.monitor.cmd(cmd)
    # Command line parameters for RV
    rv_cmd = utils.Cmd()
    # URL for RV
    url = ""
    # Make cmd for client.
    rv_cmd.append(cfg.rv_binary)
    if vm_c.is_linux():
        rv_cmd.append("--display=:0.0")
    if cfg.rv_parameters_from == 'file':
        cmd1 = utils.Cmd("getent", "passwd", cfg.username)
        cmd2 = utils.Cmd("cut", "-d:", "-f6")
        cmd = utils.combine(cmd1, "|", cmd2)
        out = act.run(vmi_c, cmd)
        client_dir = out.rstrip('\r\n')
        client_vv_file = os.path.join(client_dir, cfg.rv_file)
        rv_cmd.append(client_vv_file)
    host_ip = utils.get_host_ip(test)
    if utils.is_yes(test.kvm_g.spice_ssl):
        # Copy cacert file to client.
        # cacert file on the host
        cacert_host = get_cacert_path_host(test)
        # cacert file on the client
        if vm_c.is_linux():
            cacert_client = cacert_host
        elif vm_c.is_win():
            cacert_client = r"C:\%s" % cfg.spice_x509_cacert_file
        # Remove previous cacert on the client
        if vm_c.is_linux():
            cmd = utils.Cmd("rm", "-rf", cfg.spice_x509_prefix)
            act.run(vmi_c, cmd, ssn=ssn)
            cmd = utils.Cmd("mkdir", "-p", cfg.spice_x509_prefix)
            act.run(vmi_c, cmd, ssn=ssn)
        vm_c.copy_files_to(cacert_host, cacert_client)
        # Cacert subj is in format for create certificate(with '/'
        # delimiter) remote-viewer needs ',' delimiter. And also is needed
        # to remove first character (it's '/')
        host_subj = get_host_subj(test)
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
        elif cfg.rv_parameters_from == "menu":
            pass
        elif cfg.rv_parameters_from == "file":
            pass
        if cfg.rv_parameters_from != "file":
            opt = "--spice-ca-file=%s" % cacert_client
            rv_cmd.append(opt)
        if cfg.spice_client_host_subject and \
                cfg.rv_parameters_from != "file":
            opt = '--spice-host-subject="%s"' % host_subj
            rv_cmd.append(opt)
    else:
        # Not spice_ssl.
        port = kvm_g.spice_port
        if cfg.rv_parameters_from == "menu":
            # Line to be sent through monitor once r-v is started without
            # spice url.
            url = "spice://%s?port=%s" % (host_ip, port)
        elif cfg.rv_parameters_from == "file":
            pass
        else:
            opt = "spice://%s?port=%s" % (host_ip, port)
            rv_cmd.append(opt)
    # Usbredirection support.
    if cfg.usb_redirection_add_device:
        logging.info("USB redirection set auto redirect on connect for device"
                     "class 0x08")
        opt = r'--spice-usbredir-redirect-on-connect="0x08,-1,-1,-1,1"'
        rv_cmd.append(opt)
        # USB was created by qemu (root). This prevents right issue.
        # ..todo:: must be root session
        if vm_c.is_linux():
            cmd = utils.Cmd("chown", cfg.username, cfg.file_path)
            act.run(vmi_c, cmd, ssn=ssn)
        if not act.check_usb_policy(test.vmi_c):
            act.add_usb_policy(test.vmi_c)
    if cfg.rv_debug:
        rv_cmd.append("--spice-debug")
    if cfg.rv_parameters_from == "cmd":
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
    if cfg.rv_parameters_from == "file":
        host_dir = os.path.expanduser('~')
        host_vv_file = os.path.join(host_dir, cfg.rv_file)
        generate_vv_file(host_vv_file, test)
        act.info(vmi_c, "Copy from host: %s to %s", host_vv_file,
                 client_vv_file)
        test.vm_c.copy_files_to(host_vv_file, client_vv_file)
    logging.info(vmi_c, "Final cmd for client is: %s", rv_cmd)
    try:
        pid = ssn.get_pid()
        logger.info("shell pid id: %s", pid)
        ssn.sendline(rv_cmd)
    except aexpect.ShellStatusError:
        logging.debug("Ignoring a status exception, will check connection"
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
    # client waits for user entry (authentication) if spice_password is set
    # use qemu monitor password if set, else, if set, try normal password.
    if cfg.ticket_send and cfg.rv_parameters_from != "file":
        # In case of .vv file, password supplied inside .vv file.
        # Wait for remote-viewer to launch
        try:
            act.wait_for_win(vmi_c, RV_WIN_NAME_AUTH)
            act.str_input(vmi_c, cfg.ticket_send)
        except utils.SpiceUtilsError:
            raise RVSessionConnect(test)
    is_connected(test)


def is_connected(test):
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
        logging.info("Proxy port to inspect: %s", proxy_port)
    rv_binary = test.vm_c.params.get("rv_binary")
    rv_binary = os.path.basename(rv_binary)
    if test.vm_c.is_linux():
        cmd = '(netstat -pn 2>&1| grep "^tcp.*:.*%s.*ESTABLISHED.*%s.*")' % \
            (remote_ip, rv_binary)
    elif test.vm_c.is_win():
        # .. todo: finish it
        cmd = "netstat -n"
    try:
        # Wait all RV Spice links raise UP.
        time.sleep(5)
        netstat_out = test.ssn_c.cmd_output(cmd)
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
            logging.info(
                "Reported ipv6 address found in output from 'info spice'")
        else:
            raise RVSessionConnect("ipv6 address not found from qemu monitor"
                                   " command: 'info spice'")
    logging.debug("Connection checking pass")


def disconnect(test):
    """Terminates connection by killing remote-viewer.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    :return: None
    """
    act.kill_by_name(test.vmi_c, test.cfg.rv_binary)


def generate_vv_file(path, test):
    """Generates vv file for remote-viewer.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    """
    cfg = test.cfg
    rv_file = open(path, 'w')
    rv_file.write("[virt-viewer]\n")
    rv_file.write("type=%s\n" % cfg.display)
    rv_file.write("host=%s\n" % utils_net.get_host_ip_address(cfg))
    rv_file.write("port=%s\n" % test.kvm_g.spice_port)
    if cfg.ticket_send:
        rv_file.write("password=%s\n" % cfg.ticket_send)
    if utils.is_yes(test.kvm_g.spice_ssl):
        rv_file.write("tls-port=%s\n" % test.kvm_g.spice_tls_port)
        rv_file.write("tls-ciphers=DEFAULT\n")
    host_subj = get_host_subj(test)
    if host_subj:
        rv_file.write("host-subject=%s\n" % host_subj)
    cacert_host = get_cacert_path_host(test)
    if cacert_host:
        cert = open(cacert_host)
        cert_auth = cert.read()
        cert_auth = cert_auth.replace('\n', r'\n')
        rv_file.write("ca=%s\n" % cert_auth)
    if cfg.full_screen:
        rv_file.write("fullscreen=1\n")
    if cfg.spice_proxy:
        rv_file.write("proxy=%s\n" % cfg.spice_proxy)
