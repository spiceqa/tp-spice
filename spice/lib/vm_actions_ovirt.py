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


@reg.add_action(req=[ios.IOvirt4, ios.ILinux])
def new_ssn(vmi, admin=False):
    utils.debug(vmi, "Yahooooooooooooo!")
    #if admin:
    #    username = vmi.cfg.rootuser
    #    password = vmi.cfg.rootpassword
    #    utils.debug(vmi, "Open a new session for: admin.")
    #else:
    #    username = vmi.cfg.username
    #    password = vmi.cfg.password
    #    utils.debug(vmi, "Open a new session for: user.")
    #ssn = vmi.vm.wait_for_login(username=username,
    #                            password=password,
    #                            timeout=int(vmi.cfg.login_timeout))
    #act.export_vars(vmi, ssn)
    #return ssn
