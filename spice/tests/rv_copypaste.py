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
import time
import aexpect
import logging

from avocado.core import exceptions
from virttest import utils_misc

from spice.lib import stest
from spice.lib import utils
from spice.lib import deco
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
    act.x_active(test.vmi_c)
    act.x_active(test.vmi_g)
    ssn = act.new_ssn(test.vmi_c)
    act.rv_connect(test.vmi_c, ssn)
    act.clear_cb(test.vmi_g)
    act.clear_cb(test.vmi_c)
    if cfg.vdagent_action:
        act.service_vdagent(test.vmi_g, cfg.vdagent_action)
    if cfg.guest2client:
        src = test.vmi_g
        dst = test.vmi_c
    elif cfg.client2guest:
        src = test.vmi_c
        dst = test.vmi_g
    success = False
    if cfg.copy_text:
        act.text2cb(src, cfg.text)
        text = act.cb2text(dst)
        if cfg.text in text:
            success = True
    elif cfg.copy_text_big:
        act.gen_text2cb(src, cfg.kbytes)
        act.cb2file(src, cfg.dump_file)
        md5src = act.md5sum(src, cfg.dump_file)
        act.cb2file(dst, cfg.dump_file)
        md5dst = act.md5sum(dst, cfg.dump_file)
        if md5src == md5dst:
            success = True
    elif cfg.copy_img:
        dst_img = os.path.join(act.dst_dir(src), cfg.test_image)
        act.imggen(src, dst_img, cfg.test_image_size)
        act.img2cb(src, dst_img)
        act.cb2img(src, cfg.dump_img)
        act.cb2img(dst, cfg.dump_img)
        md5src = act.md5sum(src, cfg.dump_img)
        md5dst = act.md5sum(dst, cfg.dump_img)
        if md5src == md5dst:
            success = True

    if cfg.negative and success \
        or not cfg.negative and not success:
        raise utils.SpiceTestFail(test, "Test failed.")

    pass
