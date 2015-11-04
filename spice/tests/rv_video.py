"""
rv_video.py - Starts video player
Video is played in a loop, usually kill_app
test should be called later to close totem.

Requires: binaries Xorg, totem, gnome-session
          Test starts video player

"""
import logging
import os
from virttest import utils_misc, remote


#TODO: whole file needs rewrite


def launch_totem(guest_session, params):
    """
    Launch Totem player

    @param guest_vm - vm object
    """

    totem_version = guest_session.cmd_output('totem --version')
    logging.info("Totem version", totem_version)

    # repeat parameters for totem
    logging.info("Set up video repeat to '%s' to the Totem.",
                 params.get("repeat_video"))

    #release check. From RHEL7 dconf is used
    #there is different of settings repeat
    release = guest_session.cmd_output("cat /etc/redhat-release")
    if "release 7.0" in release:
        repeat_cmd = "dconf write /org/gnome/Totem/repeat true"
        norepeat_cmd = "dconf write /org/gnome/Totem/repeat false"
        #extra parameters
        totem_params = ""
    else:
        repeat_cmd = "gconftool-2 --set /apps/totem/repeat -t bool true"
        norepeat_cmd = "gconftool-2 --set /apps/totem/repeat -t bool false"
        totem_params = "--display=:0.0 --play"

    if params.get("repeat_video", "no") == "yes":
        cmd = repeat_cmd
    else:
        cmd = norepeat_cmd

    guest_session.cmd(cmd)

    cmd = "export DISPLAY=:0.0"
    guest_session.cmd(cmd)

    #fullscreen parameters for totem
    if params.get("fullscreen", "no") == "yes":
        fullscreen = " --fullscreen "
    else:
        fullscreen = ""

    cmd = "nohup totem %s %s %s &> /dev/null &" \
            % (fullscreen, params.get("destination_video_file_path"),
               totem_params)
    guest_session.cmd(cmd)


def deploy_video_file(test, vm_obj, params):
    """
    Deploy video file into destination on vm

    @param vm_obj - vm object
    @param params: Dictionary with the test parameters.
    """
    source_video_file = params.get("source_video_file")
    video_dir = os.path.join("deps", source_video_file)
    video_path = utils_misc.get_path(test.virtdir, video_dir)

    remote.copy_files_to(vm_obj.get_address(), 'scp',
                         params.get("username"),
                         params.get("password"),
                         params.get("shell_port"),
                         video_path,
                         params.get("destination_video_file_path"))


def run_rv_video(test, params, env):
    """
    Test of video through spice

    @param test: KVM test object.
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """

    guest_vm = env.get_vm(params["guest_vm"])
    guest_vm.verify_alive()
    guest_session = guest_vm.wait_for_login(
        timeout=int(params.get("login_timeout", 360)))
    deploy_video_file(test, guest_vm, params)

    launch_totem(guest_session, params)
    guest_session.close()
