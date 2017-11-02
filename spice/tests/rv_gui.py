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

"""rv_gui.py - runs dogtail tests on the client.

Requirements for host machine
-----------------------------

    - rv_setup must be run to have dogtail be installed on the client.
    - rv_connect must be run to restart the gdm session.

This file doesn't make any decision about test success. The decision is made by
test running at VM.

Test is successful if all sub-tests running at VM are successful.

"""

import os
import logging
import traceback
from spice.lib import stest
from spice.lib import utils
from spice.lib import act

EXPECTED_RV_CORNERS_FS = [('+0', '+0'), ('-0', '+0'),
                          ('-0', '-0'), ('+0', '-0')]
WIN_TITLE = "'vm1 (1) - Remote Viewer'"


logger = logging.getLogger(__name__)


class Helper(object):
    """Call-able class."""

    def __init__(self, test):
        self.test = test

    def get_cfg(self):
        """Prepare for cPickle serialization
        """
        return dict((v, k) for (v, k) in self.test.cfg.iteritems())

    def get_x_var(self, var_name, vm_name):
        var_val = act.get_x_var(self.test.vm_info[vm_name], var_name)
        return var_val

    def get_uri(self):
        host_ip = utils.get_host_ip(self.test)
        port = self.test.kvm_g.spice_port
        uri = "spice://%s?port=%s" % (host_ip, port)
        if utils.is_yes(self.test.kvm_g.spice_ssl):
            tls_port = self.test.kvm_g.spice_tls_port
            uri = uri + "\\&tls-port=%s" % tls_port
        logging.info("Reply for URI req: %s", uri)
        return uri

    def bad_request(self, *args, **kargs):
        return NotImplementedError('BadRequest')

    def __call__(self, request, *args, **kargs):
        """Respond for quires from VM.

        Parameters
        ----------
        request : str
            Kind of request.
        *args
            Variable length argument list.
        **kargs
            Arbitrary keyword arguments.

        Returns
        -------
            Pickable object. Depends on request.

        """
        logging.info("Query --> %s: args=%s, kargs=%s", str(request),
                     str(args), str(kargs))
        answ = getattr(self, str(request), self.bad_request)
        return answ(*args, **kargs)


def run(vt_test, test_params, env):
    """GUI tests for remote-viewer.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    Raises
    ------
    TestFail
        Test fails for expected behaviour.

    """
    test = stest.ClientGuestTest(vt_test, test_params, env)
    cfg = test.cfg
    vmi_c = test.vmi_c
    vmi_g = test.vmi_g
    vm_c = test.vm_c
    # Screen lock is now disabled in kickstart file for source QCOW images of
    # SPICE-QE team (https://gitlab.cee.redhat.com/spiceqe/install-compose/ks).
    # act.lock_scr_off(vmi_c)
    act.turn_accessibility(vmi_c)
    if utils.vm_is_rhel6(vm_c):
        act.reset_gui(vmi_c)  # Activate accessibility for rhel6, BZ#1340160 for rhel7
    # act.reset_gui(vmi_g)  # disabled because BZ#1340160
    act.install_rpm(vmi_c, test.cfg_c.epel_rpm)
    act.install_rpm(vmi_c, test.cfg_c.dogtail_rpm)
    act.install_rpm(vmi_c, test.cfg_c.wmctrl_rpm)
    act.install_rpm(vmi_c, "xdotool")
    # Copy tests to client VM.
    # Some tests could require established RV session, some of them, don't.
    is_connected = False
    if cfg.make_rv_connect:
        act.x_active(vmi_g)
        ssn = act.new_ssn(vmi_c)
        act.rv_connect(vmi_c, ssn)
        act.rv_chk_con(vmi_c)
        is_connected = True
    errors = 0
    logging.getLogger().setLevel(logging.DEBUG)
    try:
        ddir = act.dst_dir(vmi_c)
        commander = vm_c.commander(commander_path=ddir)
    except Exception as e:
        logger.info("Failed to create commander: %s.", str(e))
        fname = "/tmp/remote_runner.log"
        vm_c.copy_files_from(fname, fname)
        f = open(fname)
        logger.info("Remote runner log: %s.", f.read())
    responder = Helper(test)
    commander.set_responder(responder)
    tdir = act.cp2vm(vmi_c, cfg.client_tests)
    tpath = os.path.join(tdir, cfg.ctest)
    vm_c.info("Client test: %s.", tpath)
    try:
        cmd = commander.manage.python_file_run_with_helper(tpath)
    except Exception as e:
        a = traceback.format_exc()
        logger.info("Exceptio: %s: %s.", repr(e), a)
    result = cmd.results
    logger.info("Test %s finished with result: %s", cfg.ctest, result)
    if cfg.make_rv_connect:
        out = ssn.read_nonblocking()
        logger.info("RV log: %s.", str(out))
    # Responder in commander is not pickable.
    commander.close()
    vm_c.remote_sessions.remove(commander)
    assert result == 0
