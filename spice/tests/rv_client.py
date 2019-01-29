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

"""Tests for SPICE remote-viewer client side.
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
    """Tests for SPICE remote-viewer client side.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.
    """

    test = stest.ClientTest(vt_test, test_params, env)
    vmi = test.vmi
    act.x_active(vmi)
    out = act.run(vmi, test_params['client_cmd'])
    assert test_params['client_output'] == out.rstrip()
