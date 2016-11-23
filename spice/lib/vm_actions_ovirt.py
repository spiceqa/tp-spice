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
import subprocess

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

@reg.add_action(req=[ios.IOvirt4])
def get_ip(vmi):
    """Get IP for VM.

    Notes
    -----

        * At this moment we use Ovirt ReST API. We need to know only VMs IP.
        If it is necessary to send more complex requests consider to switch to
        Ovirt Python SDK.

        * This function requires to installed and running a daemon from RPM
        rhevm-guest-agent-common or GuestTools for Windows.:

            28236 ?        Ssl   34:36 /usr/bin/python /usr/share/ovirt-guest-agent/ovirt-guest-agent.py

        * Will be called next command:

        curl \
            --insecure \
            --request GET \
            --header "Filter: true" \
            --header "Accept: application/xml" \
            --user "auto@spice.brq.redhat.com:redhat" \
            'https://rhevm36.spice.brq.redhat.com/ovirt-engine/api/vms/?search=auto_pool_06_rhel72' \
            | xmllint --xpath 'string(/vms/vm/guest_info/ips/ip/@address)' -

    Returns
    -------
    str
        String with IP address of a VM.

    Raises
    ------
    Exception
        Cannot get IP for VM.
    """
    cfg = vmi.cfg
    cmd1 = utils.Cmd("curl")
    cmd.append("--insecure")
    cmd.append("--request")
    cmd.append("GET")
    cmd.append("--header")
    cmd.append("Filter: true")
    cmd.append("--header")
    cmd.append("Accept: application/xml")
    cmd.append("--user")
    user = "{user}@{profile}:{passw}".format(user=cfg.ovirt_user,
                                             profile=cfg.ovirt_profile,
                                             passw=cfg.ovirt_password)
    cmd.append(user)
    if cfg.ovirt_vm_name:
        # The same syntax as in admin portal search bar.
        search = "name=%s" % cfg.ovirt_vm_name
    elif cfg.ovirt_pool_name:
        search = "pool=%s" % cfg.ovirt_pool_name
    else:
        raise Exception("Not defined: VM or pool name.")
    url = "{ovirt_engine}/api/vms/?search={search}".format(
        ovirt_engine=cfg.ovirt_engine_url,
        search=search)
    cmd.append(url)
    cmd2 = utils.Cmd("xmllint",
                     "--xpath",
                     "string(/vms/vm/guest_info/ips/ip/@address)",
                     "-")
    cmd_get_ip = utils.combine(cmd1, "|", cmd2)
    out = subprocess.check_output(cmd_get_ip, shell=True)
    return out
