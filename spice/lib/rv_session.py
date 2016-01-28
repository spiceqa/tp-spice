#!/usr/bin/env python

"""Connect with remote-viewer from client VM to guest VM.

Client requires
---------------
    - remote-viewer

Guest requires
--------------
    - Xorg
    - netstat
"""

import os
import logging
import socket
from aexpect import ShellStatusError
from virttest import utils_net
from virttest import utils_misc
from spice.lib import utils_spice
from spice.lib import conf

# Root exception for the RV Session
class RVSessionError(Exception):
    """Exception for remote-viewer session.
    """


class RvSession(object):
    """Class used to manage remote-viewer connection.

    Parameters
    ----------
    params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    """

    def __init__(self, params, env):
        self.hostname = socket.gethostname()
        self.params = params
        self.env = env
        utils_spice.extend_vm()
        self.cfg = conf.Params(params)
        self.guest_vm = env.get_vm(self.cfg.guest_vm)
        self.guest_vm.verify_alive()
        timeout = int(self.cfg.login_timeout)
        self.guest_session = self.guest_vm.wait_for_login(timeout=timeout)
        self.client_vm = env.get_vm(self.cfg.client_vm)
        self.client_vm.verify_alive()
        self.client_session = self.client_vm.wait_for_login(timeout=timeout)
        if self.client_vm.is_linux():
            self.client_session.cmd("export DISPLAY=:0.0")
        self.host = utils_net.get_host_ip_address(self.params)
        if self.guest_vm.get_spice_var("listening_addr") == "ipv6":
            self.host = "[" + utils_misc.convert_ipv4_to_ipv6(self.host) + "]"
        self.port = None
        self.tls_port = None
        self.rv_binary = self.cfg.rv_binary
        self.secure_channels = self.cfg.spice_secure_channels
        self.secure_channels_num = 0
        if self.secure_channels:
            self.secure_channels_num = len(self.secure_channels.split(','))
        self.proxy = self.cfg.spice_proxy
        self.ssltype = self.cfg.ssltype
        self.test_type = self.cfg.test_type
        self.host_subj = None
        self.cacert_host = None
        if self.guest_vm.get_spice_var("spice_ssl") == "yes":
            # Client needs cacert file
            self.cacert_host = "%s/%s" % (self.cfg.spice_x509_prefix,
                                          self.cfg.spice_x509_cacert_file)
            # Cacert subj is in format for create certificate(with '/'
            # delimiter) remote-viewer needs ',' delimiter. And also is needed
            # to remove first character (it's '/')
            self.host_subj = self.guest_vm.get_spice_var(
                "spice_x509_server_subj")
            self.host_subj = self.host_subj.replace('/', ',')[1:]
            if self.ssltype == "invalid_explicit_hs":
                self.host_subj = "Invalid Explicit HS"
            else:
                self.host_subj += self.host

    def kill_by_name(self, name):
        """
        Kill selected app on selected VM

        @params name - Name of the binary
        """
        logging.info("About to kill %s", name)
        if self.client_vm.params.get("os_type") == "linux":
            try:
                output = self.client_session.cmd_output(
                    "pkill %s" % name.split(os.path.sep)[-1])
            except:
                if output == 1:
                    pass
                else:
                    raise RVSessionError
        elif self.client_vm.params.get("os_type") == "windows":
            self.client_session.cmd_output("taskkill /F /IM %s" %
                                           name.split('\\')[-1])

    def connect(self):
        """Establish connection between client and guest based on test
        parameters supplied at initialization.

        Returns
        -------
        None

        """
        rv_binary = self.cfg.rv_binary
        rv_ld_library_path = self.cfg.rv_ld_library_path
        display = self.cfg.display
        disable_audio = self.cfg.disable_audio
        full_screen = self.cfg.full_screen
        check_spice_info = self.cfg.spice_info
        # cmd var keeps final remote-viewer command line to be executed on
        # client
        cmd = rv_binary
        if self.client_vm.is_linux():
            cmd = cmd + " --display=:0.0"
        # If qemu_ticket is set, set the password of the VM using the
        # qemu-monitor
        ticket = None
        ticket_send = self.cfg.spice_password_send
        qemu_ticket = self.cfg.qemu_password
        if qemu_ticket:
            self.guest_vm.monitor.cmd("set_password spice %s" % qemu_ticket)
            logging.info("Sending to qemu monitor: set_password spice %s",
                         qemu_ticket)
        gencerts = self.cfg.gencerts
        certdb = self.cfg.certdb
        smartcard = self.cfg.smartcard
        rv_parameters_from = self.cfg.rv_parameters_from
        if rv_parameters_from == 'file':
            cmd += " " + self.cfg.rv_file
        if display == "vnc":
            raise RVSessionError("remote-viewer vnc not implemeted")
        elif display != "spice":
            raise RVSessionError("Unsupported display value")
        ticket = self.guest_vm.get_spice_var("spice_password")
        if self.guest_vm.get_spice_var("spice_ssl") == "yes":
            # Client needs cacert file
            cacert_client = self.cacert_host
            if self.client_vm.is_linux():
                self.client_session.cmd("rm -rf %s && mkdir -p %s" % (
                    self.cfg.spice_x509_prefix, self.cfg.spice_x509_prefix))
            if self.client_vm.is_win():
                cacert_client = "C:\\%s" % self.cfg.spice_x509_cacert_file
            self.client_vm.copy_files_to(self.cacert_host, cacert_client)
            self.tls_port = self.guest_vm.get_spice_var("spice_tls_port")
            self.port = self.guest_vm.get_spice_var("spice_port")
            # If it's invalid implicit, a remote-viewer connection will be
            # attempted with the hostname, since ssl certs were generated with
            # the ip address.
            escape_char = self.client_vm.params.get("shell_escape_char", '\\')
            if self.ssltype == "invalid_implicit_hs" or \
                    "explicit" in self.ssltype:
                spice_url = " spice://%s?tls-port=%s%s&port=%s" % (
                    self.hostname, self.tls_port, escape_char, self.port)
            else:
                spice_url = " spice://%s?tls-port=%s%s&port=%s" % (
                    self.host, self.tls_port, escape_char, self.port)
            if rv_parameters_from == "menu":
                line = spice_url
            elif rv_parameters_from == "file":
                pass
            else:
                cmd += spice_url
            if rv_parameters_from != "file":
                cmd += " --spice-ca-file=%s" % cacert_client
            if (self.cfg.spice_client_host_subject == "yes" and
                    rv_parameters_from != "file"):
                cmd += " --spice-host-subject=\"%s\"" % self.host_subj
        else:
            # Not spice_ssl.
            self.port = self.guest_vm.get_spice_var("spice_port")
            if rv_parameters_from == "menu":
                # Line to be sent through monitor once r-v is started without
                # spice url.
                line = "spice://%s?port=%s" % (self.host, self.port)
            elif rv_parameters_from == "file":
                pass
            else:
                cmd += " spice://%s?port=%s" % (self.host, self.port)
        # Usbredirection support.
        if self.cfg.usb_redirection_add_device_vm2 == "yes":
            logging.info("USB redirection set auto redirect on connect for"
                         "device class 0x08")
            cmd += " --spice-usbredir-redirect-on-connect=\"0x08,-1,-1,-1,1\""
            client_root_session = self.client_vm.wait_for_login(
                timeout=int(self.cfg.login_timeout),
                username=conf.USERNAME,
                password=conf.PASSWORD)
            usb_mount_path = self.cfg.file_path
            # USB was created by qemu (root). This prevents right issue.
            client_root_session.cmd("chown test:test %s" % usb_mount_path)
            client_root_session.close()
            if not utils_spice.check_usb_policy(self.client_vm, self.params):
                logging.info("No USB policy.")
                utils_spice.add_usb_policy(self.client_vm)
                utils_spice.wait_timeout(3)
            else:
                logging.info("USB policy OK")
        else:
            logging.info("No USB redirection")
        # Check to see if the test is using the full screen option.
        if full_screen == "yes" and rv_parameters_from != "file":
            logging.info("Remote Viewer Set to use Full Screen")
            cmd += " --full-screen"
        if disable_audio == "yes":
            logging.info("Remote Viewer Set to disable audio")
            cmd += " --spice-disable-audio"
        # Check to see if the test is using a smartcard.
        if smartcard == "yes":
            logging.info("remote viewer Set to use a smartcard")
            if rv_parameters_from != "file":
                cmd += " --spice-smartcard"
            if certdb is not None:
                logging.debug("Remote Viewer set to use the following "
                              "certificate database: %s", certdb)
                cmd += " --spice-smartcard-db " + certdb
            if gencerts is not None:
                logging.debug(
                    "Remote Viewer set to use the following certs: " +
                    gencerts)
                cmd += " --spice-smartcard-certificates " + gencerts
        if self.client_vm.is_linux():
            cmd = "nohup " + cmd + " &> ~/rv.log &"  # Launch it on background
            if rv_ld_library_path:
                cmd = "export LD_LIBRARY_PATH=" + \
                    rv_ld_library_path + ";" + cmd
        if rv_parameters_from == "file":
            logging.info("Generating file")
            self.generate_vv_file()
            logging.info("Uploading file to client")
            self.client_vm.copy_files_to("rv_file.vv", self.cfg.rv_file)
        # Launching the actual set of commands.
        try:
            if rv_ld_library_path:
                utils_spice.print_rv_version(self.client_session,
                                             "LD_LIBRARY_PATH=/usr/local/lib "
                                             "%s" % rv_binary)
            else:
                utils_spice.print_rv_version(self.client_session, rv_binary)
        except ShellStatusError as ShellProcessTerminatedError:
            # Sometimes It fails with Status error, ingore it and continue.
            # It's not that important to have printed versions in the log.
            logging.debug(
                "Ignoring a Status Exception that occurs from calling print"
                "versions of remote-viewer or spice-gtk"
            )
        logging.info("Launching %s on the client (virtual)", cmd)
        if self.proxy:
            if "http" in self.proxy:
                split = self.proxy.split('//')[1].split(':')
            else:
                split = self.proxy.split(':')
            self.host = split[0]
            if len(split) > 1:
                self.port = split[1]
            else:
                self.port = "3128"
            if rv_parameters_from != "file":
                if self.client_vm.is_linux():
                    self.client_session.cmd("export SPICE_PROXY=%s" %
                                            self.proxy)
                elif self.client_vm.is_win():
                    self.client_session.cmd_output("SET SPICE_PROXY=%s" %
                                                   self.proxy)
        try:
            logging.info("spice,connection: %s", cmd)
            self.client_session.cmd(cmd)
        except ShellStatusError:
            logging.debug("Ignoring a status exception, will check connection"
                          "of remote-viewer later")
        # Send command line through monitor since url was not provided
        if rv_parameters_from == "menu":
            utils_spice.wait_timeout(1)
            utils_spice.str_input(self.client_vm, line)
        # client waits for user entry (authentication) if spice_password is set
        # use qemu monitor password if set, else, if set, try normal password.
        if qemu_ticket:
            # Wait for remote-viewer to launch
            utils_spice.wait_timeout(5)
            utils_spice.str_input(self.client_vm, qemu_ticket)
        elif ticket:
            if ticket_send:
                ticket = ticket_send
            utils_spice.wait_timeout(5)  # Wait for remote-viewer to launch
            utils_spice.str_input(self.client_vm, ticket)
        utils_spice.wait_timeout(5)  # Wait for conncetion to establish

    """
    # @TODO: This probably needs moving back to rv_connect or to a new file
    # tbh, not sure why it's here -.-
        # Get spice info
        output = guest_vm.monitor.cmd("info spice")
        logging.debug("INFO SPICE")
        logging.debug(output)

        # Check to see if ipv6 address is reported back from qemu monitor
        if (check_spice_info == "ipv6"):
            logging.info("Test to check if ipv6 address is reported"
                    " back from the qemu monitor")
            # Remove brackets from ipv6 host ip
            if (host_ip[1:len(host_ip) - 1] in output):
            logging.info("Reported ipv6 address found in output from"
                        " 'info spice'")
            else:
            raise error.TestFail("ipv6 address not found from qemu monitor"
                                " command: 'info spice'")
        else:
            logging.info("Not checking the value of 'info spice'"
                        " from the qemu monitor")
    """

    def is_connected(self):
        """Tests whether or not is connection active.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        rv_binary = self.cfg.rv_binary
        rv_binary = os.path.basename(rv_binary)
        if ".exe" in rv_binary:
            cmd = "netstat -n"
        else:
            cmd = (
                '(netstat -pn 2>&1| grep "^tcp.*:.*%s.*ESTABLISHED.*%s.*")' %
                (self.host, rv_binary)
            )
        netstat_out = self.client_session.cmd_output(cmd)
        if "ESTABLISHED" not in netstat_out:
            logging.error("netstat reports no established connection")
            return False
        port = self.port
        tls_port = self.tls_port
        port_count = netstat_out.count(port)
        tls_port_count = 0
        if tls_port:
            tls_port_count = netstat_out.count(tls_port)
        # logging.info("netstat output: %s", netstat_out)
        if (port_count + tls_port_count) < 4:
            logging.error("Not enough channels were open")
            return False
        if self.secure_channels and tls_port_count < self.secure_channels_num:
            logging.error("Not enough secure channels open")
            return False
        for line in netstat_out.split('\n'):
            if (
                    (port and
                     port in line and
                     "ESTABLISHED" not in line) or
                    (tls_port and
                     tls_port in line and
                     "ESTABLISHED" not in line)
            ):
                logging.error(
                    "Failed to get established connection from netstat"
                )
                return False
        logging.info("Connection checking pass")
        return True

    def disconnect(self):
        """
        Terminates connection by killing remote-viewer.

        :return: None
        """
        self.kill_by_name(self.cfg.rv_binary)

    def clear_guest(self):
        """ Clears interface on guest """
        utils_spice.clear_interface(self.guest_vm, int(self.cfg.login_timeout))

    def clear_client(self):
        """ Clears interface on client """
        utils_spice.clear_interface(self.client_vm,
                                    int(self.cfg.login_timeout))

    def clear_interface_all(self):
        """
        Clears interface on all vms without restart.
        """
        for vm in self.cfg.vms.split():
            utils_spice.clear_interface(self.env.get_vm(vm),
                                        int(self.cfg.login_timeout))

    def generate_vv_file(self):
        """
        Generates vv file for remote-viewer

        @param params:          all parameters of the test
        @param guest_vm:        object of a guest VM
        @param host_subj:       subject of the host
        @param cacert:          location of certificate of host
        """
# def gen_rv_file(params, guest_vm, host_subj = None, cacert = None):
        full_screen = self.cfg.full_screen
        proxy = self.cfg.spice_proxy
        rv_file = open('rv_file.vv', 'w')
        rv_file.write("[virt-viewer]\n" +
                      "type=%s\n" % self.cfg.display +
                      "host=%s\n" %
                      utils_net.get_host_ip_address(self.params) +
                      "port=%s\n" % self.guest_vm.get_spice_var("spice_port"))
        ticket = self.cfg.spice_password
        ticket_send = self.cfg.spice_password_send
        qemu_ticket = self.cfg.qemu_password
        if ticket_send:
            ticket = ticket_send
        if qemu_ticket:
            ticket = qemu_ticket
        if ticket:
            rv_file.write("password=%s\n" % ticket)

        if self.guest_vm.get_spice_var("spice_ssl") == "yes":
            rv_file.write("tls-port=%s\n" %
                          self.guest_vm.get_spice_var("spice_tls_port"))
            rv_file.write("tls-ciphers=DEFAULT\n")
        if self.host_subj:
            rv_file.write("host-subject=%s\n" % self.host_subj)
        if self.cacert_host:
            cert = open(self.cacert_host)
            cert_auth = cert.read()
            cert_auth = cert_auth.replace('\n', r'\n')
            rv_file.write("ca=%s\n" % cert_auth)
        if full_screen == "yes":
            rv_file.write("fullscreen=1\n")
        if proxy:
            rv_file.write("proxy=%s\n" % proxy)

    # TODO: Update properties and add functionality to test others
    # Other properties:
    # username
    # version
    # title
    # toggle-fullscreen (key combo)
    # release-cursor (key combo)
    # smartcard-insert
    # smartcard-remove
    # enable-smartcard
    # enable-usbredir
    # color-depth
    # disable-effects
    # usb-filter
    # secure-channels
    # delete-this-file (0,1)

    def set_client_resolution(self, res, display='qxl-0'):
        """ Sets resolution of a display device in client

        :param res: Requested resolution (WidthxHeight)
        :param display: Display device that you want to change
        :return:
        """
        return utils_spice.set_resolution(self.client_session, res, display)

    def get_client_resolution(self):
        """ Get client resolution

        :return: List of resolutions on individual displays
        """
        return utils_spice.get_display_resolution(self.client_session)

    def set_guest_resolution(self, res, display='qxl-0'):
        """ Sets resolution of a display device in guest

        :param res: Requested resolution (WidthxHeight)
        :param display: Display device you want to change
        :return:
        """
        return utils_spice.set_resolution(self.guest_session, res, display)

    def get_guest_resolution(self):
        """ Get guest resolution

        :return: List of resolutions on individual displays
        """
        return utils_spice.get_display_resolution(self.guest_session)

    def get_windows_ids(self):
        """
        Get ids of active remote-viewer windows

        :return: List of remote-viewer window ids
        """
        return utils_spice.get_open_window_ids(self.client_session,
                                               'remote-viewer')

    def is_fullscreen_xprop(self, window=0):
        """ Tests if remote-viewer windows is fullscreen based on xprop

        :param window: Which window is tested (0-3)
        :return: Returns True if fullscreen property is set
        """
        win_id = self.get_windows_ids()[window]
        props = utils_spice.get_window_props(self.client_session, win_id)
        for prop in props.split('\n'):
            if ('_NET_WM_STATE(ATOM)' in prop and
                    '_NET_WM_STATE_FULLSCREEN ' in prop):
                return True

    def window_resolution(self, window=0):
        win_id = self.get_windows_ids()[window]
        return utils_spice.get_window_geometry(self.client_session, win_id)

    def get_fullscreen_windows(self):
        windows = self.get_windows_ids()
    # TODO: Will need to install xdotool on client VM (or dogtail, or both)
