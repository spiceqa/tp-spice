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
#
# Copyright: Red Hat Inc. 2016
# Author: Andrei Stepanov <astepano@redhat.com>
#

"""Called by act.py.
Implements act.something_callable(vm_info, ...).
"""

import logging
from spice.lib import reg
from spice.lib import ios
from spice.lib import utils


logger = logging.getLogger(__name__)
registry = reg.registry


class Action(object):
    def __init__(self, action_name):
        self.name = action_name

    def __call__(self, vmi, *args, **kwargs):
        os = registry.lookup([], ios.IOSystem,
                             vmi.cfg.interface_os)
        ver = registry.lookup([], ios.IVersionMajor,
                              vmi.cfg.interface_os_version)
        mver = registry.lookup([], ios.IVersionMinor,
                               vmi.cfg.interface_os_mversion)
        arch = registry.lookup([], ios.IArch,
                               vmi.cfg.interface_os_arch)
        ovirt_ver = registry.lookup([], ios.IArch,
                                    vmi.cfg.interface_ovirt_version)
        os_info = ",".join(map(repr, [os, ver, mver, arch, ovirt_ver]))
        msg = "OS info: %s" % os_info
        utils.debug(vmi, msg)
        lookup_order = [[os, ver, mver, arch, ovirt_ver],
                        [os, ver, mver, ovirt_ver],
                        [os, ver, arch, ovirt_ver],
                        [os, ver, ovirt_ver],
                        [os, ovirt_ver],
                        [os, ver, mver, arch],
                        [os, ver, mver],
                        [os, ver, arch],
                        [os, ver],
                        [os]]
        action = None
        iset = None
        for iset in lookup_order:
            if not all(iset):
                continue
            action = registry.lookup(iset, reg.IVmAction, self.name)
            if action:
                break
        if not action:
            msg = "Cannot find suitable implementation for: %s." % self.name
            raise utils.SpiceTestFail(vmi.test, msg)
        act_reqs = ",".join(map(repr, iset))
        msg = "Call: %s, for OS interface: %s" % (self.name, act_reqs)
        utils.debug(vmi, msg)
        return action(vmi, *args, **kwargs)
