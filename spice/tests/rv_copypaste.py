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

"""Tests copy & paste functionality between client and guest using the spice
vdagent daemon.

"""


import os
import logging
from avocado.core import exceptions
from spice.lib import rv_ssn
from spice.lib import stest
from spice.lib import utils
from spice.lib import deco
from spice.lib import act
import time
import aexpect
from virttest import utils_misc


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
    act.x_active(test.vmi_c)
    act.x_active(test.vmi_g)
    ssn = test.open_ssn(test.name_c)
    rv_ssn.connect(test, ssn)
    act.clear_cb(test.vmi_g)
    act.clear_cb(test.vmi_c)
    if cfg.vdagent_action:
        act.service_vdagent(test.vmi_g, cfg.vdagent_action)
    if cfg.guest2client:
        src = test.name_g
        dst = test.name_c
    elif cfg.client2guest:
        src = test.name_c
        dst = test.name_g
    success = False
    if cfg.copy_text:
        test.cmds[src].text2cb(cfg.text)
        text = test.cmds[dst].cb2text()
        if cfg.text in text:
            success = True
    elif cfg.copy_text_big:
        test.cmds[src].gen_text2cb(cfg.kbytes)
        test.cmds[src].cb2file(cfg.dump_file)
        md5src = test.cmds[src].md5sum(cfg.dump_file)
        test.cmds[dst].cb2file(cfg.dump_file)
        md5dst = test.cmds[dst].md5sum(cfg.dump_file)
        if md5src == md5dst:
            success = True
    elif cfg.copy_img:
        dst_img = test.cmds[src].chk_deps(cfg.test_image)
        test.cmds[src].img2cb(dst_img)
        test.cmds[src].cb2img(cfg.dump_img)
        test.cmds[dst].cb2img(cfg.dump_img)
        md5src = test.cmds[src].md5sum(cfg.dump_img)
        md5dst = test.cmds[dst].md5sum(cfg.dump_img)
        if md5src == md5dst:
            success = True

    if cfg.negative and success \
        or not cfg.negative and not success:
        raise utils.SpiceTestFail(test, "Test failed.")

    pass
