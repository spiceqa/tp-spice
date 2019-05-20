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

"""Define zope interfaces that help to indentify a OS. Based on a current
interfaces set we can find most suitable function.

Marker of interface must exactly correspond to a value of an appropritate key
in cartesian config.

Example
-------

    if cartesian_config["os_type"] == "linux":
        print "OS provide ILinux interface."

Example
-------
    In python interpreter:

    # execfile("ios.py")
    # registry.lookupAll([],IOSInfo)
    # registry.lookup([],IVersionMajor,'7')

"""

from zope import interface  # pylint: disable=F0401
from spice.lib import reg


registry = reg.registry


def add_os_info(marker):
    """Decorator for interface classes. Simplify adding OS type to registry.

    Parameters
    ----------
    marker : str
        Marker that is associated with an interface.  In terms of zope
        interfaces it is a "name of the adapter".

    Returns
    -------
    Interface
        Unmodified interface class.

    """
    def class_builder(cls):
        for c in cls.__bases__:
            registry.register([], c, marker, cls)
        return cls
    return class_builder


# pylint: disable=E0239
class IOSInfo(interface.Interface):
    """Base class for all OS variety interfaces.
    """


class IOvirt(IOSInfo):
    """OS type.
    """


@add_os_info(marker='4')
class IOvirt4(IOvirt):
    pass


class IOSystem(IOSInfo):
    """OS type.
    """


@add_os_info(marker='windows')
class IWindows(IOSystem):
    pass


@add_os_info(marker='linux')
class ILinux(IOSystem):
    pass


# Linux distro.
@add_os_info(marker='rhel')
class IRhel(ILinux):
    pass


@add_os_info(marker='fedora')
class IFedora(ILinux):
    pass


# Windows name.
# https://en.wikipedia.org/wiki/List_of_Microsoft_Windows_versions
@add_os_info(marker='Windows10')
class IWindows10(IWindows):
    pass


@add_os_info(marker='Windows8')
class IWindows8(IWindows):
    pass


@add_os_info(marker='Windows7')
class IWindows7(IWindows):
    pass


@add_os_info(marker='WindowsVista')
class IWindowsVista(IWindows):
    pass


@add_os_info(marker='WindowsXP')
class IWindowsXP(IWindows):
    pass


# Architecture.
class IArch(IOSInfo):
    pass


@add_os_info(marker='32bits')
class IArch32(IArch):
    pass


@add_os_info(marker='64bits')
class IArch64(IArch):
    pass


# Major version.
class IVersionMajor(IOSInfo):
    pass


@add_os_info(marker='6')
class IVersionMajor6(IVersionMajor):
    pass


@add_os_info(marker='7')
class IVersionMajor7(IVersionMajor):
    pass


@add_os_info(marker='8')
class IVersionMajor8(IVersionMajor):
    pass


@add_os_info(marker='25')
class IVersionMajor25(IVersionMajor):
    pass


# Minor version.
class IVersionMinor(IOSInfo):
    pass


@add_os_info(marker='1')
class IVersionMinor1(IVersionMinor):
    pass


@add_os_info(marker='2')
class IVersionMinor2(IVersionMinor):
    pass


@add_os_info(marker='3')
class IVersionMinor3(IVersionMinor):
    pass


@add_os_info(marker='4')
class IVersionMinor4(IVersionMinor):
    pass


@add_os_info(marker='5')
class IVersionMinor5(IVersionMinor):
    pass


@add_os_info(marker='6')
class IVersionMinor6(IVersionMinor):
    pass


@add_os_info(marker='7')
class IVersionMinor7(IVersionMinor):
    pass


@add_os_info(marker='8')
class IVersionMinor8(IVersionMinor):
    pass


@add_os_info(marker='9')
class IVersionMinor9(IVersionMinor):
    pass


@add_os_info(marker='10')
class IVersionMinor10(IVersionMinor):
    pass


@add_os_info(marker='devel')
class IVersionMinorDevel(IVersionMinor):
    pass
