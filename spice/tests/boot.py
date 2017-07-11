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

import logging

from autotest.client.shared import error
from spice.lib import deco

logger = logging.getLogger(__name__)


@deco.retry(8, exceptions=(AssertionError,))
def chk_all_alive(vms):
    assert all([vm.is_alive() for vm in vms])


@deco.retry(8, exceptions=(AssertionError,))
def down_all_vms(vms):
    alive_vms = [vm for vm in vms if vm.is_alive()]
    for vm in alive_vms:
        logger.info("Powerdown %s vm.", vm.name)
        vm.monitor.system_powerdown()
    assert not alive_vms


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
    chk_all_alive(vms)
    down_all_vms(vms)
