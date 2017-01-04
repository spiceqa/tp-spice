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

"""rv_video.py - Starts video player. Video is played in a loop, usually
kill_app test should be called later to close totem.

TEST IS UNFINISHED. AND IS USELESS NOW.

Test env
--------

    GuestOS - is Linux.

Requirements for GuestOS
------------------------

    - totem - is simple movie player for the GNOME desktop.
    - gnome-session.
    - png2theora -o 1.ogv -v 10 -f '1' -F 1 '%d.png'

"""

import logging
import os
from virttest import utils_misc
from distutils import util
from autotest.client.shared import error


def launch_totem(session):
    """Launch Totem player and play video file.

    Parameters
    ----------
    session : RvSession
        remote-viewer session
    """
    totem_version = session.guest_session.cmd_output('totem --version')
    logging.info("Totem version %s", totem_version)
    # Repeat parameters for totem.
    totem_params = ""
    if session.guest_vm.is_rhel7():
        repeat_cmd = "dconf write /org/gnome/Totem/repeat true"
        norepeat_cmd = "dconf write /org/gnome/Totem/repeat false"
    elif session.guest_vm.is_linux():
        repeat_cmd = "gconftool-2 --set /apps/totem/repeat -t bool true"
        norepeat_cmd = "gconftool-2 --set /apps/totem/repeat -t bool false"
        totem_params += "--display=:0.0 --play"
    if util.strtobool(session.cfg.repeat_video):
        cmd = repeat_cmd
    else:
        cmd = norepeat_cmd
    session.guest_session.cmd(cmd, timeout=120)
    if util.strtobool(session.cfg.fullscreen):
        totem_params += " --fullscreen "
    dst = session.cfg.destination_video_file_path
    cmd = "nohup totem %s %s &> /dev/null &" % (dst, totem_params)
    session.guest_session.cmd(cmd)


# pylint: disable=E0602
def deploy_video_file(test, vm_obj, params):
    """Deploy video file into destination on vm.

    Parameters
    ----------
    vm_obj : type
        - vm object
    param :
        Dictionary with the test parameters.
    """
    video_dir = os.path.join("deps", session.cfg.source_video_file)
    video_path = utils_misc.get_path(test.virtdir, video_dir)
    session.guest_vm.copy_files_to(video_path, session.cfg.destination_video_file_path)


def run_rv_video(test, params, env):
    """
    Test of video through spice

    @param test: KVM test object.
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """

    session = RvSession(params, env)
    session.clear_interface_all()

    guest_vm = session.guest_vm
    guest_session = guest_vm.wait_for_login(
        timeout=int(params.get("login_timeout", 360)),
        username="root", password="123456")
    guest_root_session = guest_vm.wait_for_login(
        timeout=int(params.get("login_timeout", 360)),
        username="root", password="123456")

    client_vm = session.client_vm

    client_session = client_vm.wait_for_login(
        timeout=int(params.get("login_timeout", 360)),
        username="root", password="123456")
    # Verify remote-viewer is running
    try:
        session.is_connected()
    except:
        raise error.TestFail("Failed to establish connection")

    deploy_video_file(test, guest_vm, params)

    launch_totem(guest_session)
    guest_session.close()
