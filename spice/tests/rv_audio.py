"""
This module Plays audio playback / record on guest and detect any pauses in the
audio stream.
"""

import logging
from avocado.core import exceptions
from virttest import utils_misc
from spice.lib import rv_session
from spice.lib import conf

def verify_recording(recording, params):
    """
    Tests whether something was actually recorded. Threshold is a number of
    bytes which have to be zeros, in order to record an unacceptable pause.
    11000 bytes is ~ 0.06236s (at 44100 Hz sampling, 16 bit depth and stereo)

    Parameters
    ----------
    recording : str
        Path to recorded wav file.
    params : virttest.utils_params.Params
        Dictionary with the test parameters.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    rec = open(recording).read()
    disable_audio = params.get("disable_audio", "no")
    threshold = int(params.get("rv_audio_threshold", "25000"))
    config_test = params.get("config_test", None)
    if len(rec) - rec.count('\0') < 50:
        logging.info("Recording is empty")
        if disable_audio != "yes":
            return False
        else:
            return True
    pauses = []
    pause = False
    try:
        for index, value in enumerate(rec):
            if value == '\0':
                if not pause:
                    pauses.append([index])
                    pause = True
            else:
                if pause:
                    pauses[-1].append(index - 1)
                    pause = False
                    if (pauses[-1][1] - pauses[-1][0]) < threshold:
                        pauses.pop()
        if len(pauses):
            logging.error("%d pauses detected:", len(pauses))
            for i in pauses:
                start = float(i[0]) / (2 * 2 * 44100)
                duration = float(i[1] - i[0]) / (2 * 2 * 44100)
                logging.info("start: %10fs, duration: %10fs", start, duration)
            # Two small hiccups are allowed when migrating
            if len(pauses) < 3 and config_test == "migration":
                return True
            else:
                return False
        else:
            logging.info("No pauses detected")
    except IndexError:
        # Too long pause, overflow in index
        return False
    return True

def run(test, params, env):
    """
    Playback of audio stream tests for remote-viewer.

    Parameters
    ----------
    test : avocado.core.plugins.vt.VirtTest
        QEMU test object.
    params : virttest.utils_params.Params
        Dictionary with the test parameters.
    env : virttest.utils_env.Env
        Dictionary with test environment.

    Raises
    ------
    TestFail
        Test fails for expected behaviour.

    """
    logging.info("Start test %s", test.name)
    session = rv_session.RvSession(params, env)
    session.clear_interface_all()
    guest_vm = session.guest_vm
    client_vm = session.client_vm
    timeout = int(params.get("login_timeout", 360))
    guest_session = guest_vm.wait_for_login(timeout=timeout,
                                            username=conf.USERNAME,
                                            password=conf.PASSWORD)
    client_session = client_vm.wait_for_login(timeout=timeout,
                                              username=conf.USERNAME,
                                              password=conf.PASSWORD)
    try:
        session.is_connected()
    except:
        raise exceptions.TestFail("Failed to establish connection")
    audio_src = params.get("audio_src")
    audio_tgt = params.get("audio_tgt")
    audio_rec = params.get("audio_rec")
    audio_time = params.get("audio_time", "200")
    config_test = params.get("config_test", "no")
    rv_record = params.get("rv_record")
    if guest_session.cmd_status("ls %s" % audio_tgt):
        logging.info("Copying %s to guest.", audio_src)
        guest_vm.copy_files_to(audio_src, audio_tgt)
    if client_session.cmd_status("ls %s" % audio_tgt):
        client_vm.copy_files_to(audio_src, audio_tgt)
    if rv_record == "yes":
        logging.info("rv_record set; Testing recording")
        player = client_vm.wait_for_login(timeout=timeout)
        recorder_session = guest_vm.wait_for_login(timeout=timeout)
        recorder_session_vm = guest_vm
    else:
        logging.info("rv_record not set; Testing playback")
        player = guest_vm.wait_for_login(timeout=timeout)
        recorder_session = client_vm.wait_for_login(timeout=timeout)
        recorder_session_vm = client_vm
    cmd = "aplay %s &> /dev/null &" % audio_tgt
    player.cmd(cmd, timeout=30)
    if config_test == "migration":
        bguest = utils_misc.InterruptedThread(guest_vm.migrate, kwargs={})
        bguest.start()
    cmd = "arecord -d %s -f cd -D hw:0,1 %s" % (audio_time, audio_rec)
    recorder_session.cmd(cmd, timeout=500)
    if config_test == "migration":
        bguest.join()
    recorder_session_vm.copy_files_from(audio_rec, conf.AUDIO_REC_FILE)
    if not verify_recording(conf.AUDIO_REC_FILE, params):
        raise exceptions.TestFail("Test failed")
