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
# Copyright: Red Hat Inc. 2017
# Author: Radek Duda <rduda@redhat.com>
#

"""Tests file transfer functionality between client and guest using the spice
vdagent daemon.

Funcional only for rhel7 guest now.
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
    if utils.vm_is_rhel6(test.vm_c):
        # Activate accessibility for rhel6, BZ#1340160 for rhel7
        act.reset_gui(vmi_c)
    act.x_active(vmi_c)
    act.x_active(vmi_g)
    ssn = act.new_ssn(vmi_c)
    act.rv_connect(vmi_c, ssn)
    # Nautilus cannot be docked to side when default resolution
    act.set_resolution(vmi_c, "1280x1024")
    act.install_rpm(vmi_c, vmi_c.cfg.dogtail_rpm)
    dst_script = act.chk_deps(vmi_c, cfg.helper_c)
    if cfg.locked:
        # enable screen lock
        cmd = utils.Cmd('rm', '-I', '/etc/dconf/db/local.d/screensaver')
        act.run(vmi_g, cmd, admin=True)
        cmd = utils.Cmd('dconf', 'update')
        act.run(vmi_g, cmd, admin=True)
        cmd = utils.Cmd('loginctl', 'lock-sessions')
        act.run(vmi_g, cmd, admin=True)
        logging.info('Locking gnome session on guest')
    if 'generate' in cfg.test_xfer_file:
        if cfg.copy_img:
            test_xfer_file = 'test.png'
            act.imggen(vmi_c, test_xfer_file, cfg.test_image_size)
        else:
            test_xfer_file = 'test.txt'
            act.gen_rnd_file(vmi_c, test_xfer_file, cfg.xfer_kbytes)
    elif 'http' in cfg.test_xfer_file:
        cmd = utils.Cmd('wget', cfg.test_xfer_file)
        act.run(vmi_c, cmd)
        test_xfer_file = os.path.basename(cfg.test_xfer_file)
        logger.info('Downloading %s', test_xfer_file)
    act.run(vmi_c, "nautilus &")
    if cfg.xfer_args:
        cmd = utils.Cmd(dst_script, cfg.xfer_args, test_xfer_file)
    else:
        cmd = utils.Cmd(dst_script, test_xfer_file)
    logger.info('Sending command to client: %s', cmd)
    try:
        act.run(vmi_c, cmd)
    except aexpect.exceptions.ShellCmdError:
        logger.info('Cannot transfer a file.')
        utils.SpiceTestFail(test, "Test failed.")
    md5src = act.md5sum(vmi_c, test_xfer_file)
    try:
        md5dst = act.md5sum(vmi_g, os.path.join(homedir_g, 'Downloads',
                                                test_xfer_file))
    except aexpect.exceptions.ShellCmdError:
        logger.info('File is not transferred.')
        md5dst = None
    if md5src == md5dst:
        logger.info('%s transferred to guest VM', test_xfer_file)
        cmd1 = utils.Cmd('lsof')
        cmd2 = utils.Cmd('grep', '-q', '-s', test_xfer_file)
        cmd = utils.combine(cmd1, '|', cmd2)
        status, _ = act.rstatus(vmi_g, cmd)
        if status:
            logger.info('Transferred file %s is closed.', test_xfer_file)
            success = True
    elif cfg.xfer_args == '--negative':
        logger.info('File %s was not transferred.', test_xfer_file)
        success = True
    if not success:
        raise utils.SpiceTestFail(test, "Test failed.")
    # test passes
