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
from spice.lib import params
from spice.lib import utils
from virttest import virt_vm


class AttributeDict(dict):
    """Dictionary class derived from standard dict. Reffer to keys as obj.key.
    """
    # http://stackoverflow.com/questions/4984647/
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


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
        logging.info("Start test %s", test.name)
        self.cfg = AttributeDict()
        cfg = self.cfg
        """Construct test's parameters. Merge default pre-defined values with
        provided through Cartesian config."""
        for prm in (x for x in dir(params.Params) if not x.startswith('_')):
            cfg[prm] = getattr(params.Params, prm)
        cfg.update(parameters)
        self.vms = {}
        vm_names = cfg.vms.split()
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
            self.sessions[name] = vm_obj.wait_for_login(
                username=cfg.username, password=cfg.password,
                timeout=int(cfg.login_timeout))
            self.sessions_admin[name] = vm_obj.wait_for_login(
                username=cfg.rootuser, password=cfg.rootpassword,
                timeout=int(cfg.login_timeout))
        self.kvm = {}
        """Spice KVM options per VM."""
        for name in vm_names:
            self.kvm[name] = AttributeDict()
            for prm in params.KVM_SPICE_KNOWN_PARAMS:
                self.kvm[name][prm] = self.vms[name].get_spice_var(prm)
                if self.kvm[name][prm]:
                    logging.info("VM %s spice server option %s is %s.", name,
                                 prm, self.kvm[name][prm])
        utils.extend_api_vm()


class ClientGuestTest(SpiceTest):
    """Simplify writing tests with guest & client vms.
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
