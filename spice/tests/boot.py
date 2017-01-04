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

"""Boot VM.
"""

import time
import logging
from virttest import utils_test
from autotest.client.shared import error

logger = logging.getLogger(__name__)


@error.context_aware
def run(test, params, env):
    """Boot VM.

    Parameters
    ----------
    vt_test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    test_params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    """
    vms = env.get_all_vms()

    while not all([vm.is_alive() for vm in vms]):
        logger.info("Wait VMs to up.")
        time.sleep(5)

    i = 0
    while any([vm.is_alive() for vm in vms]):
        if i % 100 == 0:
            logger.info("Found active VM continue sleep %s.", i)
        time.sleep(5)
        i = i + 1
