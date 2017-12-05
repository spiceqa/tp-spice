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

"""Tests file transfer functionality between client and guest using the spice
vdagent daemon.

"""

import os
import logging
import aexpect

from spice.lib import stest
from spice.lib import utils
from spice.lib import act


logger = logging.getLogger(__name__)


def run(vt_test, test_params, env):
    """Run remote-viewer at client VM.

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
    cfg = test.cfg
    vmi_c = test.vmi_c
    vmi_g = test.vmi_g
    homedir_g = act.home_dir(vmi_g)
    success = False
    act.turn_accessibility(vmi_c)
    act.x_active(vmi_c)
    act.x_active(vmi_g)
    ssn = act.new_ssn(vmi_c)
    act.rv_connect(vmi_c, ssn)
    # Nautilus cannot be docked to side when default resolution
    act.set_resolution(vmi_c, "1280x1024")
    if utils.vm_is_rhel6(test.vm_c):
        # Activate accessibility for rhel6, BZ#1340160 for rhel7
        act.reset_gui(vmi_c)
    act.install_rpm(vmi_c, vmi_c.cfg.dogtail_rpm)
    dst_script = act.chk_deps(vmi_c, cfg.helper_c)
    if cfg.copy_img:
        act.imggen(vmi_c, cfg.test_xfer_file, cfg.test_image_size)
    else:
        act.gen_rnd_file(vmi_c, cfg.test_xfer_file, cfg.xfer_kbytes)
    act.run(vmi_c, "nautilus &")
    if cfg.xfer_args:
        cmd = utils.Cmd(dst_script, cfg.xfer_args, cfg.test_xfer_file)
    else:
        cmd = utils.Cmd(dst_script, cfg.test_xfer_file)
    logger.info('Sending command to client: %s', cmd)
    try:
        act.run(vmi_c, cmd)
    except aexpect.exceptions.ShellCmdError:
        logger.info('Cannot paste from buffer.')
        utils.SpiceTestFail(test, "Test failed.")
    md5src = act.md5sum(vmi_c, cfg.test_xfer_file)
    md5dst = act.md5sum(vmi_g, os.path.join(homedir_g, 'Downloads',
                                            cfg.test_xfer_file))
    if md5src == md5dst:
        success = True
    if not success:
        raise utils.SpiceTestFail(test, "Test failed.")
    # test passes
