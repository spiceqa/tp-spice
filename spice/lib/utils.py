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
#
# Copyright: Red Hat Inc. 2016
# Author: Andrei Stepanov <astepano@redhat.com>
#

"""Common spice test utility functions.

.. todo:: Rework migration, add migration as a option of the session, but
that can wait.

    xwininfo

"""
import logging
import os
import re
import time
import pipes
import socket

from distutils import util  # virtualenv problem pylint: disable=E0611
from virttest import qemu_vm
from virttest import asset
from virttest import utils_net
from avocado.core import exceptions

logger = logging.getLogger(__name__)

SSL_TYPE_IMPLICIT = "implicit_hs"
"""SSL type - implicit host name."""
SSL_TYPE_EXPLICIT = "explicit_hs"
"""SSL type - explicit host name."""
SSL_TYPE_IMPLICIT_INVALID = "invalid_implicit_hs"
"""SSL type - invalid implicit host name."""
SSL_TYPE_EXPLICIT_INVALID = "invalid_explicit_hs"
"""SSL type - invalid explicit host name."""
PTRN_QEMU_SSL_ACCEPT_FAILED = "SSL_accept failed"
"""Pattern for qemu log - failed to accept SSL."""
DEPS_DIR = "deps"
"""Dir with useful files."""

VV_DISTR_PATH = r'C:\virt-viewer.msi'
USBCLERK_DISTR_PATH = r'C:\usbclerk.msi'
"""Path to virt-viewer distribution."""
# ..todo:: add to configs: host_path. client_path + rename to more obvious.
DISPLAY = "qxl-0"


# http://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
# ..todo:: rewrite

url_regex = re.compile(
    r'^(?:http|ftp)s?://'                   # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
    r'localhost|'                           # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'                            # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class Cmd(list):
    def __init__(self, *args):
        super(Cmd, self).__init__(map(pipes.quote, args))

    def __str__(self):
        return " ".join(self)

    def append(self, arg):
        return super(Cmd, self).append(pipes.quote(arg))

    def append_raw(self, arg):
        return super(Cmd, self).append(arg)


def combine(*args):
    return " ".join(map(str, args))


def vm_is_win(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_type") == "windows":
        return True
    return False


def vm_is_linux(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_type") == "linux":
        return True
    return False


def quote(arg):
    """Quote one argument. After quotation shell receives argument that cannot
    be treated in any way. No variables, no back-slashes.

    Example
    -------
        print pipes.quote(r'<\n $0>')
        '<\n $0>'  -- What receives shell.

    Note
    ----
        The string argument must be passed in r"something" raw format.

    """
    return pipes.quote(arg)


def vm_is_rhel7(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_variant") == "rhel7":
        return True
    return False


def vm_is_rhel6(self):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    if self.params.get("os_variant") == "rhel6":
        return True
    return False


def vm_info(self, string, *args, **kwargs):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    logger.info(self.name + " : " + string, *args, **kwargs)


def vm_error(self, string, *args, **kwargs):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    logger.error(self.name + " : " + string, *args, **kwargs)


def info(vmi, string, *args, **kwargs):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    logger.info(vmi.vm_name + " : " + string, *args, **kwargs)


def debug(vmi, string, *args, **kwargs):
    """Extention to qemu.VM(virt_vm.BaseVM) class.
    """
    logger.debug(vmi.vm_name + " : " + string, *args, **kwargs)


def extend_api_vm():
    """Extend qemu.VM(virt_vm.BaseVM) with useful methods.
    """
    qemu_vm.VM.is_linux = vm_is_linux
    qemu_vm.VM.is_win = vm_is_win
    qemu_vm.VM.is_rhel7 = vm_is_rhel7
    qemu_vm.VM.is_rhel6 = vm_is_rhel6
    qemu_vm.VM.info = vm_info
    qemu_vm.VM.error = vm_error


def type_variant(test, vm_name):
    vm = test.vms[vm_name]
    os_type = vm.params.get("os_type")
    os_variant = vm.params.get("os_variant")
    return (os_type, os_variant)


def download_asset(asset_name, ini_dir=None, section=None, ddir=None):
    provider_dirs = asset.get_test_provider_subdirs(backend="spice")[0]
    if ini_dir:
        provider_dirs.insert(0, ini_dir)
    logger.debug("Provider_dirs: %s.", repr(provider_dirs))
    fname = "%s.ini" % asset_name
    for d in os.walk(provider_dirs):
        d = d[0]
        ini_file = os.path.join(d, fname)
        if os.path.isfile(ini_file):
            asset_dir = d
            break
    assert os.path.isfile(ini_file), "Cannot find %s.ini file." % asset_name
    logger.info("Section: %s", section)
    asset_info = asset.get_asset_info(asset_name, ini_dir=asset_dir,
                                      section=section)
    if ddir:
        dst_file = os.path.basename(asset_info['destination'])
        asset_info['destination'] = os.path.join(ddir, dst_file)
    asset.download_file(asset_info)
    stored_at = asset_info['destination']
    logger.info("Asset stored at: %s.", stored_at)
    return stored_at


class SpiceUtilsError(Exception):
    """Exception raised in case the lib API fails."""


class SpiceUtilsUnknownVmType(SpiceUtilsError):
    """Unknow VM type."""

    def __init__(self, vm_name, *args, **kwargs):
        super(SpiceUtilsUnknownVmType, self).__init__(args, kwargs)
        self.vm_name = vm_name

    def __str__(self):
        return "Unkon VM type: %s" % self.vm_name


class SpiceUtilsBadVmType(SpiceUtilsError):
    """Bad VM type."""

    def __init__(self, vm_name, *args, **kwargs):
        super(SpiceUtilsBadVmType, self).__init__(args, kwargs)
        self.vm_name = vm_name

    def __str__(self):
        return "Bad and unexpected VM type: %s." % self.vm_name


# ..todo:: or aexpect.xxx ???
class SpiceUtilsCmdRun(SpiceUtilsError):
    """Fail to run cmd on VM."""

    def __init__(self, vm_name, cmd, output, *args, **kwargs):
        super(SpiceUtilsCmdRun, self).__init__(args, kwargs)
        self.vm_name = vm_name
        self.cmd = cmd
        self.output = output

    def __str__(self):
        return "Command: {0} failed at: {1} with output: {2}".format(
            self.cmd, self.vm_name, self.output)


class SpiceTestFail(exceptions.TestFail):
    """Unknow VM type."""

    def __init__(self, test, *args, **kwargs):
        super(SpiceTestFail, self).__init__(args, kwargs)
        if test.cfg.pause_on_fail or test.cfg.pause_on_end:
            # 1 hour
            seconds = 60 * 60 * 10
            logger.error("Test %s has failed. Do nothing for %s seconds.",
                         test.cfg.id, seconds)
            time.sleep(seconds)


def finish_test(test):
    """Could be located at the end of the tests."""
    if test.cfg.pause_on_end:
        # 1 hour
        seconds = 60 * 60
        logger.info("Test %s is finished. Do nothing for %s seconds.",
                    test.cfg.id, seconds)
        time.sleep(seconds)


def is_yes(string):
    """Wrapper around util.strtobool.

    Parameters
    ----------
    string : str
        String to check.

    Note
    ----
    https://docs.python.org/2/distutils/apiref.html#distutils.util.strtobool
    True values are y, yes, t, true, on and 1; false values are n, no, f,
    false, off and 0. Raises ValueError if val is anything else.
    """
    return util.strtobool(str(string))


def str2res(res):
    """Convert resolution in str for: XXXxYYY to tuple.

    Parameters
    ----------
    res : str
        Resolution.

    Returns
    -------
    tuple
        Resolution.

    """
    width = int(res.split('x')[0])
    # The second split of - is a workaround because the xwinfo sometimes
    # prints out dashes after the resolution for some reason.
    height = int(res.split('x')[1].split('-')[0])
    return (width, height)


def res_gt(res1, res2):
    """Test res2 > res1

    Parameters
    ----------
    res1: tuple
        resolution
    res2: tuple
        resolution

    Returns
    -------
    bool
        res1 > res2

    """
    return res2[0] > res1[0] and res2[1] > res1[1]


def res_eq(res1, res2):
    """Test res1 == res2

    Parameters
    ----------
    res1: tuple
        resolution
    res2: tuple
        resolution

    Returns
    -------
    bool
        res1 == res2

    """
    return res1 == res2


def is_eq(val, tgt, err_limit):
    """Test if val is equal to tgt in allowable limits.

    Parameters
    ----------
    val :
        Value to check.
    tgt :
        Specimen.
    err_limit :
        Acceptable percent change of x2 from x1.

    init: original integer value
    post: integer that must be within an acceptable percent of x1

    """
    if not isinstance(tgt, int):
        tgt = int(tgt)
    if not isinstance(val, int):
        val = int(val)
    if not isinstance(err_limit, int):
        err_limit = int(err_limit)
    sub = tgt * err_limit / 100
    bottom = tgt - sub
    up = tgt + sub
    ret = bottom <= val and val <= up
    logger.info("Stating %d <= %d <= %d is %s.", bottom, val, up, str(ret))
    return ret


def get_host_ip(test):
    """Get IP for host.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    """
    ip_ver = test.kvm_g.listening_addr
    if not ip_ver:
        ip_ver = "ipv4"
    try:
        ip = utils_net.get_host_ip_address(test.cfg, ip_ver)
    except utils_net.NetError:
        ips = utils_net.get_all_ips()
        ip = ips[0]
        logger.info("Take as a host IP: %s", ip)
    if ip_ver == "ipv6":
        ip = "[" + ip + "]"
    return ip


def cacert_path_host(test):
    """Cacert file path on host system.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    Returns
    -------
    str
        Cacert file path on host system.

    """
    path = None
    if is_yes(test.kvm_g.spice_ssl):
        path = "%s/%s" % (test.cfg.spice_x509_prefix,
                          test.cfg.spice_x509_cacert_file)
    logger.info("CA cert file on host: %s", path)
    return path


def get_host_subj(test):
    """Host subject.

    Parameters
    ----------
    test : SpiceTest
        Spice test object.

    """
    subj = None
    if is_yes(test.kvm_g.spice_ssl):
        if test.cfg.ssltype == "invalid_explicit_hs":
            subj = "Invalid Explicit HS"
        else:
            # Has form: /C=CZ/L=BRNO/O=SPICE/CN=.
            subj = test.kvm_g.spice_x509_server_subj
            subj = subj.replace('/', ',')[1:]
            subj += str(get_host_ip(test))
    return subj


def set_ticket(test):
    cfg = test.cfg
    if cfg.ticket_set:
        logger.info("Set guest ticket: set_password spice %s", cfg.ticket_set)
        cmd = "set_password spice %s" % cfg.ticket_set
        test.vm_g.monitor.cmd(cmd)


def URL_parse(url, def_port=None):
    """Parses URL to IP address and port

    Parameters
    ----------
    url : URL string to parse
    def_port : default port value

    :return: (IP address, port)
    """
    parse = url.split('//')[-1]
    if ']:' in parse or '.' in parse and ':' in parse:
        # port is specified in parse
        ip, _, port = parse.rpartition(':')
    else:
        ip, port = parse, def_port
    ip = ip.strip('[]')
    if ip.split('.')[-1].isalpha():
        ip = socket.gethostbyname(ip)
    return ip, port
