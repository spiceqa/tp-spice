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
from spice.lib import reg
from spice.lib import utils
from virttest import virt_vm


logger = logging.getLogger(__name__)
registry = reg.registry


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

#    def __init__(self, custom_dict={}):
#        self.update(custom_dict)


class VmInfo(object):

    def __init__(self, test, vm_name):
        self.test = test
        self.cfg = test.cfg_vm[vm_name]     # VM config
        self.ccfg = test.cfg                # Common config
        self.vm = test.vms[vm_name]
        self.vm_name = vm_name
        self.kvm = test.kvms[vm_name]


class VmOvirtInfo(object):

    def __init__(self, test, vm_name):
        self.test = test
        self.cfg = test.cfg_vm[vm_name]     # VM config
        self.ccfg = test.cfg                # Common config
        self.vm_name = vm_name


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

    Raises
    ------
        utils.SpiceTestFail
            Something is not good.
    """
    def __init__(self, test, parameters, env):
        # Change log level here from info to debug:
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
                raise utils.SpiceTestFail(self,
                                          "Required VM is dead: %s" % excp)
        self.kvms = {}
        """Spice KVM options per VM."""
        for name in vm_names:
            self.kvms[name] = AttributeDict()
            for prm in KVM_SPICE_KNOWN_PARAMS:
                self.kvms[name][prm] = self.vms[name].get_spice_var(prm)
                if self.kvms[name][prm]:
                    logger.info("VM %s spice server option %s is %s.", name,
                                prm, self.kvms[name][prm])
        """Config set per VM."""
        self.cfg_vm = {}
        for name in vm_names:
            self.cfg_vm[name] = AttributeDict()
            self.cfg_vm[name].update(self.vms[name].get_params())
        """Actions set per VM's OS."""
        self.vm_info = {}
        for name in vm_names:
            self.vm_info[name] = VmInfo(self, name)
        """Ovirt."""
        vm_roles = self.cfg.ovirt_vms.split()
        """Config set per Ovirt VM."""
        for name in vm_roles:
            self.cfg_vm[name] = AttributeDict()
            vm_role_cfg = parameters.object_params(name)
            # See env_process.py: process(..., postprocess_vm,...)
            self.cfg_vm[name].update(vm_role_cfg)
        """Actions set per Ovirt VM's OS."""
        for name in vm_roles:
            self.vm_info[name] = VmOvirtInfo(self, name)


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
        self.kvm_c = self.kvms[name_c]
        self.kvm_g = self.kvms[name_g]
        self.cfg_c = self.cfg_vm[name_c]
        self.cfg_g = self.cfg_vm[name_g]
        self.vmi_c = self.vm_info[name_c]
        self.vmi_g = self.vm_info[name_g]


class OneVMTest(SpiceTest):
    """Class for one VM.

    Notes
    -----
    If name == None, then use a name of the first VM.

    """
    def __init__(self, test, parameters, env, name=None):
        super(OneVMTest, self).__init__(test, parameters, env)
        if not name:
            name = self.cfg.vms.split()[0]
        self.name = name
        self.vm = self.vms[name]
        self.kvm = self.kvms[name]
        self.cfg = self.cfg_vm[name]  # Fix me, base class has .cfg
        self.vmi = self.vm_info[name]


class ClientTest(OneVMTest):
    """Alias to OneVMTest.
    """
    def __init__(self, test, parameters, env):
        vm_name = parameters.get("client_vm", None)
        super(ClientTest, self).__init__(test, parameters, env, name=vm_name)


class GuestTest(OneVMTest):
    """Alias to OneVMTest.
    """
    def __init__(self, test, parameters, env):
        vm_name = parameters.get("guest_vm", None)
        super(GuestTest, self).__init__(test, parameters, env, name=vm_name)


class ClientGuestOvirtTest(SpiceTest):
    """Guest is running at Ovirt portal. No running avocado-vt KVM for guest.
    """
    def __init__(self, test, parameters, env):
        super(ClientGuestOvirtTest, self).__init__(test, parameters, env)
        name_c = self.cfg.client_vm
        name_g = self.cfg.guest_vm
        self.name_c = name_c
        self.name_g = name_g
        self.vm_c = self.vms[name_c]
        # self.vm_g = is absent for Ovirt
        self.kvm_c = self.kvms[name_c]
        # self.kvm_g = is absent for Ovirt
        self.cfg_c = self.cfg_vm[name_c]
        self.cfg_g = self.cfg_vm[name_g]
        self.vmi_c = self.vm_info[name_c]
        self.vmi_g = self.vm_info[name_g]
