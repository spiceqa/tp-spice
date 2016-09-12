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


"""Default values used in spice tests.
"""

import logging
import pprint
from spice.lib import utils
from virttest import virt_vm


logger = logging.getLogger(__name__)


# Complete list is defined at avocado-vt/virttest/qemu_vm.py spice_keys=, make
# duplication.
KVM_SPICE_KNOWN_PARAMS = [
    "spice_port",
    "spice_password",
    "spice_addr",
    "spice_ssl",
    "spice_tls_port",
    "spice_tls_ciphers",
    "spice_gen_x509",
    "spice_x509_dir",
    "spice_x509_prefix",
    "spice_x509_key_file",
    "spice_x509_cacert_file",
    "spice_x509_key_password",
    "spice_x509_secure",
    "spice_x509_cacert_subj",
    "spice_x509_server_subj",
    "spice_secure_channels",
    "spice_image_compression",
    "spice_jpeg_wan_compression",
    "spice_zlib_glz_wan_compression",
    "spice_streaming_video",
    "spice_agent_mouse",
    "spice_playback_compression",
    "spice_ipv4",
    "spice_ipv6",
    "spice_x509_cert_file",
    "disable_copy_paste",
    "spice_seamless_migration",
    "listening_addr"]


class AttributeDict(dict):
    """Dictionary class derived from standard dict. Reffer to keys as obj.key.
    """
    # http://stackoverflow.com/questions/4984647/
    __setattr__ = dict.__setitem__

    def __getattr__(self, key):
        if key in ["__getstate__", "__setstate__", "__slots__"]:
            raise AttributeError()
        try:
            item = dict.__getitem__(self, key)
        except KeyError:
            item = ""
        try:
            return utils.is_yes(item)
        except ValueError:
            return item

    def dump(self):
        for line in pprint.pformat(self).split('\n'):
                logger.info(line)

    #def __init__(self, custom_dict={}):
    #    self.update(custom_dict)


class SpiceTest(object):
    """Perform some basic initialization steps.

    Parameters
    ----------
    test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    Todo
    ----
        Add root sessions.

    Raises
    ------
        utils.SpiceTestFail
            Something is not good.
    """
    def __init__(self, test, parameters, env):
        logging.getLogger().setLevel(logging.INFO)
        utils.extend_api_vm()
        logger.info("Start test %s", test.name)
        self.cfg = AttributeDict()
        self.cfg.update(parameters)
        self.vms = {}
        self.vt_test = test
        vm_names = self.cfg.vms.split()
        """Holds all VM objects."""
        for name in vm_names:
            self.vms[name] = env.get_vm(name)
            try:
                self.vms[name].verify_alive()
            except virt_vm.VMDeadError as excp:
                raise utils.SpiceTestFail("Required VM is dead: %s" % excp)
        self.sessions = {}
        self.sessions_admin = {}
        """Establish session to each VM."""
        for name in vm_names:
            vm_obj = self.vms[name]
            self.sessions[name] = self.open_ssn(name)
            self.sessions_admin[name] = self.open_ssn(name, admin=True)
        self.kvm = {}
        """Spice KVM options per VM."""
        for name in vm_names:
            self.kvm[name] = AttributeDict()
            for prm in KVM_SPICE_KNOWN_PARAMS:
                self.kvm[name][prm] = self.vms[name].get_spice_var(prm)
                if self.kvm[name][prm]:
                    logger.info("VM %s spice server option %s is %s.", name,
                                 prm, self.kvm[name][prm])
        self.cmds = {}
        """Config set per VM."""
        self.cfg_vm = {}
        for name in vm_names:
            self.cfg_vm[name] = AttributeDict()
            self.cfg_vm[name].update(self.vms[name].get_params())
        """Commands set per VM."""
        for name in vm_names:
            self.cmds[name] = utils.Commands.get(self, name)


    def open_ssn(self, vm_name, admin=False):
        vm_obj = self.vms[vm_name]
        if admin:
            username = self.cfg.rootuser
            password = self.cfg.rootpassword
            vm_obj.info("Open new admin session.")
        else:
            username = self.cfg.username
            password = self.cfg.password
            vm_obj.info("Open new user session.")
        ssn = vm_obj.wait_for_login(username=username,
                                    password=password,
                                    timeout=int(self.cfg.login_timeout))
        """Export essentials variables per SSH session."""
        ssn.cmd("export DISPLAY=:0.0")
        return ssn


class ClientGuestTest(SpiceTest):
    """Class for tests with guest & client vms.
    """
    def __init__(self, test, parameters, env):
        super(ClientGuestTest, self).__init__(test, parameters, env)
        name_c = self.cfg.client_vm
        name_g = self.cfg.guest_vm
        self.name_c = name_c
        self.name_g = name_g
        self.vm_c = self.vms[name_c]
        self.vm_g = self.vms[name_g]
        self.ssn_c = self.sessions[name_c]
        self.ssn_g = self.sessions[name_g]
        self.assn_c = self.sessions_admin[name_c]
        self.assn_g = self.sessions_admin[name_g]
        self.kvm_c = self.kvm[name_c]
        self.kvm_g = self.kvm[name_g]
        self.cmd_c = self.cmds[name_c]
        self.cmd_g = self.cmds[name_g]
        self.cfg_c = self.cfg_vm[name_c]
        self.cfg_g = self.cfg_vm[name_g]


class OneVMTest(SpiceTest):
    """Class for one VM.
    """
    def __init__(self, test, parameters, env):
        super(OneVMTest, self).__init__(test, parameters, env)
        name = self.cfg.vms.split()[0]
        self.name = name
        self.vm = self.vms[name]
        self.ssn = self.sessions[name]
        self.assn = self.sessions_admin[name]
        self.kvm = self.kvm[name]
        self.cmd = self.cmds[name]
        self.cfg = self.cfg_vm[name]


class ClientTest(OneVMTest):
    """Alias to OneVMTest.
    """
    def __init__(self, test, parameters, env):
        super(ClientTest, self).__init__(test, parameters, env)


class GuestTest(OneVMTest):
    """Alias to OneVMTest.
    """
    def __init__(self, test, parameters, env):
        super(GuestTest, self).__init__(test, parameters, env)


def download_asset(asset_name, ini_dir=None, section=None, ddir=None):
    provider_dirs = asset.get_test_provider_subdirs(backend="spice")
    if ini_dir:
        provider_dirs.insert(0, ini_dir)
    for d in provider_dirs:
        ini_file = os.path.join(d, "%s.ini" % asset_name)
        if os.path.isfile(ini_file):
            asset_dir=d
            break
    assert os.path.isfile(ini_file), "Cannot find %.ini file." % asset_name
    asset_info = asset.get_asset_info(asset_name, ini_dir=asset_dir,
                                        section=asset_section)
    logger.info("Asset info: %s" % asset_info)
    if ddir:
        dst_file=os.path.basename(asset_info['destination'])
        asset_info['destination'] = os.path.join(ddir, dst_file)
    asset.download_file(asset_info)
    logger.info("Use: %s" % asset_info['destination'])
