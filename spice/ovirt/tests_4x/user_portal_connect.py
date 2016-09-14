#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import logging

import time
import logging

from avocado.core import exceptions
from autotest.client.shared import error
from virttest import asset

from spice.lib import stest

logger = logging.getLogger(__name__)

@error.context_aware
def run(vt_test, test_params, env):
    """Download SeleniumHQ server, and copy it to a client.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    """
    test = stest.ClientGuestTest(vt_test, test_params, env)
    ssn = test.open_ssn(test.name_c)
    test.cmd_c.run_selenium(ssn)
    time.sleep(10)
    out = ssn.read_nonblocking()
    logger.info("RV log: %s.", str(out))
    time.sleep(10000)

