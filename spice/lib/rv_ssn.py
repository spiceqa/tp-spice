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
from virttest import utils_misc
from spice.lib import utils

RV_WIN_NAME_AUTH = "Authentication required"
"""Expected window caption."""
RV_WIN_NAME = "Remote Viewer"
"""Expected window caption."""
RV_WM_CLASS = "remote-viewer"


class RVSessionError(Exception):
    """Exception for remote-viewer session. Root exception for the RV Sessiov.
    """


class RVSessionNotImplemented(RVSessionError):
    """Used to show that this part of code is not implemented.
    """


class RVSessionConnect(RVSessionError):
    """Exception for remote-viewer session.
    """


def get_host_ip(test):
    """Get IP for host.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    """
    ip = utils_net.get_host_ip_address(test.cfg)
    if test.kvm_g.listening_addr == "ipv6":
        ip = "[" + utils_misc.convert_ipv4_to_ipv6(ip) + "]"
    return ip


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
            subj += get_host_ip(test)
    return subj


def connect(test, env={}):
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
    env : dict
        Dictionary of env variables to passed before remote-viewer start.

    Returns
    -------
    None

    """
    cfg = test.cfg
    ssn_c = test.ssn_c
    vm_c = test.vm_c
    vm_g = test.vm_g
    kvm_g = test.kvm_g
    # Check correct invocation.
    if cfg.display == "vnc":
        raise RVSessionError("remote-viewer vnc not implemeted")
    elif cfg.display != "spice":
        raise RVSessionError("Unsupported display value")
    # Print remove-viewer version on client
    if vm_c.is_linux():
        ssn_c.cmd("export DISPLAY=:0.0")
        if cfg.rv_ld_library_path:
            cmd = "export LD_LIBRARY_PATH=%s" % cfg.rv_ld_library_path
            ssn_c.cmd(cmd)
    if cfg.spice_proxy and cfg.rv_parameters_from != "file":
        if vm_c.is_linux():
            ssn_c.cmd("export SPICE_PROXY=%s" % cfg.spice_proxy)
        elif vm_c.is_win():
            ssn_c.cmd_output("SET SPICE_PROXY=%s" % cfg.spice_proxy)
    for key in env:
        if vm_c.is_linux():
            ssn_c.cmd("export %s=%s" % (key, env[key]))
        elif vm_c.is_win():
            ssn_c.cmd_output("SET %s=%s" % (key, env[key]))
    utils.print_rv_version(test, test.name_c)
    # Set the password of the VM using the qemu-monitor.
    if cfg.qemu_password:
        logging.info("Guest qemu monitor: set_password spice %s",
                     cfg.qemu_password)
        cmd = "set_password spice %s" % cfg.qemu_password
        vm_g.monitor.cmd(cmd)
    # Command line parameters for RV
    cmd = ""
    # URL for RV
    url = ""
    # Make cmd for client.
    cmd += cfg.rv_binary
    if vm_c.is_linux():
        cmd = cmd + " --display=:0.0"
    if cfg.rv_parameters_from == 'file':
        cmd += " " + cfg.rv_file
    host_ip = get_host_ip(test)
    if utils.is_yes(kvm_g.spice_ssl):
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
            xcmd = "rm -rf %s" % cfg.spice_x509_prefix
            ssn_c.cmd(xcmd)
            xcmd = "mkdir -p %s" % cfg.spice_x509_prefix
            ssn_c.cmd(xcmd)
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
        escape_char = vm_c.params.get("shell_escape_char", '\\')
        if cfg.ssltype == "invalid_implicit_hs" or \
                "explicit" in cfg.ssltype:
            hostname = socket.gethostname()
            url = " spice://%s?tls-port=%s%s&port=%s" % (
                hostname, tls_port, escape_char, port)
        else:
            url = " spice://%s?tls-port=%s%s&port=%s" % (
                host_ip, tls_port, escape_char, port)
        if cfg.rv_parameters_from == "cmd":
            cmd += url
        elif cfg.rv_parameters_from == "menu":
            pass
        elif cfg.rv_parameters_from == "file":
            pass
        if cfg.rv_parameters_from != "file":
            cmd += " --spice-ca-file=%s" % cacert_client
        if utils.is_yes(cfg.spice_client_host_subject) and \
                cfg.rv_parameters_from != "file":
            cmd += ' --spice-host-subject="%s"' % host_subj
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
            cmd += " spice://%s?port=%s" % (host_ip, port)
    # Usbredirection support.
    if utils.is_yes(cfg.usb_redirection_add_device):
        logging.info("USB redirection set auto redirect on connect for device"
                     "class 0x08")
        cmd += ' --spice-usbredir-redirect-on-connect="0x08,-1,-1,-1,1"'
        # USB was created by qemu (root). This prevents right issue.
        # ..todo:: must be root session
        if vm_c.is_linux():
            ccmd = "chown {0}:{0} {1}".format(cfg.username, cfg.file_path)
            ssn_c.cmd(ccmd)
        if not utils.check_usb_policy(test, test.name_c):
            utils.add_usb_policy(test, test.name_c)
    if cfg.rv_parameters_from == "cmd":
        if utils.is_yes(cfg.full_screen):
            cmd += " --full-screen"
        if utils.is_yes(cfg.disable_audio):
            cmd += " --spice-disable-audio"
        if utils.is_yes(cfg.smartcard):
            cmd += " --spice-smartcard"
            if cfg.certdb:
                cmd += " --spice-smartcard-db " + cfg.certdb
            if cfg.gencerts:
                cmd += " --spice-smartcard-certificates " + cfg.gencerts
    if test.vm_c.is_linux():
        cmd = "nohup " + cmd + " &> ~/rv.log &"  # Launch it on background
    if cfg.rv_parameters_from == "file":
        generate_vv_file(test)
        test.vm_c.copy_files_to(cfg.rv_file, cfg.rv_file)
    logging.info("Final cmd for client is: %s", cmd)
    try:
        test.ssn_c.cmd(cmd)
    except aexpect.ShellStatusError:
        logging.debug("Ignoring a status exception, will check connection"
                      "of remote-viewer later")
    # Send command line through monitor since url was not provided
    if cfg.rv_parameters_from == "menu":
        utils.str_input(test, test.name_c, url)
    # client waits for user entry (authentication) if spice_password is set
    # use qemu monitor password if set, else, if set, try normal password.
    ticket = kvm_g.spice_password
    # At this step remote-viewer application window must exist.  It can be any
    # remote-viewer window: main, pop-up, menu, etc.
    try:
        utils.wait_for_win(test, test.name_c, RV_WM_CLASS, "WM_CLASS")
    except utils.SpiceUtilsError:
        raise RVSessionError
    if cfg.qemu_password:
        # Wait for remote-viewer to launch
        utils.wait_for_win(test, test.name_c, RV_WIN_NAME_AUTH)
        utils.str_input(test, test.name_c, cfg.qemu_password)
    elif ticket:
        if cfg.spice_password_send:
            ticket = cfg.spice_password_send
        try:
            utils.wait_for_win(test, test.name_c, RV_WIN_NAME_AUTH)
            utils.str_input(test, test.name_c, ticket)
        except utils.SpiceUtilsError:
            raise RVSessionConnect
    is_connected(test)

#    # @TODO: This probably needs moving back to rv_connect or to a new file
#    # tbh, not sure why it's here -.-
#        # Get spice info
#        output = vm_g.monitor.cmd("info spice")
#        logging.debug("INFO SPICE")
#        logging.debug(output)
#
#        # Check to see if ipv6 address is reported back from qemu monitor
#        check_spice_info = cfg.spice_info
#        if (check_spice_info == "ipv6"):
#            logging.info("Test to check if ipv6 address is reported"
#                    " back from the qemu monitor")
#            # Remove brackets from ipv6 host ip
#            if (host_ip[1:len(host_ip) - 1] in output):
#            logging.info("Reported ipv6 address found in output from"
#                        " 'info spice'")
#            else:
#            raise error.TestFail("ipv6 address not found from qemu monitor"
#                                " command: 'info spice'")
#        else:
#            logging.info("Not checking the value of 'info spice'"
#                        " from the qemu monitor")


def is_connected(test):
    """Tests whether or not is connection active.

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
    remote_ip = get_host_ip(test)
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
    if test.vm_c.is_linux():
        rv_binary = os.path.basename(cfg.rv_binary)
        cmd = '(netstat -pn 2>&1| grep "^tcp.*:.*%s.*ESTABLISHED.*%s.*")' % \
            (remote_ip, rv_binary)
    elif test.vm_c.is_win():
        # ..todo: finish it
        cmd = "netstat -n"
    try:
        # Wait all RV Spice links raise UP.
        time.sleep(5)
        netstat_out = test.ssn_c.cmd_output(cmd)
    except aexpect.ShellCmdError, info:
        raise RVSessionError(info)
    proxy_port_count = 0
    if cfg.spice_proxy:
        proxy_port_count = netstat_out.count(proxy_port)
    port = test.kvm_g.spice_port
    tls_port = test.kvm_g.spice_tls_port
    port_count = netstat_out.count(port)
    tls_port_count = 0
    if tls_port:
        tls_port_count = netstat_out.count(tls_port)
    opened_ports = port_count + tls_port_count + proxy_port_count
    if opened_ports < 4:
        raise RVSessionConnect("Total links per session is less then 4 (%s)." %
                               opened_ports)
    if cfg.spice_secure_channels:
        tls_port_expected = len(cfg.spice_secure_channels.split(','))
        if tls_port_count < tls_port_expected:
            msg = "Secure links per session is less then expected. %s (%s)" % (
                tls_port_count, tls_port_expected)
            raise RVSessionConnect(msg)
    for line in netstat_out.split('\n'):
        for p in port, tls_port, proxy_port:
            if p and p in line and "ESTABLISHED" not in line:
                raise RVSessionConnect("Missing active link at port %s", p)
    logging.debug("Connection checking pass")


def disconnect(test):
    """Terminates connection by killing remote-viewer.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    :return: None
    """
    utils.kill_by_name(test, test.name_c, test.cfg.rv_binary)


def generate_vv_file(test):
    """Generates vv file for remote-viewer.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    """
    cfg = test.cfg
    rv_file = open(cfg.rv_file, 'w')
    rv_file.write("[virt-viewer]\n")
    rv_file.write("type=%s\n" % cfg.display)
    rv_file.write("host=%s\n" % utils_net.get_host_ip_address(cfg))
    rv_file.write("port=%s\n" % test.kvm_g.spice_port)
    ticket = cfg.spice_password
    if cfg.spice_password_send:
        ticket = cfg.spice_password_send
    if cfg.qemu_password:
        ticket = cfg.qemu_password
    if ticket:
        rv_file.write("password=%s\n" % ticket)
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
    if utils.is_yes(cfg.full_screen):
        rv_file.write("fullscreen=1\n")
    if cfg.spice_proxy:
        rv_file.write("proxy=%s\n" % cfg.spice_proxy)
