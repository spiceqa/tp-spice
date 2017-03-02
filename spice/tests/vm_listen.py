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

"""Verify listening SPICE sockets of guest VM.
"""
import logging
import signal
from spice.lib import act
from spice.lib import stest

from autotest.client.shared import error

from virttest import env_process
from virttest import virt_vm

from avocado.utils import process

logger = logging.getLogger(__name__)


@error.context_aware
def run(vt_test, test_params, env):
    """Tests for SPICE listening sockets.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.
    """
    # See
    # https://www.redhat.com/archives/avocado-devel/2017-January/msg00012.html
    vmname = test_params['main_vm']
    if test_params['start_vm'] == "no":
        test_params['start_vm'] = "yes"
        if test_params['spice_port_closed'] == "yes":
            cmd = "nc -l %s" % test_params['spice_port']
            nc_process_cl = process.get_sub_process_klass(cmd)
            nc_process = nc_process_cl(cmd)
            nc_process_pid = nc_process.start()
        error.context("Start guest VM with invalid parameters.")
        try:
            env_process.preprocess_vm(vt_test, test_params, env, vmname)
        except virt_vm.VMCreateError, emsg:
            error_s = test_params['error_msg']
            if '%s,%s' in error_s:
                s_port = env.get_vm(vmname).spice_port
                error_s = error_s % (test_params['spice_addr'], s_port)
            if error_s in emsg.output and emsg.status == 1:
                logging.info("Guest terminated as expected: %s" % emsg.output)
                return
            else:
                raise error.TestFail("Guest creation failed, bad error message:"
                                     " %s and/or exit status: %s" %
                                     (emsg.output, emsg.status))
        finally:
            try:
                process.safe_kill(nc_process_pid, signal.SIGKILL)
            except:
                pass
        raise error.TestFail("Guest start normally, didn't quit as expected.")
    else:
        test = stest.GuestTest(vt_test, test_params, env)
        cfg = test.cfg
        vmi = test.vmi
        act.x_active(vmi)
        act.verify_listen(vmi)
