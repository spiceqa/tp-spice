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

"""
Test keyboard inputs through spice. Send keys through qemu monitor to client.

Requires
--------
    - Deployed PyGTK on guest VM.

Presumes the numlock state at startup is 'OFF'.


"""


import logging
from avocado.core import exceptions
from spice.lib import rv_ssn
from spice.lib import stest
from spice.lib import utils
from spice.lib import act
from virttest import utils_misc


logger = logging.getLogger(__name__)

#
#def test_leds_migration(client_vm, guest_vm, guest_session, params):
#    """
#    Check LEDS after migration.
#    Function sets LEDS (caps, num) to ON and send scancodes of "a" and "1 (num)"
#    and expected to get keycodes of "A" and "1" after migration.
#
#    Parameters
#    ----------
#    client_vm :
#        Vm object.
#    guest_vm :
#        Vm object.
#    guest_session :
#        Ssh session to guest VM.
#    params : virttest.utils_params.Params
#        Dictionary with the test parameters.
#    """
#    # Turn numlock on RHEL6 on before the test begins:
#    grep_ver_cmd = "grep -o 'release [[:digit:]]' /etc/redhat-release"
#    rhel_ver = guest_session.cmd(grep_ver_cmd).strip()
#    logging.info("RHEL version: #{0}#".format(rhel_ver))
#    if rhel_ver == "release 6":
#        client_vm.send_key('num_lock')
#    #Run PyGTK form catching KeyEvents on guest
#    run_test_form(guest_session, params)
#    utils_spice.wait_timeout(3)
#    # Tested keys before migration
#    test_keys = ['a', 'kp_1', 'caps_lock', 'num_lock', 'a', 'kp_1']
#    logging.info("Sending leds keys to client machine before migration")
#    for key in test_keys:
#        client_vm.send_key(key)
#        utils_spice.wait_timeout(0.3)
#    guest_vm.migrate()
#    utils_spice.wait_timeout(8)
#    #Tested keys after migration
#    test_keys = ['a', 'kp_1', 'caps_lock', 'num_lock']
#    logging.info("Sending leds keys to client machine after migration")
#    for key in test_keys:
#        client_vm.send_key(key)
#        utils_spice.wait_timeout(0.3)
#    utils_spice.wait_timeout(30)

#expected_keysyms = [97, 65457, 65509, 65407, 65, 65436, 65, 65436,
#                            65509, 65407]
#


def test_seq(test, send_keys, expected_keysyms):
    ssn = act.klogger_start(test.vmi_g)
    for i in send_keys:
        test.vm_c.send_key(i)
    logged_keys = act.klogger_stop(test.vmi_g, ssn)
    keysyms = map(lambda (ignore, keysym): keysym, logged_keys)
    assert keysyms == expected_keysyms
    ssn.close


def run(vt_test, test_params, env):
    """Test for testing keyboard inputs through spice.

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
    #test.cmd_g.install_rpm(cfg.xev)
    act.x_active(test.vmi_c)
    act.x_active(test.vmi_g)
    ssn = test.open_ssn(test.name_c)
    rv_ssn.connect(test, ssn)

    if cfg.ttype == 'type_and_func_keys':
        """Test typewriter and functional keys."""
        keycodes = range(1, 69)
        # Skip Ctrl, RSH, LSH, PtScr, Alt, CpsLk
        skip = [29, 42, 54, 55, 56, 58]
        send_keys = filter(lambda k: k not in skip, keycodes)
        send_keys = map(lambda k: str(hex(k)), send_keys)
        expected_keysyms = [65307, 49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 45,
                            61, 65288, 65289, 113, 119, 101, 114, 116, 121,
                            117, 105, 111, 112, 91, 93, 65293, 97, 115, 100,
                            102, 103, 104, 106, 107, 108, 59, 39, 96, 92, 122,
                            120, 99, 118, 98, 110, 109, 44, 46, 47, 32, 65470,
                            65471, 65472, 65473, 65474, 65475, 65476, 65477,
                            65478, 65479]
        test_seq(test, send_keys, expected_keysyms)

    if cfg.ttype == 'leds_and_esc_keys':
        escaped = ['insert', 'delete', 'home', 'end', 'pgup', 'pgdn', 'up',
                   'down', 'right', 'left']
        expected_keysyms = [65379, 65535, 65360, 65367,
                            65365, 65366, 65362, 65364, 65363, 65361]
        test_seq(test, escaped, expected_keysyms)

        shortcuts = ['a', 'shift-a', 'shift_r-a', 'ctrl-a', 'ctrl-c', 'ctrl-v',
                     'alt-x']
        expected_keysyms = [97, 65505, 65, 65506, 65, 65507, 97, 65507, 99,
                            65507, 118, 65513, 120]
        test_seq(test, shortcuts, expected_keysyms)

        leds = ['a', 'caps_lock', 'a', 'caps_lock', 'num_lock', 'kp_1',
                'num_lock', 'kp_1']
        expected_keysyms = [97, 65509, 65, 65509, 65407, 65457, 65407, 65436]
        test_seq(test, leds, expected_keysyms)
    if cfg.ttype == 'nonus_layout':
        cmd = "setxkbmap cz"
        test.ssn_g.cmd(cmd)
        keys = ['7', '8', '9', '0', 'alt_r-x', 'alt_r-c', 'alt_r-v']
        expected_keysyms = [253, 225, 237, 233, 65027, 35, 65027, 38, 65027,
                            64]
        test_seq(test, keys, expected_keysyms)
        cmd = "setxkbmap de"
        test.ssn_g.cmd(cmd)
        keys = ['minus', '0x1a', 'alt_r-q', 'alt_r-m']
        expected_keysyms = [223, 252, 65027, 64, 65027, 181]
        test_seq(test, keys, expected_keysyms)
        cmd = "setxkbmap us"
        test.ssn_g.cmd(cmd)
    if cfg.ttype == "leds_migration":
        if test.vm_c.is_rhel6():
            test.vm_c.send_key('num_lock')
        keys1 = ['a', 'kp_1', 'caps_lock', 'num_lock', 'a', 'kp_1']
        keys2 = ['a', 'kp_1', 'caps_lock', 'num_lock']
        expected_keysyms = ['97', '65457', '65509', '65407', '65', '65436',
                            '65', '65436', '65509', '65407']
        ssn = act.klogger_start(test.vmi_g)
        for i in keys1:
            test.vm_c.send_key(i)
        test.vm_g.migrate()
        for i in keys2:
            test.vm_c.send_key(i)
        logged_keys = act.klogger_stop(test.vmi_g, ssn)
        ssn.close
        keysyms = map(lambda (ignore, keysym): keysym, logged_keys)
        assert keysyms == expected_keysyms

""" Useful links

https://code.google.com/archive/p/key-mon/
http://www.shallowsky.com/software/crikey/pykey-0.1
https://www.berrange.com/tags/key-codes/
ftp://ftp.suse.com/pub/people/sbrabec/keyboards/
http://python-evdev.readthedocs.io/en/latest/index.html
http://python-xlib.sourceforge.net/doc/html/python-xlib_16.html#SEC15
https://en.wikipedia.org/wiki/Evdev
http://python-evdev.readthedocs.io/en/latest/apidoc.html#module-evdev.ecodes
https://www.vmware.com/support/ws4/doc/devices_linux_kb_ws.html
http://www.madore.org/~david/linux/linux-old.html
http://www.comptechdoc.org/os/linux/howlinuxworks/linux_hlkeycodes.html
https://wiki.ubuntu.com/Hotkeys/Architecture
http://www.tcl.tk/man/tcl8.4/TkCmd/keysyms.htm

"""
