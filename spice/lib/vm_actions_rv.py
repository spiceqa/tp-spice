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


@reg.add_action(req=[ios.IOSystem])
def rv_connect(vmi, ssn, env={}):
    """Establish connection between client and guest based on test parameters
    supplied at cartesian config.

    Notes
    -----
    There are three possible methods to connect from client to guest:

        * Cmdline + parameters
        * Cmdline + rv file
        * remote-viewer menu URL

    Parameters
    ----------
    test : VmInfo
        VM that runs RV.
    ssn : xxx
        Session object, as a exec-layer to VM.
    env : dict
        Dictionary of env variables to passed before remote-viewer start.

    Returns
    -------
    None

    """
    method = vmi.cfg.rv_parameters_from
    if method == 'cmd':
        act.info(vmi, "Connect to VM using command line.")
        rv_connect_cmd(vmi, ssn, env)
    elif method == 'menu':
        act.info(vmi, "Connect to VM using menu.")
        rv_connect_menu(vmi, ssn, env)
    elif method == 'file':
        act.info(vmi, "Connect to VM using .vv file.")
        rv_connect_file(vmi, ssn, env)
    else:
        raise RVSessionConnect(vmi.test, "Wrong connect method.")


@reg.add_action(req=[ios.ILinux])
def rv_connect_cmd(vmi, ssn, env):
    cmd = act.rv_basic_opts(vmi)
    url = act.rv_url(vmi)
    cmd.append(url)
    cmd = utils.combine(cmd, "2>&1")
    act.info(vmi, "Final RV command: %s", cmd)
    utils.set_ticket(vmi.test)
    act.rv_run(vmi, cmd, ssn)
    act.rv_auth(vmi)


@reg.add_action(req=[ios.ILinux])
def rv_connect_menu(vmi, ssn, env):
    cmd = act.rv_basic_opts(vmi)
    utils.set_ticket(vmi.test)
    cmd = utils.combine(cmd, "2>&1")
    act.info(vmi, "Final RV command: %s", cmd)
    act.rv_run(vmi, cmd, ssn)
    url = act.rv_url(vmi)
    act.str_input(vmi, url)
    act.rv_auth(vmi)


@reg.add_action(req=[ios.ILinux])
def rv_connect_file(vmi, ssn, env):
    cmd = utils.Cmd(vmi.cfg.rv_binary)
    vv_file_host = act.gen_vv_file(vmi)
    with open(vv_file_host, 'r') as rvfile:
        file_contents = rvfile.read()
        act.info(vmi, "RV file contents:\n%s", file_contents)
    vv_file_client = act.cp_file(vmi, vv_file_host)
    cmd.append(vv_file_client)
    utils.set_ticket(vmi.test)
    cmd = utils.combine(cmd, "2>&1")
    act.info(vmi, "Final RV command: %s", cmd)
    act.rv_run(vmi, cmd, ssn)


@reg.add_action(req=[ios.ILinux])
def rv_basic_opts(vmi):
    """Command line parameters for RV.

    """
    cfg = vmi.cfg
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
    if utils.is_yes(vmi.test.kvm_g.spice_ssl):
        cacert_host = utils.cacert_path_host(vmi.test)
        cacert_client = act.cp_file(vmi, cacert_host)
        opt = "--spice-ca-file=%s" % cacert_client
        rv_cmd.append(opt)
        if cfg.spice_client_host_subject:
            host_subj = utils.get_host_subj(vmi.test)
            opt = '--spice-host-subject=%s' % host_subj
            rv_cmd.append(opt)
    return rv_cmd


@reg.add_action(req=[ios.ILinux])
def rv_url(vmi):
    """Cacert subj is in format for create certificate(with '/' delimiter)
    remote-viewer needs ',' delimiter. And also is needed to remove first
    character (it's '/').

    If it's invalid implicit, a remote-viewer connection will be attempted
    with the hostname, since ssl certs were generated with the ip address.

    """
    test = vmi.test
    port = test.kvm_g.spice_port
    tls_port = test.kvm_g.spice_tls_port
    #escape_char = test.cfg_c.shell_escape_char or '\\'
    host_ip = utils.get_host_ip(test)
    # SSL
    if utils.is_yes(vmi.test.kvm_g.spice_ssl):
        if vmi.cfg.ssltype == "invalid_implicit_hs" or \
                "explicit" in vmi.cfg.ssltype:
            hostname = socket.gethostname()
            url = "spice://%s?tls-port=%s&port=%s" % (hostname, tls_port,
                                                      port)
        else:
            url = "spice://%s?tls-port=%s&port=%s" % (host_ip, tls_port,
                                                      port)
        return url
    # No SSL
    url = "spice://%s?port=%s" % (host_ip, port)
    return url


@reg.add_action(req=[ios.ILinux])
def rv_auth(vmi):
    """Client waits for user authentication if spice_password is set use qemu
    monitor password if set, else, if set, try normal password.

    Only for cmdline. File console.rv should have a password.

    """
    if vmi.cfg.ticket_send:
        # Wait for remote-viewer to launch.
        act.wait_for_win(vmi, RV_WIN_NAME_AUTH)
        act.str_input(vmi, vmi.cfg.ticket_send)


@reg.add_action(req=[ios.IOSystem])
def gen_vv_file(vmi):
    """Generates vv file for remote-viewer.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    """
    test = vmi.test
    cfg = vmi.cfg
    host_dir = os.path.expanduser('~')
    fpath = os.path.join(host_dir, cfg.rv_file)
    rv_file = open(fpath, 'w')
    rv_file.write("[virt-viewer]\n")
    rv_file.write("type=%s\n" % cfg.display)
    rv_file.write("host=%s\n" % utils.get_host_ip(test))
    rv_file.write("port=%s\n" % test.kvm_g.spice_port)
    if cfg.ticket_send:
        rv_file.write("password=%s\n" % cfg.ticket_send)
    if utils.is_yes(test.kvm_g.spice_ssl):
        rv_file.write("tls-port=%s\n" % test.kvm_g.spice_tls_port)
        rv_file.write("tls-ciphers=DEFAULT\n")
    host_subj = utils.get_host_subj(test)
    if host_subj:
        rv_file.write("host-subject=%s\n" % host_subj)
    cacert_host = utils.cacert_path_host(test)
    if cacert_host:
        cert = open(cacert_host)
        cert_auth = cert.read()
        cert_auth = cert_auth.replace('\n', r'\n')
        rv_file.write("ca=%s\n" % cert_auth)
    if cfg.full_screen:
        rv_file.write("fullscreen=1\n")
    if cfg.spice_proxy:
        rv_file.write("proxy=%s\n" % cfg.spice_proxy)
    if cfg.rv_debug:
        """TODO"""
        # rv_cmd.append("--spice-debug")  ..todo:: XXX TODO
    rv_file.close()
    return fpath


@reg.add_action(req=[ios.ILinux])
def rv_run(vmi, rcmd, ssn, env={}):
    cfg = vmi.cfg
    if cfg.rv_ld_library_path:
        cmd = utils.Cmd("export")
        cmd.append("LD_LIBRARY_PATH=%s" % cfg.rv_ld_library_path)
        act.run(vmi, cmd, ssn=ssn)
    if cfg.spice_proxy and cfg.rv_parameters_from != "file":
        cmd = utils.Cmd("export")
        cmd.append("SPICE_PROXY=%s" % cfg.spice_proxy)
        act.run(vmi, cmd, ssn=ssn)
    for key in env:
        cmd = utils.Cmd("export", "%s=%s" % (key, env[key]))
        act.run(vmi, cmd, ssn=ssn)
    if cfg.usb_redirection_add_device:
        # USB was created by qemu (root). This prevents right issue.
        # ..todo:: must be root session
        cmd = utils.Cmd("chown", cfg.username, cfg.file_path)
        act.run(vmi, cmd)
        if not act.check_usb_policy(vmi):
            act.add_usb_policy(vmi)
    try:
        pid = ssn.get_pid()
        logger.info("shell pid id: %s", pid)
        ssn.sendline(str(rcmd))
    except aexpect.ShellStatusError:
        logger.debug("Ignoring a status exception, will check connection"
                     "of remote-viewer later")


@reg.add_action(req=[ios.ILinux])
def rv_chk_con(vmi):
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
    test = vmi.test
    cfg = test.cfg
    proxy_port = None
    if vmi.cfg.ssltype == "invalid_implicit_hs" or \
            "explicit" in vmi.cfg.ssltype:
        hostname = socket.gethostname()    # See rv_url() function
        remote_ip = socket.gethostbyname(hostname)
    elif cfg.spice_proxy:
        prx_parse = cfg.spice_proxy.split('//')[-1]
        if ']:' in prx_parse or '.' in prx_parse and ':' in prx_parse:
            # port is specified in prx_parse
            remote_ip, _, proxy_port = prx_parse.rpartition(':')
        else:
            remote_ip, proxy_port = prx_parse, cfg.http_proxy_port
        remote_ip = remote_ip.strip('[]')
        if remote_ip.split('.')[-1].isalpha():
            remote_ip = socket.gethostbyname(remote_ip)
        logger.info("Proxy port to inspect: %s, proxy IP: s%",
                    proxy_port, remote_ip)
    else:
        remote_ip = utils.get_host_ip(test)
    rv_binary = os.path.basename(cfg.rv_binary)
    cmd1 = utils.Cmd("netstat", "-p", "-n", "--wide")
    grep_regex = "^tcp.*:.*%s.*ESTABLISHED.*%s.*" % (remote_ip, rv_binary)
    cmd2 = utils.Cmd("grep", "-e", grep_regex)
    cmd = utils.combine(cmd1, "|", cmd2)
    time.sleep(7)  # Wait all RV Spice links raise up.
    status, netstat_out = act.rstatus(vmi, cmd, admin=True)
    if status:
        raise utils.SpiceUtilsError("No active RV connections.")
    proxy_port_count = 0
    if cfg.spice_proxy:
        proxy_port_count = netstat_out.count(proxy_port)
        test.vm_g.info("Active proxy ports %s: %s", proxy_port, proxy_port_count)
    port = test.kvm_g.spice_port
    tls_port = test.kvm_g.spice_tls_port
    if port == 'no':
        port_count = 0
    else:
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
    if cfg.spice_plaintext_channels:
        plaintext_port_expected = len(cfg.spice_plaintext_channels.split(','))
        if port_count < plaintext_port_expected:
            msg = "Plaintext links per session is less then expected. %s (%s)" % (
                port_count, plaintext_port_expected)
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
    logger.debug("RV connection checking pass")


def rv_disconnect(test):
    """Terminates connection by killing remote-viewer.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    :return: None
    """
    act.kill_by_name(test.vmi_c, test.cfg.rv_binary)
