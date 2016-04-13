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
import aexpect
import glob
from virttest.virt_vm import VMDeadError
from autotest.client.shared import error
from virttest import utils_net
from spice.lib import rv_ssn
from spice.lib import stest
from spice.lib import utils


EXPECTED_RV_CORNERS_FS = [('+0','+0'),('-0','+0'),('-0','-0'),('+0','-0')]
WIN_TITLE = "'vm1 (1) - Remote Viewer'"


class Helper(object):
    """Call-able class."""

    def __init__(self, test):
        self.test = test

    def get_dic(self):
        return test.cfg

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
        logging.info("Query %s from VM: args=%s, kargs=%s", request, str(args),
                     str(kargs))
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
    ssn_c = test.ssn_c
    vm_c = test.vm_c
    utils.turn_accessibility(test, test.name_c)
    utils.clear_interface(test, test.name_c)
    # 
    utils.install_rpm(test, test.name_c, vm_c.params.get("epel_rpm"))
    utils.install_rpm(test, test.name_c, vm_c.params.get("dogtail_rpm"))
    utils.install_rpm(test, test.name_c, vm_c.params.get("wmctrl_rpm"))
    mdir = os.path.dirname(os.path.realpath(__file__))
    # Copy client tests to VM.
    tests_dir = os.path.join(mdir, os.path.pardir, cfg.client_tests)
    vm_c.copy_files_to(tests_dir, cfg.test_script_tgt)
    # Copy libraries to VM.
    libs_dir = os.path.join(mdir, os.path.pardir, "lib")
    libs_files = " ".join((os.path.join(libs_dir, _) for _ in ("params.py",)))
    vm_c.copy_files_to(libs_files, cfg.test_script_tgt)
    # Some tests could require established RV session, some of them, don't.
    is_connected = False
    if utils.is_yes(cfg.make_rv_connect):
        try:
            rv_ssn.connect(test)
            is_connected = True
        except rv_ssn.RVSessionConnect as excp:
            reason = str(excp)
        except rv_ssn.RVSessionError as e:
            raise exceptions.TestFail(str(e))
    tests = cfg.rv_gui_test_list.split()
    errors = 0
    commander = vm_c.commander(commander_path="/tmp")
    responder = Helper(test)
    commander.set_responder(responder)
    for test in tests:
        logging.info("Test: %s", test)
        # Adding parameters to the test
        test_path = "%s/%s/%s.py" % (cfg.test_script_tgt, cfg.client_tests,
                                        test)
        vm_c.info("cmdline : %s", test_path)
        try:
            cmd = commander.manage.python_file_run_with_helper(test_path)
        except Exception as e:
            logging.info("Got exception: %s", str(e))
            result = False
            raise exceptions.TestFail("Tests failed with %s:", str(e))
        else:
            result = cmd.results
        logging.info("Test finished with result: %s", result)
    pass
    # Responder in commander is not pickable.
    commander.close()
    vm_c.remote_sessions.remove(commander)
